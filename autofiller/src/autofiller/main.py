"""Main orchestration and public API for contact form autofilling."""

import json
import os
import sys

from dotenv import load_dotenv

# Load .env file if it exists (silently fails if not found)
load_dotenv()
from pathlib import Path
from typing import Dict

from playwright.sync_api import Page, sync_playwright

from autofiller.config import Config
from autofiller.field_config import get_field_config
from autofiller.db import DB
from autofiller.form_detection import extract_form_html, find_best_contact_form
from autofiller.heuristics import find_and_fill_first, get_heuristic_selectors
from autofiller.llm_selector import infer_selectors_with_llm


def _build_llm_config() -> dict | None:
    """Build LLM config dict if API key is set."""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return None
    config = {
        "litellm_prefix": Config.LLM_PROVIDER_PREFIX.strip(),
        "model": Config.LLM_MODEL,
        "api_key": api_key,
    }
    # Override base URL when using local/self-hosted LLM (e.g. Ollama)
    if Config.LLM_BASE_URL:
        config["base_url"] = Config.LLM_BASE_URL
    return config


def _get_llm_selectors(
    page: Page,
    llm_config: dict | None,
    logical_field_values: Dict[str, str],
) -> Dict[str, str | None]:
    """Get LLM-inferred selectors for form fields. Returns empty dict if LLM not configured or form not found."""
    llm_selectors: Dict[str, str | None] = {}
    if not llm_config:
        return llm_selectors

    form_element = find_best_contact_form(page)
    if not form_element:
        print("Warning: No contact form detected, using heuristics only")
        return llm_selectors

    form_html = extract_form_html(form_element)
    if not form_html:
        print("Warning: Could not extract form HTML, skipping LLM inference")
        return llm_selectors

    fields_to_map = list(logical_field_values.keys())
    return infer_selectors_with_llm(form_html, fields_to_map, llm_config)


def _expand_name_fields(
    page: Page,
    logical_field_values: Dict[str, str],
    heuristic_selectors: dict,
) -> tuple[bool, bool]:
    """
    If form has first_name/last_name but we only have 'name', split it.
    Mutates logical_field_values. Returns (has_first_name, has_last_name).
    """
    has_first_name = False
    has_last_name = False

    if "name" not in logical_field_values or ("first_name" in logical_field_values and "last_name" in logical_field_values):
        return has_first_name, has_last_name

    if "first_name" in heuristic_selectors:
        for selector in heuristic_selectors["first_name"]:
            if page.query_selector(selector):
                has_first_name = True
                break
    if "last_name" in heuristic_selectors:
        for selector in heuristic_selectors["last_name"]:
            if page.query_selector(selector):
                has_last_name = True
                break

    if not (has_first_name or has_last_name):
        return has_first_name, has_last_name

    full_name = logical_field_values.get("name", "")
    name_parts = full_name.strip().split(None, 1)
    if len(name_parts) >= 2:
        if "first_name" not in logical_field_values:
            logical_field_values["first_name"] = name_parts[0]
        if "last_name" not in logical_field_values:
            logical_field_values["last_name"] = name_parts[1]
    elif len(name_parts) == 1:
        if "first_name" not in logical_field_values:
            logical_field_values["first_name"] = name_parts[0]
        if "last_name" not in logical_field_values:
            logical_field_values["last_name"] = ""

    return has_first_name, has_last_name


def _fill_form_fields(
    page: Page,
    logical_field_values: Dict[str, str],
    llm_selectors: Dict[str, str | None],
    heuristic_selectors: dict,
    has_first_name: bool,
    has_last_name: bool,
) -> str | None:
    """Fill all form fields. Returns the message field selector if filled, for focusing."""
    used_message_selector: str | None = None

    # Skip 'name' when we're filling first_name/last_name (from heuristics or LLM)
    has_first_or_last = has_first_name or has_last_name
    if not has_first_or_last:
        has_first_or_last = bool(
            llm_selectors.get("first_name") or llm_selectors.get("last_name")
        )

    for field_name, value in logical_field_values.items():
        filled = False
        if field_name == "name" and has_first_or_last:
            continue  # Using first_name/last_name instead; no need to print

        if field_name in llm_selectors and llm_selectors[field_name]:
            llm_selector = llm_selectors[field_name]
            try:
                element = page.query_selector(llm_selector)
                if element:
                    print(f"[LLM] Filled '{field_name}' using selector: {llm_selector}")
                    page.fill(llm_selector, value)
                    filled = True
                    if field_name == "message":
                        used_message_selector = llm_selector
            except Exception as exc:  # noqa: BLE001
                print(f"Warning: LLM selector '{llm_selector}' failed for '{field_name}': {exc}")
                print(f"Falling back to heuristics for '{field_name}'...")

        if not filled:
            if field_name in heuristic_selectors:
                selector = find_and_fill_first(
                    page, heuristic_selectors[field_name], value, field_name
                )
                if selector and field_name == "message":
                    used_message_selector = selector
            else:
                try:
                    supported_fields = ", ".join(sorted(heuristic_selectors.keys()))
                    print(f"Warning: No heuristics available for field '{field_name}'. Supported fields: {supported_fields}. Add '{field_name}' to get_heuristic_selectors() in heuristics.py to support this field.")
                except Exception as exc:  # noqa: BLE001
                    print(f"Warning: No heuristics available for field '{field_name}'. Error: {exc}")

    return used_message_selector


def _fill_form_on_page(page: Page, url: str, logical_field_values: Dict[str, str]) -> None:
    """Fill the contact form on the current page."""
    print(f"\n{'='*60}")
    print(f"Processing: {url}")
    print(f"{'='*60}")

    llm_config = _build_llm_config()
    llm_selectors = _get_llm_selectors(page, llm_config, logical_field_values)
    heuristic_selectors = get_heuristic_selectors()
    has_first_name, has_last_name = _expand_name_fields(page, logical_field_values, heuristic_selectors)

    used_message_selector = _fill_form_fields(
        page, logical_field_values, llm_selectors, heuristic_selectors, has_first_name, has_last_name
    )

    if used_message_selector:
        try:
            page.focus(used_message_selector)
        except Exception as exc:  # noqa: BLE001
            print(f"Warning: could not focus message field '{used_message_selector}': {exc}")

    print("\nThe contact form has been pre-filled as far as possible.")
    print(
        "In the browser window:\n"
        "  1) Review and edit the message field as needed.\n"
        "  2) Make any manual corrections if a field was missed.\n"
        "  3) Click the form's Submit/Send button yourself."
    )


def _get_save_next_quit_choice() -> str:
    """Show Save/Next/Quit menu; returns 'save', 'next', or 'quit'.

    Uses stdlib only (no questionary) to avoid asyncio conflict with Playwright's
    sync API, which can trigger "asyncio.run() cannot be called from a running
    event loop" when questionary/prompt_toolkit start their own loop.
    """
    while True:
        print("\nAfter reviewing the form:")
        print("  1, s) Save   - record contact and go to next URL")
        print("  2, n) Next   - skip saving and go to next URL")
        print("  3, q) Quit   - exit the script")
        raw = input("Choice (1/2/3 or s/n/q): ").strip().lower()
        if raw in ("1", "s", "save"):
            return "save"
        if raw in ("2", "n", "next"):
            return "next"
        if raw in ("3", "q", "quit"):
            return "quit"
        print("Invalid choice. Enter 1, 2, or 3 (or s, n, q).")


def autofill_contact_form(
    url: str,
    logical_field_values: Dict[str, str],
) -> None:
    """
    Open a browser, navigate to the given URL, and autofill a generic "contact us" form.
    Convenience wrapper around autofill_multiple_contact_forms for a single URL.
    """
    autofill_multiple_contact_forms([url], logical_field_values)


def autofill_multiple_contact_forms(
    urls: list[str],
    logical_field_values: Dict[str, str],
    vertical: str | None = None,
    city: str | None = None,
    state: str | None = None,
    zip_code: str | None = None,
) -> None:
    """
    Fill contact forms on multiple URLs, keeping the browser open between pages.

    Args:
        urls: List of URLs to process
        logical_field_values: Dict of field names to values (same for all forms)
        vertical: Vertical label saved to the database (e.g. 'Bookkeeping')
        city: Contact city saved to the database (optional)
        state: Contact state saved to the database (optional)
        zip_code: Contact postal code saved to the database (optional)
    """
    if not urls:
        print("No URLs provided.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for i, url in enumerate(urls, 1):
            try:
                # Skip if already submitted (in CONTACTS)
                if DB.contact_exists(url):
                    print(f"\n[{i}/{len(urls)}] Skipping {url} - already submitted (found in CONTACTS)")
                    continue

                print(f"\n[{i}/{len(urls)}] Navigating to: {url}")
                page.goto(url, wait_until="load")

                _fill_form_on_page(page, url, logical_field_values)

                choice = _get_save_next_quit_choice()
                if choice == "quit":
                    break
                if choice == "save":
                    DB.insert_contact(url, vertical=vertical, city=city, state=state, zip_code=zip_code)

            except Exception as exc:  # noqa: BLE001
                print(f"Error processing {url}: {exc}")
                if i < len(urls):
                    response = input("Continue to next page? (y/n): ")
                    if response.lower() != "y":
                        break

        browser.close()


def _init_db() -> None:
    """Initialize the shared database via tracker-server/create_db.py."""
    import importlib.util
    script = Config.DB_PATH.parent / "tracker-server" / "create_db.py"
    spec = importlib.util.spec_from_file_location("create_db", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.create_db(Config.DB_PATH)


def main(
    contact_pages_file_path: Path,
    vertical: str | None = None,
    city: str | None = None,
    state: str | None = None,
    zip_code: str | None = None,
) -> None:
    """
    Load URLs from a contact pages JSON file and field values from field_config.json,
    then process all URLs in one browser session.
    """
    _init_db()

    # Load field values from field_config.json
    config = get_field_config()
    field_values: Dict[str, str] = config.get("field_values", {})
    if not field_values:
        print("Warning: No field_values found in field_config.json. Using empty dict.")

    # Load URLs from the contact pages file
    urls: list[str] = []
    try:
        if contact_pages_file_path.exists():
            with open(contact_pages_file_path, "r", encoding="utf-8") as f:
                urls = json.load(f)
        else:
            print(f"Error: {contact_pages_file_path} not found. Add contact_pages.json with a list of URLs.")
            return
    except (json.JSONDecodeError, IOError) as e:  # noqa: BLE001
        print(f"Warning: Could not load {contact_pages_file_path}: {e}")
        return

    if not urls:
        print("No URLs found. Add a JSON array of URLs to process.")
        return

    if vertical:
        print(f"Vertical: {vertical}")
    print(f"Found {len(urls)} URL(s). Processing all in one browser session.")
    autofill_multiple_contact_forms(urls, field_values, vertical=vertical, city=city, state=state, zip_code=zip_code)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Contact Form Autofiller")
    parser.add_argument("params_file", nargs="?", type=Path, help="Path to JSON params file")
    parser.add_argument("--params_file", dest="params_file_flag", type=Path, metavar="FILE", help="Path to JSON params file (flag form)")
    args = parser.parse_args()

    params_path = args.params_file_flag or args.params_file
    if not params_path:
        parser.error("params_file is required (positional or --params_file)")

    try:
        with open(params_path, "r", encoding="utf-8") as f:
            params = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        parser.error(f"Could not load params file '{params_path}': {e}")

    contact_url_file = params.get("contact_url_file")
    if not contact_url_file:
        parser.error("params file must contain 'contact_url_file'")

    main(
        Path(contact_url_file),
        vertical=params.get("vertical") or None,
        city=params.get("city") or None,
        state=params.get("state") or None,
        zip_code=params.get("zip") or None,
    )
