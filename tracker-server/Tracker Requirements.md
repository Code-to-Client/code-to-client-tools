# Contact Form Outreach Tracker — Technical Requirements

**Version:** MVP (v1)
**Audience:** Developers building/running the app locally
**Source of truth:** *Code to Client* by Joel Gardi — Chapter 6 (Measurement System) and Chapter 7 (Executing the Framework)

---

### 1. Scope and Architecture

**Scope of this technical doc:**
- Single-user app, runs locally on the developer's machine.
- Implements the Chapter 6 measurement system exactly:
  - 8 pipeline statuses,
  - key response metrics (shown as count + % toggle), and
  - visitor tracking per vertical.

- Supports multiple verticals with per-vertical and aggregate dashboard views.
- Integrates with the Autofiller script via a shared SQLite database.
- No auth, no multi-tenant logic, no Pro features (import/export UI, analytics, reminders, etc.).

**High-level architecture:**
- **Frontend:** Nuxt 4 app (Vue 3 + Vite), running in SPA/client mode for this local, single-user tool.
- **Backend:** FastAPI app exposing a small REST API.
- **Database:** SQLite file, shared with the Autofiller script.
- **Communication:** Frontend calls backend over HTTP using `fetch`.

---

### 2. Tech Stack

| Layer     | Technology                      | Notes                                               |
|----------|---------------------------------|-----------------------------------------------------|
| Frontend | Nuxt 4 (Vue 3)                  | File-based routing; SPA/client mode locally         |
| State    | Pinia                           | Centralized state (contacts, dashboard, verticals, filters, locations) |
| HTTP     | native `fetch`                  | API calls (no axios required)                       |
| Styling  | UnoCSS (Wind preset)            | Utility-first CSS (Tailwind-compatible utilities)   |
| UI Lib   | Element Plus                    | Table, buttons, form inputs, dialogs                |
| Backend  | FastAPI                         | REST API, async capable                             |
| DB       | SQLite                          | Single `.db` file, local only; shared with script   |
| DB access| raw `sqlite3`                   | Python built-in; no ORM                            |

**Element Plus + UnoCSS:** Use Element Plus for UI components and UnoCSS (with `@unocss/preset-wind3` or `preset-wind4`) for layout, spacing, and colors.

**Styling and theming:**

- Use Element Plus default light/dark themes; do not add a heavy custom design system in MVP.
- UnoCSS for layout, spacing, and light tweaks around Element Plus components.
- Colors and shortcuts in `uno.config.ts`; Element Plus CSS variable overrides in a single global stylesheet.
- README should include a short "How to change colors" section.

**Color theming (runtime):**
- The app exposes a **primary color picker** and **secondary color picker** in the nav bar, each with 19 color options.
- Selected colors are applied as CSS variables (`--el-color-primary`, `--app-secondary`) so Element Plus components and custom utilities reflect the choice immediately.
- Selections persist to `localStorage` and are restored on next load.

**Dark mode:**
- A toggle switches between light and dark mode by toggling a `dark` class on `<html>`, using Element Plus's documented dark theme approach.
- UnoCSS `dark:` variants are used for custom utilities so they follow the same toggle.
- The preference persists to `localStorage`. On first load, the system `prefers-color-scheme` is used as the default.

**SQLite note:** Python's built-in `sqlite3` module is used; no separate DB install is needed. The app uses `contacts.db` in the project root (path hard-coded in `config.py`).

---

### 3. Data Model

#### 3.1 Entity: Contact

**Table:** `CONTACTS`

| Field                       | Type         | Notes                                                                                          |
|----------------------------|--------------|------------------------------------------------------------------------------------------------|
| ID                         | INTEGER (PK) | Auto-increment                                                                                 |
| CONTACT_FORM_URL           | TEXT UNIQUE  | Contact page URL. UNIQUE constraint prevents duplicate submissions to the same form.           |
| URL                        | TEXT         | Main website URL (nullable)                                                                    |
| VERTICAL                   | TEXT         | Vertical label, e.g. "Legal", "Property Management" (nullable; should match a VERTICALS.NAME) |
| CONTACT_SOURCE             | TEXT         | `CONTACT_FORM` or `MANUAL` — see §3.3                                                         |
| STATUS                     | TEXT         | One of the 8 allowed statuses — see §3.2                                                   |
| CONTACT_NAME               | TEXT         | Name of the person at the company (nullable)                                                   |
| CONTACT_COMPANY            | TEXT         | Company name (required)                                                                        |
| CONTACT_EMAIL              | TEXT         | Email address (nullable)                                                                       |
| CONTACT_PHONE              | TEXT         | Phone number (nullable)                                                                        |
| CONTACT_CITY               | TEXT         | City (nullable)                                                                                |
| CONTACT_STATE              | TEXT         | State/province (nullable)                                                                      |
| CONTACT_POSTAL_CODE        | TEXT         | Postal code (nullable)                                                                         |
| CONTACTED_AT  | TIMESTAMP    | When status first became `CONTACTED` (defaults to now on create; read-only after creation)     |
| DESIGN_PARTNER_PROSPECT_AT | TIMESTAMP    | When status first became `DESIGN_PARTNER_PROSPECT` (nullable)                                  |
| WAITLISTED_AT              | TIMESTAMP    | When status first became `WAITLISTED` (nullable)                                               |
| OTHER_PROSPECT_AT          | TIMESTAMP    | When status first became `OTHER_PROSPECT` (nullable)                                           |
| DISCOVERY_CALL_AT          | TIMESTAMP    | When status first became `DISCOVERY_CALL` (nullable)                                           |
| DESIGN_PARTNER_AT          | TIMESTAMP    | When status first became `DESIGN_PARTNER` (nullable)                                           |
| CUSTOMER_AT                | TIMESTAMP    | When status first became `CUSTOMER` (nullable)                                                 |
| NOT_INTERESTED_AT          | TIMESTAMP    | When status first became `NOT_INTERESTED` (nullable)                                           |
| NOTES                      | TEXT         | Free-form notes (nullable). Supports chronological entries via date-stamp helper — see §9.    |
| NEXT_ACTION                | TEXT         | Short text description of next step (nullable)                                                 |
| CREATED_AT                 | TIMESTAMP    | Auto-set on insert                                                                             |
| UPDATED_AT                 | TIMESTAMP    | Auto-set on update                                                                             |

**Status-entered dates rule:** When status changes to a given value, set the corresponding `*_AT` column to now **only if it is not already set.** This preserves the first time a contact entered each status, which is used for pipeline timing and the status history feature. The autofiller script sets `CONTACTED_AT` on insert; the app sets all other `*_AT` fields when status changes.

**`CONTACTED_AT` is read-only after creation.** It cannot be changed via the edit contact form.

#### 3.2 Status Enum (stored as TEXT, uppercase)

The eight statuses from Chapter 6, in pipeline order:

| Status value               | Label                   | Meaning                                                                                       |
|---------------------------|-------------------------|-----------------------------------------------------------------------------------------------|
| `CONTACTED`               | Contacted               | Form sent; no reply yet. Starting state for all outreach contacts.                            |
| `DESIGN_PARTNER_PROSPECT` | Design Partner Prospect | Contact replied with interest in possibly becoming a design partner.                          |
| `WAITLISTED`              | Waitlisted              | Contact replied asking for updates but is not ready to collaborate right now.                 |
| `OTHER_PROSPECT`          | Other Prospect          | Contact responded with a question, comment, or other reply that doesn't indicate collaboration or waitlist intent. |
| `DISCOVERY_CALL`          | Discovery Call          | A discovery call has been held or scheduled. Can follow any of the three response statuses.   |
| `DESIGN_PARTNER`          | Design Partner          | Confirmed collaborator actively working with the developer. Not a customer.                   |
| `CUSTOMER`                | Customer                | Paying client. Not counted as a design partner.                                               |
| `NOT_INTERESTED`          | Not Interested          | Contact declined to move forward (typically after a discovery call).                         |

**There is no generic "Responded" status.** When a reply is received, classify it immediately into exactly one of: `DESIGN_PARTNER_PROSPECT`, `WAITLISTED`, or `OTHER_PROSPECT`.

**Status flow:**

```
CONTACTED
  → DESIGN_PARTNER_PROSPECT  (replied: collaboration interest)
  → WAITLISTED               (replied: notify me later)
  → OTHER_PROSPECT           (replied: other)

DESIGN_PARTNER_PROSPECT | WAITLISTED | OTHER_PROSPECT
  → DISCOVERY_CALL

DISCOVERY_CALL
  → DESIGN_PARTNER
  → CUSTOMER
  → NOT_INTERESTED
```

#### 3.3 Contact Source (stored as TEXT, uppercase)

| Value           | Meaning                                                              |
|----------------|----------------------------------------------------------------------|
| `CONTACT_FORM` | Record created by the Contact Form Autofiller script.                |
| `MANUAL`       | Contact added manually via the app's "Add contact" form.            |

Default to `CONTACT_FORM` when the script inserts a row, `MANUAL` when the user creates a contact in the UI.

#### 3.4 Entity: Vertical

Verticals are first-class entities. They store the vertical name and its website visitor count (manually updated from host analytics). A vertical cannot be deleted while any contact references it.

**Table:** `VERTICALS`

| Field            | Type         | Notes                                                                          |
|-----------------|--------------|--------------------------------------------------------------------------------|
| ID              | INTEGER (PK) | Auto-increment                                                                 |
| NAME            | TEXT UNIQUE  | Vertical label (required, max 255 chars). Must be unique.                      |
| WEBSITE_VISITORS| INTEGER      | Latest known visitor count from the trackable contact form link (e.g. `?cf=1`). Updated manually by the developer after checking host analytics (Netlify, Vercel, etc.). Nullable until set. |
| CREATED_AT      | TIMESTAMP    | Auto-set on insert                                                             |
| UPDATED_AT      | TIMESTAMP    | Auto-set on update                                                             |

**Visitor tracking note:** The developer uses a trackable URL parameter (e.g. `?cf=1`) in their contact form message. After checking their host's analytics to see how many visitors came from that link, they update `WEBSITE_VISITORS` on the relevant vertical (or an "overall" record). The dashboard uses this value as the visitor count metric.

**Dashboard aggregate visitor count:** When displaying the aggregate dashboard (all verticals), sum `WEBSITE_VISITORS` across all verticals, or maintain a convention for an overall record (e.g. vertical name = `_all`). Implementation may vary; document the chosen approach in the README.

---

### 4. API Design

Base path: `/api/v1`

All responses are JSON. Errors use appropriate HTTP status codes (4xx/5xx) with a JSON body: `{"detail": "..."}`.

#### 4.1 Contacts

**GET `/api/v1/contacts`**
- **Query params:**
  - `status` — filter by a single status value (optional).
  - `vertical` — filter by vertical, exact match (optional).
  - `postal_code` — filter by postal code, exact match (optional). Use `N/A` to return contacts with no postal code.
  - `city_state` — filter by `"City, State"` string (optional). Use `N/A` to return contacts with no city.
  - `limit` — max results, 1–500 (default 50).
  - `offset` — pagination offset (default 0).
- **Response 200:** Array of contact objects (all fields from §3.1).

**POST `/api/v1/contacts`**
- **Request body:**
  - `company_name` (required)
  - `contact_name` (optional)
  - `email` (optional)
  - `phone` (optional)
  - `city` (optional)
  - `state` (optional)
  - `postal_code` (optional)
  - `url` (optional)
  - `contact_url` (optional; must be unique — 409 if already exists)
  - `vertical` (optional)
  - `status` (optional, defaults to `CONTACTED`)
  - `contact_source` (optional, defaults to `MANUAL`)
  - `contacted_at` (optional, defaults to now)
  - `notes` (optional)
  - `next_action` (optional)
- **Response 201:** Created contact object.
- **Errors:** 409 if `contact_url` already exists.

**GET `/api/v1/contacts/{id}`**
- **Response 200:** Contact object plus a computed `status_history` array — see §4.1.1.
- **Errors:** 404 if not found.

**PATCH `/api/v1/contacts/{id}`**
- **Request body:** Any subset of editable fields. `contacted_at` / `CONTACTED_AT` is **not** patchable after creation.
- **Behavior:**
  - Only provided fields are updated.
  - When `status` changes, set the corresponding `*_AT` column to now if not already set.
  - `UPDATED_AT` is set to now on any successful update.
- **Response 200:** Updated contact object (including updated `status_history`).
- **Errors:** 404 if not found; 422 if invalid status value.

**DELETE `/api/v1/contacts/{id}`**
- **Response 204:** No content.
- **Errors:** 404 if not found.

#### 4.1.1 Status History (computed field on GET /contacts/{id})

`GET /api/v1/contacts/{id}` includes a computed `status_history` array alongside the contact fields. It is built from the contact's `*_AT` timestamp fields and contains one entry per status that has been entered (i.e. has a non-null `*_AT` value), ordered descending by date.

```json
"status_history": [
  { "status": "DISCOVERY_CALL", "changed_at": "2026-02-10T14:30:00" },
  { "status": "DESIGN_PARTNER_PROSPECT", "changed_at": "2026-02-05T09:00:00" },
  { "status": "CONTACTED", "changed_at": "2026-01-28T11:00:00" }
]
```

The client displays this as a timeline sidebar on the contact detail page.

---

#### 4.2 Dashboard

**GET `/api/v1/dashboard`**
- **Query params:**
  - `vertical` — filter to a specific vertical (optional; omit for aggregate across all verticals).
  - `postal_code` — filter by postal code (optional). Use `N/A` for contacts with no postal code.
  - `city_state` — filter by `"City, State"` string (optional). Use `N/A` for contacts with no city.
- **Response 200:**

```json
{
  "vertical": null,
  "contacts_sent": 350,
  "visitor_count": 140,
  "total_responses": 32,
  "design_partner_prospects": 6,
  "waitlist_signups": 21,
  "other_prospects": 5,
  "response_rate_pct": 9.1,
  "pct_of_contacts_sent": {
    "visitor_count": 40.0,
    "total_responses": 9.1,
    "design_partner_prospects": 1.7,
    "waitlist_signups": 6.0,
    "other_prospects": 1.4
  },
  "by_status": {
    "CONTACTED": 318,
    "DESIGN_PARTNER_PROSPECT": 6,
    "WAITLISTED": 21,
    "OTHER_PROSPECT": 5,
    "DISCOVERY_CALL": 3,
    "DESIGN_PARTNER": 2,
    "CUSTOMER": 0,
    "NOT_INTERESTED": 1
  }
}
```

**Metric definitions:**

| Metric                    | Definition                                                                                                     |
|--------------------------|----------------------------------------------------------------------------------------------------------------|
| `contacts_sent`          | Total rows in `CONTACTS` (filtered by vertical/location if provided).                                         |
| `visitor_count`          | `WEBSITE_VISITORS` from the matching `VERTICALS` row. Summed across all verticals when no vertical is specified. |
| `total_responses`        | COUNT where `DESIGN_PARTNER_PROSPECT_AT IS NOT NULL` + `WAITLISTED_AT IS NOT NULL` + `OTHER_PROSPECT_AT IS NOT NULL`. Based on *_AT timestamps, not current status. |
| `design_partner_prospects`| COUNT where `DESIGN_PARTNER_PROSPECT_AT IS NOT NULL`.                                                        |
| `waitlist_signups`       | COUNT where `WAITLISTED_AT IS NOT NULL`.                                                                       |
| `other_prospects`        | COUNT where `OTHER_PROSPECT_AT IS NOT NULL`.                                                                   |
| `response_rate_pct`      | `(total_responses / max(contacts_sent, 1)) * 100`, rounded to one decimal.                                   |
| `pct_of_contacts_sent`   | Each metric divided by `contacts_sent` × 100, rounded to one decimal. 0.0 if `contacts_sent` is 0.           |

**Important:** Response metrics (`total_responses`, `design_partner_prospects`, `waitlist_signups`, `other_prospects`) are counts of contacts that have *ever* reached those statuses (based on `*_AT` timestamps), regardless of what their current status is. `by_status` provides per-current-status counts for the pipeline summary.

---

#### 4.3 Locations

**GET `/api/v1/locations`**
- **Query params:**
  - `vertical` — scope to a specific vertical (optional; omit for all verticals).
- **Response 200:**
```json
{
  "zips": ["N/A", "97201", "97202"],
  "city_states": ["N/A", "Portland, OR", "Seattle, WA"]
}
```
- `"N/A"` is prepended to each list when any contacts in scope have a missing value for that field.
- Used to populate the zip and city/state filter dropdowns in the UI.

---

#### 4.4 Verticals

**GET `/api/v1/verticals`**
- **Response 200:** Array of vertical objects, each including all fields from §3.4 plus a computed `contact_count` (number of contacts referencing this vertical).

**POST `/api/v1/verticals`**
- **Request body:**
  - `name` (required, 1–255 chars; must be unique)
  - `website_visitors` (optional, integer ≥ 0)
- **Response 201:** Created vertical object.
- **Errors:** 409 if name already exists.

**PATCH `/api/v1/verticals/{id}`**
- **Request body:** Any subset of: `name`, `website_visitors`. At least one field required.
- **Response 200:** Updated vertical object.
- **Errors:** 404 if not found; 409 if name conflicts with existing vertical.

**DELETE `/api/v1/verticals/{id}`**
- **Behavior:** Rejected if any contact has `VERTICAL` matching this vertical's name.
- **Response 204:** No content on success.
- **Errors:** 404 if not found; 409 if vertical is in use by one or more contacts.

---

---

### 5. Frontend Structure

```text
app/
├── app.vue                        # Root layout with nav bar
├── composables/
│   ├── useApi.js                  # fetch wrapper for /api/v1
│   ├── useDark.js                 # Dark mode toggle + localStorage persistence
│   ├── usePrimaryColor.js         # Primary color picker + CSS vars + localStorage
│   └── useSecondaryColor.js       # Secondary color picker + CSS vars + localStorage
├── stores/
│   ├── contacts.js                # Pinia: contacts list, CRUD, status labels/colors
│   ├── dashboard.js               # Pinia: dashboard metrics
│   ├── filters.js                 # Pinia: global filter state (vertical, zip, cityState) + localStorage persistence
│   ├── locations.js               # Pinia: zip and city/state lists from /api/v1/locations
│   └── verticals.js               # Pinia: verticals CRUD
├── pages/
│   ├── index.vue                  # Dashboard
│   ├── contacts/
│   │   ├── index.vue              # Contact list with status filter and quick-view modal
│   │   ├── new.vue                # Add contact form
│   │   └── [id].vue               # Edit contact with status history sidebar
│   ├── settings/
│   │   └── verticals.vue          # Verticals CRUD management
├── components/
│   ├── GlobalFilters.vue          # Shared vertical + zip + city/state filter bar (used on dashboard and contacts pages)
│   ├── StatusBadge.vue            # Colored status label
│   ├── MetricCard.vue             # Dashboard metric card (value + % annotation)
│   └── StatusCard.vue             # Dashboard status count card (label colored by status)
└── assets/
    └── css/main.css               # Global styles and Element Plus overrides
```

All Pinia stores use the Composition API style (`defineStore('id', () => { ... })`).

**Routes:**
- `/` — Dashboard.
- `/contacts` — Contact list (filterable by status; vertical/location via global filters).
- `/contacts/new` — New contact form.
- `/contacts/:id` — Contact detail / edit.
- `/settings/verticals` — Verticals management.

---

### 6. Global Filters

Vertical, zip, and city/state filters are **global** — shared across the dashboard and contacts pages. They are managed by `useFiltersStore` (Pinia) and persisted to `localStorage`.

**`GlobalFilters.vue` component:**
- Rendered in the top-right of the page header on both the dashboard and contacts pages.
- Shows a Vertical dropdown (or the vertical name as plain text when only one vertical exists), a Zip dropdown, and a City/State dropdown.
- Zip and City/State dropdowns are scoped to the selected vertical: when a vertical is selected, only locations belonging to that vertical are listed.
- Selecting a zip clears the city/state selection; selecting a city/state clears the zip selection.
- Changing the vertical clears both zip and city/state and re-fetches the location lists.
- `"N/A"` appears as the first option in each location dropdown when any contacts in scope have a missing value for that field.

**`useFiltersStore`:**
- Exposes: `vertical`, `zip`, `cityState` (all refs, default `''`).
- Each value is watched and persisted to `localStorage` on change.
- Keys: `tracker-vertical`, `tracker-zip`, `tracker-city-state`.

**`useLocationsStore`:**
- Exposes: `zips`, `cityStates`, `loading`, `fetchList(vertical?)`.
- `fetchList` calls `GET /api/v1/locations?vertical=...` (vertical omitted when empty).

---

### 7. Dashboard Layout

Two sections, matching the Chapter 6 measurement system.

**Header row:** Page title on the left, `<GlobalFilters />` on the right.

**Section 1 — Key Metrics:** Six `MetricCard` components in a 3-column grid:
Contacts Sent, Website Visitors, Total Responses, Design Partner Prospects, Waitlist Signups, Other Prospects.

Each card always shows the **count**. A `% Contacted / % Visitors` radio toggle (shown to the right of the "Key metrics" heading) controls the % annotation:
- **% Contacted mode:** Contacts Sent shows `100%`; the four response metrics show their % of contacts sent.
- **% Visitors mode:** Website Visitors shows `100%`; the four response metrics show their % of visitor count.
- No % is shown on the non-baseline card in either mode.

**Section 2 — Contacts by Status:** One `StatusCard` per status (Contacted, Design Partner Prospect, Waitlisted, Other Prospect, Discovery Call, Design Partner, Customer, Not Interested), each showing count. The card label text is colored to match the status (no left-colored border).

**Filters:** The `<GlobalFilters />` component handles vertical, zip, and city/state filtering. Any change to the global filters triggers a re-fetch of the dashboard data.

---

### 8. Contact List Page

**Header row:** Page title on the left, `<GlobalFilters />` on the right.

**Card header:** Contact count label on the left; Status filter dropdown and "Add contact" button on the right (all in one row).

- **Status filter:** Dropdown inside the card header. Filters the contact list by current status. Defaults to "All".
- **Vertical, zip, city/state filters:** Handled globally by `<GlobalFilters />`. Any change triggers a re-fetch.

**Table columns:** All sortable except Actions.
- Company name, Vertical, Contact page URL, Status badge, Contacted date, Actions.

**Actions per row:**
- **View** — opens a quick-view modal showing all contact fields (including city, state, postal code) and status history (read-only). Includes an "Edit" button to navigate to the full edit page.
- **Edit** — navigates to `/contacts/:id`.

---

### 9. Add Contact Form

**Fields:** contact_name, company_name (required), email, phone, city, state, postal_code, url, contact_url, vertical, contacted_at (date picker, defaults to today in local timezone), status (defaults to `CONTACTED`), notes, next_action.

**Layout:** Email and phone on one row; city, state, and zip on one row (CSS grid, offset to align with other form fields).

**Default vertical:** Pre-selected to the first vertical in the list on mount.

**Contacted date default:** Uses `new Date().toLocaleDateString('en-CA')` to get the local date (avoids UTC off-by-one-day issue from `toISOString()`).

**Smart URL inference:** When `contact_url` is filled in and `url` is empty, `url` is auto-populated with the origin of the contact URL (e.g. `https://example.com/contact` → `https://example.com`). This runs on focus-out of the contact_url field.

**Inline vertical creation:** The vertical field is a creatable dropdown — the user can type a new vertical name to create it on the fly without navigating to the verticals settings page.

**Save behavior:** Redirects to `/contacts/:id` (the detail page for the new contact) on success.

---

### 10. Edit Contact Page

**Form fields:** Same as Add Contact except `contacted_at` is **displayed but disabled** — it cannot be changed after creation.

**After save:** Re-fetches the full contact (including `status_history`) from `GET /api/v1/contacts/{id}` to keep the status history sidebar up to date.

**Status history sidebar:** Shows a chronological timeline of the contact's status transitions, built from the `status_history` array returned by `GET /api/v1/contacts/{id}`. Entries sorted descending (most recent first). Scrollable if the list is long.

**Notes field — date-stamp helper:** The notes textarea includes a helper button that prepends today's date as a label (e.g. `[2026-03-10]`) to the existing notes content. This makes it easy to maintain a chronological log of interactions within a single notes field.

**Delete:** A delete button opens a confirmation dialog. On confirm, deletes the contact and redirects to `/contacts`. If deletion fails (e.g. server error), shows an error notification without navigating away.

---

### 11. Verticals Settings Page (`/settings/verticals`)

- Table columns: Name, Website Visitors, Contact Count, Actions.
- **Add vertical:** Opens a dialog with Name (required, max 255) and Website Visitors (optional integer).
- **Edit vertical:** Opens the same dialog pre-filled. Name and Website Visitors are editable.
- **Delete vertical:** Opens a confirmation dialog. If the vertical has contacts, the delete button is disabled and a tooltip explains why.
- **Auto-select on delete:** After a vertical is deleted, if only one vertical remains, it is automatically set as the selected vertical in `useFiltersStore`.
- Contact count is read-only (computed by the API via JOIN; not editable).

---

### 12. Autofiller Script Integration

The Contact Form Autofiller script (Python + Playwright) writes directly to the same SQLite database.

**CLI:** The script takes a single `--params_file` argument pointing to a JSON file that specifies per-batch runtime parameters:
```json
{
  "vertical": "Legal",
  "contact_url_file": "contacts/contacts-legal-portland.json",
  "city": "Portland",
  "state": "OR",
  "zip": "97201"
}
```
`city`, `state`, and `zip` are optional (can be empty strings or omitted).

**Script insert behavior:**
- Inserts a row into `CONTACTS` with:
  - `CONTACT_FORM_URL` = the contact form page URL (UNIQUE; duplicate submissions to the same form are silently ignored or raise a conflict)
  - `STATUS` = `CONTACTED`
  - `CONTACT_SOURCE` = `CONTACT_FORM`
  - `CONTACTED_AT` = now
  - `VERTICAL` = from params file
  - `CONTACT_CITY`, `CONTACT_STATE`, `CONTACT_POSTAL_CODE` = from params file (nullable)
  - All other fields null or default
- New rows appear in the contact list immediately on next app load — no sync step needed.

The developer enriches each record (company name, contact name, notes, status updates) via the app as replies come in.

---

### 13. Environment & Configuration

**Backend (`config.py`):**

No `.env` file is read by the backend. Configuration is hard-coded in `src/tracker_server/config.py`:
- `DB_PATH`: `contacts.db` in the project root
- `CORS_ORIGINS`: `http://localhost:5173`, `http://localhost:3000`

**Frontend (`.env`):**
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

### 14. Non-Functional Requirements

| Aspect       | Target                                                              |
|-------------|---------------------------------------------------------------------|
| Performance | Dashboard loads in < 1s with up to ~1,000 contacts                 |
| Browser     | Recent versions of Chrome, Firefox, Safari                          |
| Offline     | Not required                                                        |
| Deployment  | Local dev: `npm run dev` + `uvicorn tracker_server.main:app --reload` |

No containerization or cloud deployment required for MVP. The app runs directly on the developer's machine alongside the autofiller script.
