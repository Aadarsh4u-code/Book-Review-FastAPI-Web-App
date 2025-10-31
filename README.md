### Create a new migration (manual)
alembic revision -m "description"

### Create migration from model changes (auto)
alembic revision --autogenerate -m "description"

### Apply all migrations
alembic upgrade head

### Apply specific migration
alembic upgrade abc123

### Rollback one migration
alembic downgrade -1

### Rollback to specific version
alembic downgrade abc123

### Rollback all migrations
alembic downgrade base

### Show current version
alembic current

### Show migration history
alembic history --verbose

### Show SQL without running
alembic upgrade head --sql

