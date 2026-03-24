"""Heuristic selector lists and filling logic."""

from playwright.sync_api import Page

from autofiller.field_config import get_selectors


def get_heuristic_selectors() -> dict[str, list[str]]:
    """
    Get heuristic CSS selector lists for common contact form fields.

    Returns:
        Dict mapping logical field names to lists of CSS selectors to try in order
    """
    return get_selectors()


def find_and_fill_first(
    page: Page, selectors: list[str], value: str, label: str
) -> str | None:
    """
    Try a list of CSS selectors in order, fill the first match, and
    return the selector that succeeded (or None if none matched).

    Args:
        page: Playwright page object
        selectors: List of CSS selectors to try in order
        value: Value to fill into the field
        label: Human-readable label for logging

    Returns:
        The selector that succeeded, or None if none matched
    """
    for selector in selectors:
        try:
            element = page.query_selector(selector)
            if element:
                # Skip reCAPTCHA elements (hidden, not meant for user input)
                element_id = element.get_attribute("id") or ""
                element_name = element.get_attribute("name") or ""
                element_class = element.get_attribute("class") or ""
                
                if "g-recaptcha" in element_id or "g-recaptcha" in element_name or "g-recaptcha" in element_class:
                    continue
                
                # Check if element is visible and editable before attempting to fill
                is_visible = element.is_visible()
                is_editable = element.is_editable()
                
                if is_visible and is_editable:
                    print(f"[HEURISTICS] Filled '{label}' using selector: {selector}")
                    page.fill(selector, value)
                    return selector
        except Exception as exc:  # noqa: BLE001
            print(f"Warning: error while trying selector '{selector}' for {label}: {exc}")
    return None
