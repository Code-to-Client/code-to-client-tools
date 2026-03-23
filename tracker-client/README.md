# Contact Form Outreach Tracker — Client

Frontend for the **Contact Form Outreach Tracker**, built with **Nuxt 4** (Vue 3 + Vite). Connects to the FastAPI backend at `http://localhost:8000` by default.

For full product and technical requirements covering both the frontend and backend, see [Tracker Requirements.md](../tracker-server/Tracker%20Requirements.md).

## Prerequisites

- Node.js 18+
- The tracker API server running (`tracker-server`)

## Setup and run

```bash
cd tracker-client
npm install
npm run dev
```

App runs at `http://localhost:3000`.

## Configuration

Set `NUXT_PUBLIC_API_BASE_URL` to point to the API (default: `http://localhost:8000/api/v1`).

## Pages

- **/** — Dashboard (metrics, pipeline summary)
- **/contacts** — Contact list with status and global location filters
- **/contacts/new** — Add contact
- **/contacts/:id** — Contact detail (view/edit/delete, status history sidebar)
- **/settings/verticals** — Verticals management

## Project structure

```
app/
├── app.vue                        # Root layout with nav bar
├── composables/
│   ├── useApi.js                  # Fetch wrapper for /api/v1 — wraps GET/POST/PATCH/DELETE
│   ├── useDark.js                 # Dark mode toggle + localStorage persistence
│   ├── usePrimaryColor.js         # Primary color picker + CSS vars + localStorage
│   └── useSecondaryColor.js       # Secondary color picker + CSS vars + localStorage
├── stores/
│   ├── contacts.js                # Contacts CRUD + STATUS_LABELS / STATUS_COLORS constants
│   ├── dashboard.js               # Dashboard metrics fetch
│   ├── filters.js                 # Global filter state: vertical, zip, cityState (localStorage-persisted)
│   ├── locations.js               # Zip + city/state lists from /api/v1/locations
│   ├── verticals.js               # Verticals CRUD
├── components/
│   ├── GlobalFilters.vue          # Vertical + zip + city/state filter bar (shared across pages)
│   ├── MetricCard.vue             # Dashboard metric card (count + optional % annotation)
│   ├── StatusBadge.vue            # Colored status label chip
│   ├── StatusCard.vue             # Dashboard pipeline status card (label colored by status)
│   └── StatusHistory.vue          # Status transition timeline (used in contact detail sidebar)
├── pages/
│   ├── index.vue                  # Dashboard
│   ├── contacts/
│   │   ├── index.vue              # Contact list
│   │   ├── new.vue                # Add contact form
│   │   └── [id].vue               # Edit contact + status history sidebar
│   ├── settings/
│   │   └── verticals.vue          # Verticals management
└── assets/
    └── css/main.css               # Global styles and Element Plus CSS variable overrides
```

All Pinia stores use Composition API style (`defineStore('id', () => { ... })`). All composables and stores are auto-imported by Nuxt.

## Composables

### `useApi`

Thin fetch wrapper that reads `NUXT_PUBLIC_API_BASE_URL` from runtime config and provides `get`, `post`, `patch`, and `delete` helpers. Throws an `Error` with the server's `detail` message on non-2xx responses. Returns `undefined` for 204 No Content.

```js
const api = useApi()
const contacts = await api.get('/contacts?status=CONTACTED')
const created  = await api.post('/contacts', { company_name: 'Acme' })
await api.patch('/contacts/1', { status: 'WAITLISTED' })
await api.delete('/contacts/1')
```

## Stores

### `useContactsStore`

| Export | Type | Description |
|---|---|---|
| `items` | `Ref<Contact[]>` | Current contact list |
| `loading` | `Ref<boolean>` | True while fetching |
| `fetchList(params?)` | function | Load contacts; accepts `status`, `vertical`, `postal_code`, `city_state`, `limit`, `offset` |
| `fetchOne(id)` | function | Fetch one contact (includes `status_history`) |
| `create(body)` | function | POST new contact |
| `update(id, body)` | function | PATCH contact |
| `remove(id)` | function | DELETE contact |

Also exports `STATUS_LABELS` (display strings) and `STATUS_COLORS` (hex values) keyed by status value.

### `useDashboardStore`

| Export | Type | Description |
|---|---|---|
| `data` | `Ref<DashboardData \| null>` | Latest dashboard response |
| `loading` | `Ref<boolean>` | True while fetching |
| `fetch(params?)` | function | Load dashboard; accepts `vertical`, `postal_code`, `city_state` |

### `useFiltersStore`

Global filter state shared across the dashboard and contacts pages. Values are persisted to `localStorage`.

| Export | Type | localStorage key |
|---|---|---|
| `vertical` | `Ref<string>` | `tracker-vertical` |
| `zip` | `Ref<string>` | `tracker-zip` |
| `cityState` | `Ref<string>` | `tracker-city-state` |

### `useLocationsStore`

| Export | Type | Description |
|---|---|---|
| `zips` | `Ref<string[]>` | Unique postal codes (scoped to selected vertical) |
| `cityStates` | `Ref<string[]>` | Unique `"City, State"` strings |
| `loading` | `Ref<boolean>` | True while fetching |
| `fetchList(vertical?)` | function | Load from `/api/v1/locations`; pass vertical to scope results |

### `useVerticalsStore`

| Export | Type | Description |
|---|---|---|
| `items` | `Ref<Vertical[]>` | Current verticals list |
| `loading` | `Ref<boolean>` | True while fetching |
| `fetchList()` | function | Load all verticals (includes `contact_count`) |
| `create(body)` | function | POST new vertical |
| `update(id, body)` | function | PATCH vertical |
| `remove(id)` | function | DELETE vertical |

## Styling and theming

- **UnoCSS:** Edit `uno.config.js` to change theme colors and shortcuts (primary, success, danger, grays). Uses Tailwind-compatible preset; `dark:` variants follow the app dark-mode toggle.
- **Element Plus:** Light/dark mode is toggled in the nav. For deeper theming, override Element Plus CSS variables in `app/assets/css/main.css` (see comments there).
- **Runtime color pickers:** Primary and secondary color pickers in the nav bar apply CSS variables (`--el-color-primary`, `--app-secondary`) immediately; selections persist to `localStorage`.
