# Contact Form Autofiller — Requirements

**Version:** MVP (v1)
**Audience:** Developers running the tool locally (no login, single user)

---

### 1. Purpose and Scope

**Goal:** Automate the tedious part of contact form outreach — typing the same information into hundreds of forms — while keeping the developer in control of every submission.

The tool opens a browser, navigates to each contact form URL, pre-fills the fields with your contact information and message, then **pauses and waits** for you to review, edit if needed, and click Submit yourself. After you submit, you tell the tool whether to save the contact to the database and move to the next URL, skip saving, or quit.

**What it does:**
- Reads a list of contact form URLs from a JSON file.
- Opens each URL in a visible Chromium browser window.
- Detects the contact form on the page and fills in the fields.
- Waits for you to review the pre-filled form and submit it manually.
- On your instruction, saves the submitted URL to the shared `contacts.db` database.
- Skips URLs already in the database (no duplicate submissions).

**Out of scope for MVP:**
- Automatic form submission (always human-in-the-loop).
- Scraping contact URLs (URLs are provided manually).
- Email or social media outreach.

---

### 2. Project Structure

```
autofiller/
├── contacts/          # Contact URL files — one JSON array of URLs per batch
├── params/            # Runtime params files — one JSON object per batch
├── src/autofiller/    # Source code
│   └── field_config.py  # Heuristic CSS selectors (hardcoded)
└── .env               # LLM API key (optional)
```

> **Note:** `contacts/` and `params/` are conventions, not requirements. Files can live anywhere — the params file simply references `contact_url_file` by path. Feel free to organize however suits your workflow, for example with subfolders per vertical (`contacts/legal/`, `params/legal/`) or any other structure.

---

### 3. User Flow


```
1. Developer prepares a JSON file of contact form URLs for a batch.
2. Developer runs the script with the JSON file as argument.
3. For each URL (in order):
   a. Skip if already in the database.
   b. Open the URL in the browser.
   c. Detect the contact form on the page.
   d. Pre-fill form fields using LLM inference (if configured) or heuristics.
   e. Focus the message field so it's ready to edit.
   f. Print instructions in the terminal.
   g. Developer reviews the form in the browser, edits if needed, clicks Submit.
   h. Terminal shows the Save / Next / Quit menu.
   i. Developer chooses:
      - Save (s/1): insert the URL into the database → move to next URL.
      - Next (n/2): skip saving → move to next URL.
      - Quit (q/3): close the browser and exit.
4. After all URLs are processed (or Quit is chosen), the browser closes.
```

---

### 4. Command-Line Arguments

The tool accepts a single argument: a path to a JSON params file. It can be provided as a positional argument or a named flag.

| Argument | Positional | Flag | Required | Description |
|---------|-----------|------|----------|-------------|
| Params file | 1st positional | `--params_file FILE` | Yes | Path to the JSON file with run parameters |

**Naming convention:** `params-<vertical>-<location>.json`

**Both of these are equivalent:**

```bash
# Positional
poetry run python -m autofiller.main params/params-legal-portland.json

# Named flag
poetry run python -m autofiller.main --params_file params/params-legal-portland.json
```

#### Params File Format

A JSON object with the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| `vertical` | Yes | Vertical label saved to the database (e.g. `Legal`) |
| `contact_url_file` | Yes | Path to the JSON file containing contact form URLs |
| `field_values` | Yes | Object with sender identity and message to pre-fill into forms |
| `city` | No | City saved to `CONTACT_CITY` in the database |
| `state` | No | State saved to `CONTACT_STATE` in the database |
| `zip` | No | Postal code saved to `CONTACT_POSTAL_CODE` in the database |

**Example:**
```json
{
  "vertical": "Legal",
  "contact_url_file": "contacts/contacts-legal-portland.json",
  "city": "Portland",
  "state": "OR",
  "zip": "97201",
  "field_values": {
    "name": "Jane Smith",
    "first_name": "Jane",
    "last_name": "Smith",
    "company": "Acme, LLC",
    "email": "jane@acme.com",
    "phone": "503-555-0100",
    "subject": "Partnership Inquiry",
    "message": "Hello,\nWe'd love to connect..."
  }
}
```

`city`, `state`, and `zip` are optional and can be omitted or set to empty strings.

#### Contact Pages File Format

A JSON array of contact form URLs, one per entry.

```json
[
  "https://example-legal.com/contact",
  "https://another-firm.com/contact-us",
  "https://thirdco.com/get-in-touch"
]
```

**Naming convention:** `contacts-<vertical>-<location>.json`

- Example: `contacts-portland.json`
- The `contacts/` directory holds all URL lists, organized by vertical and city.

---

### 5. Field Values and Selectors

#### 5.1 `field_values` (in the params file)

Each params file includes a `field_values` object with the sender identity and message to pre-fill into forms. Because `field_values` lives in the params file, you can use different sender identities and messages for different outreach batches.

| Field        | Description                                      |
|-------------|--------------------------------------------------|
| `name`       | Full name (used when form has a single name field) |
| `first_name` | First name (used when form splits name into two fields) |
| `last_name`  | Last name (used when form splits name into two fields) |
| `company`    | Company name                                     |
| `email`      | Your email address                               |
| `phone`      | Your phone number                                |
| `subject`    | Message subject line                             |
| `message`    | The outreach message body                        |

**Name field handling:** If the form has separate `first_name` / `last_name` fields, the tool automatically splits the `name` value and fills them individually. If the form has only a single name field, `name` is used directly.

#### 5.2 `selectors` (in `src/autofiller/field_config.py`)

CSS selector patterns for each field, tried in order. The first matching, visible, and editable element is filled. Edit `field_config.py` directly to add selectors for non-standard form field naming conventions you encounter.

Selector lists exist for: `name`, `first_name`, `last_name`, `email`, `phone`, `subject`, `message`, `company`.

---

### 6. Form Detection

When the tool lands on a page, it scores all `<form>` elements and picks the one most likely to be the contact form. Scoring is heuristic:

- **+10 points** if the form contains a `<textarea>` (strong signal of a message/contact form).
- **+2 points** for each contact-related keyword found in the form's text content (e.g. "contact", "message", "send").
- **+1 point** for each field whose `name`, `id`, or `placeholder` matches a contact-related keyword.

The highest-scoring form is used. If no form is found, the tool prints a warning and falls back to heuristic selectors applied to the full page.

---

### 7. Field Detection: Two Modes

The tool uses two modes in priority order:

#### 6.1 LLM Inference (optional, higher priority)

If `LLM_API_KEY` is set in `.env`, the tool sends the detected form's HTML to an LLM and asks it to map each logical field name to a CSS selector. The LLM response is a JSON object: `{ "field_name": "css_selector_or_null", ... }`.

LLM selectors are tried first. If a selector fails at fill time, the tool falls back to heuristics for that field.

**Supported providers** (via litellm):
- Together.ai (default)
- OpenAI
- Ollama (local/self-hosted)

**LLM settings** (in `src/autofiller/config.py`):

| Setting              | Default                                    | Description                                              |
|---------------------|--------------------------------------------|----------------------------------------------------------|
| `LLM_PROVIDER_PREFIX`| `together_ai`                              | litellm provider prefix                                  |
| `LLM_MODEL`          | `Qwen/Qwen3-235B-A22B-Instruct-2507-tput` | Model name (without provider prefix)                     |
| `LLM_BASE_URL`       | `None`                                     | Override API base URL (e.g. `http://localhost:11434/v1` for Ollama) |

#### 6.2 Heuristic Selectors (always runs, fallback)

The tool tries each CSS selector in the list for a field (from `field_config.py`) in order, and fills the first one that:
- Exists on the page.
- Is visible.
- Is editable.
- Is not a reCAPTCHA element.

If no selector matches, the field is skipped (with a warning printed).

---

### 8. Terminal Interaction

After each form is pre-filled, the terminal prints:

```
The contact form has been pre-filled as far as possible.
In the browser window:
  1) Review and edit the message field as needed.
  2) Make any manual corrections if a field was missed.
  3) Click the form's Submit/Send button yourself.

After reviewing the form:
  1) Save   - record contact and go to next URL
  2) Next   - skip saving and go to next URL
  3) Quit   - exit the script
Choice (1/2/3 or s/n/q):
```

**Choices:**

| Input       | Action                                             |
|------------|----------------------------------------------------|
| `1`, `s`, `save` | Insert the URL into `contacts.db` → next URL |
| `2`, `n`, `next` | Skip saving → next URL                       |
| `3`, `q`, `quit` | Close browser and exit                       |

If an error occurs processing a URL (e.g. page load failure), the tool asks whether to continue to the next URL.

---

### 9. Database Integration

The tool writes to the shared `contacts.db` SQLite database in the `Tools/` parent folder (the same database the tracker reads from).

**On Save:** Inserts a new row into the `CONTACTS` table with:
- `CONTACT_FORM_URL` = the submitted URL (UNIQUE; silently no-ops if already present).
- `CONTACTED_AT` = current timestamp.
- `CONTACT_SOURCE` = `CONTACT_FORM`.
- `STATUS` = `CONTACTED`.
- `VERTICAL` = the `vertical` value from the params file.
- `CONTACT_CITY` = the `city` value from the params file (if provided).
- `CONTACT_STATE` = the `state` value from the params file (if provided).
- `CONTACT_POSTAL_CODE` = the `zip` value from the params file (if provided).
- All other fields null (enriched later via the tracker app).

**Vertical auto-registration:** Before inserting the contact, if a `vertical` value was provided and it does not already exist in the `VERTICALS` table, it is inserted automatically (`INSERT OR IGNORE`). This ensures the vertical is always registered without requiring manual setup.

**Duplicate prevention:** Before navigating to each URL, the tool checks whether `CONTACT_FORM_URL` already exists in the database. If it does, the URL is skipped entirely (no browser navigation, no form filling) and a message is printed.

**Database initialization:** On startup, the tool calls `create_db.py` in the `Tools/` folder to create the database and tables if they do not already exist.

---

### 10. Tech Stack

| Component         | Technology                       | Notes                                         |
|------------------|----------------------------------|-----------------------------------------------|
| Language          | Python 3.10+                     |                                               |
| Browser automation| Playwright (Chromium)            | Runs in headed (visible) mode                 |
| LLM integration   | litellm                          | Multi-provider abstraction; optional          |
| Database          | SQLite3 (stdlib)                 | Shared `contacts.db` in `Tools/` folder       |
| Package manager   | Poetry                           |                                               |
| Configuration     | `field_config.py`, `.env`, `config.py`   | Set once per installation            |
| Runtime params    | `params/*.json`                  | One file per outreach batch                   |

---

### 11. Configuration

The tool uses two distinct categories of files:

#### 10.1 Configuration files (set once per installation)

These describe *how to fill forms*. Set them up once and reuse across all batches.

**`src/autofiller/field_config.py`**
Heuristic CSS selector lists for each contact form field. Edit `SELECTORS` directly to add patterns for non-standard field naming conventions you encounter.

**`.env`**
```bash
LLM_API_KEY=your_api_key_here   # Required only if using LLM inference; omit to use heuristics only
```

**`config.py`**
Edit `LLM_PROVIDER_PREFIX`, `LLM_MODEL`, and `LLM_BASE_URL` to switch LLM provider or use a local model (e.g. Ollama).

---

#### 10.2 Runtime params files (one per batch)

These describe *what to run* and *who you are* — the vertical, location, sender identity, and URL list for a specific outreach batch. Create a new params file in `params/` for each batch.

**`params/<name>.json`**
```json
{
  "vertical": "Legal",
  "contact_url_file": "contacts/contacts-legal-portland.json",
  "city": "Portland",
  "state": "OR",
  "zip": "97201",
  "field_values": {
    "name": "Jane Smith",
    "first_name": "Jane",
    "last_name": "Smith",
    "company": "Acme, LLC",
    "email": "jane@acme.com",
    "phone": "503-555-0100",
    "subject": "Partnership Inquiry",
    "message": "Hello,\nWe'd love to connect..."
  }
}
```

**`contacts/<name>.json`**
The list of contact form URLs for this batch. Pointed to by `contact_url_file` in the params file.

---

### 12. Setup and Running

```bash
# Install dependencies
poetry install
playwright install chromium

# Create the shared database (first time only)
python3 ../tracker-server/create_db.py

# Run a batch
poetry run python -m autofiller.main params/params-legal-portland.json
# or using the flag form:
poetry run python -m autofiller.main --params_file params/params-legal-portland.json
```
