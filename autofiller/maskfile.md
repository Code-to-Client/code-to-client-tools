# Project commands

## db
> Create the shared contacts database and tables

```bash
python3 ../tracker-server/create_db.py
```


## main
> Submit contact forms for contact page URLs via browser

- Input: contact pages file paths - `contacts/bookkeeper-contacts-{city}.json`
- Output: Insert contact URLs in DB

```bash
    poetry run python -m autofiller.main params/Bookkeeping-portland.json
```

