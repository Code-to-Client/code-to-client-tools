# Contact Form Autofiller

A Python tool that navigates to contact form pages, pre-fills the fields with your contact information and outreach message, then waits for you to review and submit manually. Supports LLM-powered field detection (optional) with heuristic fallback.

For full technical and functional requirements, see [Autofiller Requirements.md](Autofiller%20Requirements.md).

## Features

- **Human-in-the-loop**: Pre-fills the form, then waits for you to review and submit manually
- **Save / Next / Quit**: After each form, choose to record the contact and continue, skip saving, or exit
- **Duplicate skipping**: URLs already in the shared database are skipped automatically
- **LLM-powered field detection**: Optional integration with Together.ai, OpenAI, Ollama, or any litellm-compatible provider
- **Heuristic fallback**: Always works, even without LLM configuration
- **Per-batch field values**: Sender identity and message live in the params file, so each batch can use different values

## Installation

```bash
poetry install
poetry run playwright install chromium
```

## Project Structure

```
autofiller/
├── contacts/          # Contact URL files — one JSON array of URLs per batch
├── params/            # Runtime params files — one JSON object per batch
├── src/autofiller/    # Source code
└── .env               # LLM API key (optional)
```

> **Note:** `contacts/` and `params/` are suggestions, not requirements. You can place these files anywhere and organize them however makes sense for your workflow — for example, with subfolders per vertical (`contacts/legal/`, `params/legal/`) or any other structure. The params file just needs to point to the correct path for `contact_url_file`.

## Setup

### One-time configuration

#### 1. Create the shared database

```bash
python3 ../tracker-server/create_db.py
```

This creates `code-to-client-tools/contacts.db` — the shared database used by both the autofiller and the tracker server.

#### 2. (Optional) Configure LLM

Copy `.env.example` to `.env` and add your API key:

```bash
LLM_API_KEY=your_api_key_here
```

See [LLM Configuration](#llm-configuration-optional) for provider setup.

### Per-batch runtime setup

Each outreach batch (a specific vertical + location + URL list) needs its own params file and contact pages file.

#### 3. Prepare a contact pages file

Create a JSON file in `contacts/` listing the contact form URLs for this batch.

Suggested naming: `contacts-<vertical>-<city>.json`
Sample file `contacts-legal-portland.json` content:

```json
[
  "https://example-legal.com/contact",
  "https://another-firm.com/contact-us"
]
```

#### 4. Create a params file

Create a JSON params file in `params/` that points to the contact pages file, describes the batch context saved to the database, and includes your sender identity in `field_values`.

Suggested naming: `params-<vertical>-<city>.json`
Sample params file `params-legal-portland.json`:

```json
{
  "vertical": "Legal",
  "contact_url_file": "contacts/contacts-legal-portland.json",
  "city": "Portland",
  "state": "OR",
  "zip": "97201",
  "field_values": {
    "name": "Your Name",
    "first_name": "Your",
    "last_name": "Name",
    "email": "you@example.com",
    "phone": "555-555-5555",
    "company": "Your Company",
    "subject": "Inquiry",
    "message": [
      "Your outreach message here.",
      "Second paragraph.",
      "Sincerely,",
      "Your Name"
    ]
  }
}
```

`city`, `state`, and `zip` are optional and can be omitted or set to empty strings. All fields within `field_values` are required. The `message` field accepts either a string or an array of strings — array lines are joined with newlines at runtime.

## Task runner (mask) — optional

The project includes a `maskfile.md` with shorthand commands for common tasks. Using [mask](https://github.com/jacobdeichert/mask?tab=readme-ov-file) is optional — see that link for installation instructions. If you prefer not to install it, use the equivalent commands listed below directly.

| mask command | Equivalent command | Description |
|---|---|---|
| `mask db` | `python3 ../tracker-server/create_db.py` | Create the shared contacts database and tables |
| `mask main` | `poetry run python -m autofiller.main params/params-legal-portland.json` | Run the autofiller for a batch |

## Running

```bash
# Positional
poetry run python -m autofiller.main params/params-legal-portland.json

# Named flag
poetry run python -m autofiller.main --params_file params/params-legal-portland.json
```

### Arguments

| Argument | Positional | Flag | Required | Description |
|---------|-----------|------|----------|-------------|
| Params file | 1st | `--params_file FILE` | Yes | Path to JSON file with run parameters |

### Params file fields

| Field | Required | Description |
|-------|----------|-------------|
| `vertical` | Yes | Vertical label saved to the database (e.g. `Legal`) |
| `contact_url_file` | Yes | Path to JSON file of contact form URLs |
| `field_values` | Yes | Object with sender identity and message to pre-fill into forms |
| `city` | No | City saved to the database |
| `state` | No | State saved to the database |
| `zip` | No | Postal code saved to the database |

## What Happens

For each URL in the file (skipping any already in the database):

1. A browser window opens and navigates to the URL
2. The tool detects the contact form and fills in the fields
3. The message field is focused for easy editing
4. Terminal prints instructions to review and submit manually
5. After you submit, the terminal shows the **Save / Next / Quit** menu:
   - **Save** (`1` or `s`) — Insert the URL into the database and move to the next URL
   - **Next** (`2` or `n`) — Skip saving and move to the next URL
   - **Quit** (`3` or `q`) — Close the browser and exit

## Files Reference

### Configuration (set once)

| File | Description |
|------|-------------|
| `src/autofiller/config.py` | LLM provider, model, and path settings |
| `.env` | `LLM_API_KEY` (required only for LLM mode) |

### Runtime params (one per batch)

| File | Description |
|------|-------------|
| `params/*.json` | Batch parameters: vertical, city, state, zip, field values (sender identity + message), and path to the contact pages file |
| `contacts/*.json` | Contact form URL lists (one per vertical/city/campaign) |

## LLM Configuration (Optional)

LLM is **optional**. Without it, the tool uses built-in heuristic CSS selectors. LLM improves accuracy for complex or non-standard forms.

### Enable LLM

Set `LLM_API_KEY` in `.env`. All other LLM settings are in `src/autofiller/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_PROVIDER_PREFIX` | `together_ai` | litellm provider prefix |
| `LLM_MODEL` | `Qwen/Qwen3-235B-A22B-Instruct-2507-tput` | Model name (without provider prefix) |
| `LLM_BASE_URL` | `None` | Override API base URL (e.g. `http://localhost:11434/v1` for Ollama) |

### Supported Providers

| Provider | Prefix | Notes |
|----------|--------|-------|
| Together.ai (default) | `together_ai` | Cloud; set `LLM_API_KEY` |
| OpenAI | `openai` | Cloud; set `LLM_API_KEY` |
| Ollama | `ollama` | Local; set `LLM_BASE_URL = "http://localhost:11434/v1"` |

### Model Recommendations

Use 32B+ parameter models for reliable selector inference. Cost is negligible at this volume.

- **Together.ai**: `Qwen/Qwen3-235B-A22B-Instruct-2507-tput`, `deepseek-ai/DeepSeek-V3`, `meta-llama/Llama-3.3-70B-Instruct-Turbo`
- **Ollama**: `qwen2.5:32b` (minimum), `llama3.3:70b`, `deepseek-r1:32b`
- **OpenAI**: `gpt-4o-mini`, `gpt-4o`

## How Field Detection Works

1. **Form detection**: Scores all `<form>` elements on the page (textarea presence, contact keywords) and selects the highest-scoring form.

2. **LLM inference** (if configured): Sends the form's HTML to the LLM, which returns a JSON mapping of logical field names to CSS selectors.

3. **Heuristic fallback**: For each field, tries built-in CSS selector patterns in order, using the first visible, editable, non-CAPTCHA match.

LLM selectors are tried first per field; if they fail, heuristics take over for that field.

## Database

Contacts are saved to `code-to-client-tools/contacts.db` (shared with the tracker server).

- **On Save**: Inserts the URL with `CONTACT_SOURCE = CONTACT_FORM`, `STATUS = CONTACTED`, and the `VERTICAL`, `CITY`, `STATE`, `ZIP` values from the params file.
- **Duplicate prevention**: URLs already in the database are skipped before opening the browser.
- **Initialize**: Run `python3 ../tracker-server/create_db.py` to create the database and tables.

