# Contact Form Outreach Tracker — API Server

Backend for the **Contact Form Outreach Tracker** (see [Contact Form Tracker Requirements](../../business/Book/Tools/Contact%20Form%20Tracker%20Requirements%20-%20Technical.md)). It uses the **same SQLite database** as the [autofiller](../../autofiller) autofiller script (`contacts.db`), so contacts submitted by the script appear in the tracker and vice versa.

## Setup and run (pip)

```bash
cd tracker-server
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
python -m tracker_server.main
```

Server runs at `http://localhost:8000`. API docs: `http://localhost:8000/docs`

## Setup and run (Poetry)

```bash
cd tracker-server
poetry install
poetry run python -m tracker_server.main
```

## Database

- **Shared DB:** The server reads and writes to `contacts.db` (path in `Config.DB_PATH`).

## CORS

Allowed origins default to `http://localhost:5173` and `http://localhost:3000` (Nuxt/Vite dev servers). Edit `Config.CORS_ORIGINS` in `config.py` to change.

## Task runner (mask) — optional

The project includes a `maskfile.md` with shorthand commands for common tasks. Using [mask](https://github.com/jacobdeichert/mask?tab=readme-ov-file) is optional — see that link for installation instructions. If you prefer not to install it, use the equivalent commands listed below directly.

| mask command | Equivalent command | Description |
|---|---|---|
| `mask db` | `python3 create_db.py` | Create the shared contacts database and tables |
| `mask main` | `poetry run python -m tracker_server.main` | Run the server |

## API overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/contacts` | List contacts (optional `status`, `vertical`, `postal_code`, `city_state`, `limit`, `offset`) |
| POST | `/api/v1/contacts` | Create contact |
| GET | `/api/v1/contacts/{id}` | Get one contact (includes `status_history`) |
| PATCH | `/api/v1/contacts/{id}` | Update contact |
| DELETE | `/api/v1/contacts/{id}` | Delete contact |
| GET | `/api/v1/dashboard` | Dashboard metrics (optional `vertical`, `postal_code`, `city_state`) |
| GET | `/api/v1/locations` | Unique zip codes and city/state values (optional `vertical`) |
| GET | `/api/v1/verticals` | List verticals (includes `contact_count`) |
| POST | `/api/v1/verticals` | Create vertical |
| PATCH | `/api/v1/verticals/{id}` | Update vertical |
| DELETE | `/api/v1/verticals/{id}` | Delete vertical (rejected if contacts reference it) |
