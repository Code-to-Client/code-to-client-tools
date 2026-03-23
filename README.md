# Code to Client — Free Tools

Free developer tools for readers of [*Code to Client: Job Market in Crisis*](https://code-to-client.com) book.

These tools support the outreach framework described in the book — helping developers find consulting clients through contact forms, design partners, and semi-automation. No cold calls. No fake confidence.

---

## Tools

This repository contains three projects: **`autofiller`**, a Python CLI tool that automates pre-filling contact forms in a browser; **`tracker-client`**, a Vue frontend for managing and visualizing your outreach pipeline; and **`tracker-server`**, a Python backend API that persists and serves your contact data. The tracker client and server share a local `contacts.db` SQLite database. Together, the autofiller and tracker form a complete semi-automated outreach workflow — from first contact to signed client.

### 1. Contact Form Autofiller (`autofiller/`)

A Python CLI tool that opens contact forms in a browser and pre-fills your outreach message automatically. You review and submit manually — keeping you in control of every send.

**Requirements:** Python 3.11+, Poetry

```bash
cd autofiller
poetry install
poetry run python -m autofiller.main params/your-params.json
```

See [`autofiller/README.md`](autofiller/README.md) for full setup and usage instructions.

---

### 2. Outreach Tracker (`tracker-client/` + `tracker-server/`)

A local web app for tracking every contact through the eight pipeline statuses defined in Chapter 6 of the book. Dashboard metrics tell you exactly where you are and when to pivot.

**Requirements:** Node 20+, Python 3.11+, Poetry

```bash
# Start the backend
cd tracker-server
poetry install
poetry run python -m tracker_server.main

# Start the frontend (in a separate terminal)
cd tracker-client
npm install
npm run dev
```

See [autofiller/README.md](autofiller/README.md),[`tracker-client/README.md`](tracker-client/README.md) and [`tracker-server/README.md`](tracker-server/README.md) for full setup instructions.

---

## Reporting Bugs

Open an issue at [github.com/code-to-client/code-to-client-tools/issues](https://github.com/code-to-client/code-to-client-tools/issues).

## License

MIT — free to use, modify, and share.
