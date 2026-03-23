"""LLM-based selector inference using litellm."""

import json
import os
import re

import litellm


def infer_selectors_with_llm(
    form_html: str, fields: list[str], config: dict
) -> dict[str, str | None]:
    """
    Use LLM to infer CSS selectors for logical form fields from HTML.

    Args:
        form_html: HTML string of the form element
        fields: List of logical field names to map (e.g., ["name", "email", "subject", "message"])
        config: LLM configuration dict with keys: litellm_prefix, model, api_key, base_url (optional)

    Returns:
        Dict mapping logical field names to CSS selectors (or None if not found).
        Returns empty dict on error.
    """
    system_prompt = (
        "You are an assistant that maps logical contact-form fields to CSS selectors. "
        "Return ONLY valid JSON, no extra text or markdown formatting. "
        "The JSON should have keys matching the field names provided, and values should be "
        "CSS selectors (like 'input[name=\"email\"]' or 'textarea#message') or null if no "
        "suitable element is found."
    )

    user_prompt = f"""HTML of a contact form:

```html
{form_html}
```

Logical fields you must map: {fields}

Return a JSON object where keys are the field names and values are CSS selectors
that uniquely locate the best matching input/textarea element for that field.
If you cannot find a selector for a field, use null for that key.

Example format:
{{"name": "input[name='full_name']", "email": "input[type='email']", "subject": null, "message": "textarea[name='message']"}}"""

    try:
        model_name = config["model"]
        api_key = config["api_key"]
        prefix = config["litellm_prefix"].strip()

        # Prepend provider prefix to model if not already present (litellm expects e.g. together_ai/...)
        if not model_name.startswith(f"{prefix}/"):
            model_name = f"{prefix}/{model_name}"

        # litellm looks up API key by provider; set the env var it expects for this prefix
        # See https://docs.litellm.ai/docs/providers
        _API_KEY_ENV_BY_PREFIX: dict[str, str] = {
            "together_ai": "TOGETHER_AI_API_KEY",
            "ollama": "OPENAI_API_KEY",
            "openai": "OPENAI_API_KEY",
        }
        api_key_env = _API_KEY_ENV_BY_PREFIX.get(prefix, "OPENAI_API_KEY")
        os.environ[api_key_env] = api_key

        litellm_params = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "timeout": 30,
        }

        if "base_url" in config:
            litellm_params["api_base"] = config["base_url"]

        print(f"Calling LLM ({model_name}) to infer selectors...")
        response = litellm.completion(**litellm_params)

        # Extract content from response
        content = response.choices[0].message.content.strip()

        # Try to extract JSON from response (might be wrapped in markdown code blocks)
        # First, try to find JSON wrapped in code blocks
        code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content

        # Parse JSON
        result = json.loads(json_str)

        # Validate and normalize result
        if not isinstance(result, dict):
            print("Warning: LLM returned non-dict response, falling back to heuristics")
            return {}

        # Ensure all requested fields are in the result (with None if missing)
        normalized_result: dict[str, str | None] = {}
        for field in fields:
            value = result.get(field)
            if value is None or value == "null":
                normalized_result[field] = None
            elif isinstance(value, str) and value.strip():
                normalized_result[field] = value.strip()
            else:
                normalized_result[field] = None

        return normalized_result

    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse LLM JSON response: {e}")
        print(f"Raw response: {content[:200]}...")
        return {}
    except Exception as e:  # noqa: BLE001
        print(f"Warning: LLM inference failed: {e}")
        print("Falling back to heuristics...")
        return {}
