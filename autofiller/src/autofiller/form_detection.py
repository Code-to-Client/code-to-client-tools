"""Form detection and HTML extraction."""

from playwright.sync_api import ElementHandle, Page


def find_best_contact_form(page: Page) -> ElementHandle | None:
    """
    Find the most likely contact form on the page.

    Uses heuristics:
    - Prefers forms containing a textarea (contact forms usually have message fields)
    - Prefers forms whose text/labels/placeholders contain keywords like "contact", "message", "email"

    Args:
        page: Playwright page object

    Returns:
        ElementHandle of the best matching form, or None if no form found
    """
    try:
        forms = page.query_selector_all("form")
        if not forms:
            print("No forms found on page")
            return None

        # Score each form based on heuristics
        scored_forms: list[tuple[ElementHandle, int]] = []

        for form in forms:
            score = 0

            # Check if form contains a textarea (strong indicator of contact form)
            try:
                textareas = form.query_selector_all("textarea")
                if textareas:
                    score += 10
            except Exception:  # noqa: BLE001
                pass

            # Check form text content for contact-related keywords
            try:
                form_text = form.inner_text().lower()
                keywords = ["contact", "message", "email", "inquiry", "question", "feedback"]
                for keyword in keywords:
                    if keyword in form_text:
                        score += 2
            except Exception:  # noqa: BLE001
                pass

            # Check input placeholders and labels for keywords
            try:
                inputs = form.query_selector_all("input, textarea")
                for input_elem in inputs:
                    try:
                        placeholder = input_elem.get_attribute("placeholder") or ""
                        name = input_elem.get_attribute("name") or ""
                        id_attr = input_elem.get_attribute("id") or ""
                        combined = f"{placeholder} {name} {id_attr}".lower()

                        if any(kw in combined for kw in ["message", "contact", "email", "name"]):
                            score += 1
                    except Exception:  # noqa: BLE001
                        pass
            except Exception:  # noqa: BLE001
                pass

            scored_forms.append((form, score))

        # Sort by score (highest first) and return the best one
        scored_forms.sort(key=lambda x: x[1], reverse=True)

        if scored_forms and scored_forms[0][1] > 0:
            best_form = scored_forms[0][0]
            print(f"Found contact form (score: {scored_forms[0][1]})")
            return best_form
        elif forms:
            # If no form scored, just return the first one
            print("Using first form found (no scoring match)")
            return forms[0]
        else:
            return None

    except Exception as e:  # noqa: BLE001
        print(f"Warning: Error detecting contact form: {e}")
        return None


def extract_form_html(form_element: ElementHandle) -> str:
    """
    Extract HTML string from a form element.

    Args:
        form_element: Playwright ElementHandle of the form

    Returns:
        HTML string of the form (outer HTML)
    """
    try:
        return form_element.evaluate("(element) => element.outerHTML")
    except Exception as e:  # noqa: BLE001
        print(f"Warning: Error extracting form HTML: {e}")
        return ""
