# Alembic Managed Local Docker Postgres Database

Alembic allows us to do live schema migrations which is very important and useful

## Schema Migrations
If you want to do a schema migration, ie adding/deleting columns or tables in the database

1. Edit the database.py in models folder (This is the schema you are trying to change to)

2. Create a revision for the change

```bash
uv run alembic revision --autogenerate -m "your update message here"
```

3. Apply the changes to the database
```bash
uv run alembic upgrade head
```

### Viewing Migration History
To view migration history
```bash
uv run alembic history
```

### Rolling back migrations
To roll back the last migration
```bash
uv run alembic downgrade -1
```
To roll back to a specific version
```bash
uv run alembic downgrade <revision_id>
```
Rolling back everything
```bash
uv run alembic downgrade base
```