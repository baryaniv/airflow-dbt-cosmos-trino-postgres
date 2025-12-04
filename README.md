# Airflow + dbt + Astronomer Cosmos + Trino + Postgres

A simple, readable project showcasing the integration of:
- **Airflow 2.10.0** - Workflow orchestration
- **dbt** - Data transformation
- **Astronomer Cosmos** - dbt integration for Airflow
- **Trino** - Distributed SQL query engine
- **Postgres** - Source database

All running locally in a single Docker Compose setup.

## Architecture

```
Airflow → dbt (via Cosmos) → Trino → Postgres
```

## Project Structure

```
.
├── docker-compose.yml      # All services in one compose file
├── airflow/                # All Airflow-related files
│   ├── dags/              # Airflow DAGs
│   │   ├── __init__.py
│   │   └── simple_dbt_dag.py
│   ├── dbt_projects/       # dbt projects directory
│   │   └── dbt_project_example/  # Example dbt project
│   │       ├── dbt_project.yml
│   │       ├── profiles.yml
│   │       ├── models/
│   │       │   ├── customers.sql
│   │       │   └── schema.yml
│   │       ├── analyses/      # dbt analyses (with .gitkeep)
│   │       ├── tests/         # dbt tests (with .gitkeep)
│   │       ├── seeds/         # dbt seeds (with .gitkeep)
│   │       ├── macros/        # dbt macros (with .gitkeep)
│   │       └── snapshots/     # dbt snapshots (with .gitkeep)
│   ├── scripts/           # Utility scripts
│   │   └── setup_connections.py
│   ├── dbt_utils.py       # Cosmos integration utilities
│   ├── requirements.txt  # Python dependencies
│   ├── logs/              # Airflow logs
│   └── plugins/           # Airflow plugins
├── trino/                  # Trino catalog configuration
│   └── catalog/
│       └── postgres.properties
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM

### Setup

1. **Set environment variables** (optional):
   ```bash
   # Create .env file with optional overrides
   echo "AIRFLOW_UID=$(id -u 2>/dev/null || echo 50000)" > .env
   echo "TRINO_USER=admin" >> .env
   echo "TRINO_PASSWORD=admin123" >> .env
   ```
   Default values: `TRINO_USER=admin`, `TRINO_PASSWORD=admin123`


3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to initialize** (especially the first time):
   ```bash
   docker-compose logs -f airflow-init
   ```
   Wait until you see "Trino connection created successfully!" or similar.

5. **Access the services**:
   - **Airflow UI**: http://localhost:18081
     - Username: `admin`
     - Password: `admin`
   - **Trino UI**: http://localhost:18080
   - **Postgres**: localhost:15432

### Running the DAG

1. Open the Airflow UI at http://localhost:18081
2. Find the `simple_dbt_cosmos_dag` DAG
3. Unpause it (toggle switch on the left)
4. Trigger it manually or wait for the schedule

### Verifying Results

After the DAG runs successfully, you can query the created table through Trino:

**Using Trino CLI:**
```bash
trino --server http://localhost:18080 --user admin
```

Then run:
```sql
SELECT * FROM postgres.postgres.customers;
```

**Using Trino Web UI:**
1. Go to http://localhost:18080
2. Execute: `SELECT * FROM postgres.postgres.customers;`

**Note:** The table is created in Trino's `postgres.postgres` schema (catalog.schema), not directly in Postgres. Trino acts as the query layer.

## Key Files

### `airflow/dbt_utils.py`

Contains utility functions for creating dbt TaskGroups with Cosmos:
- `get_trino_profile_config()` - Configures Trino connection for dbt
- `create_dbt_task_group()` - Creates a Cosmos DbtTaskGroup

### `airflow/dags/simple_dbt_dag.py`

Example Airflow DAG that:
1. Verifies Trino connection
2. Runs dbt models using Cosmos

### `airflow/dbt_projects/dbt_project_example/models/customers.sql`

Simple dbt model that creates a customers table with sample data.

## Services

- **Postgres** (port 15432): Source database
  - Username: `postgres`
  - Password: `postgres`
  - Database: `postgres`
- **Trino** (port 18080): Query engine connecting to Postgres
  - Username: `admin` (or any username)
  - Password: (empty, no password required)
  - Web UI: http://localhost:18080
- **Airflow Webserver** (port 18081): Airflow UI
- **Airflow Scheduler**: Runs DAGs

## Connecting to Trino

### From your local machine:

**Using Trino CLI:**
```bash
trino --server http://localhost:18080 --user admin
```

**Using JDBC URL:**
```
jdbc:trino://localhost:18080/postgres/postgres
```

**Using Python (trino library):**
```python
from trino.dbapi import connect

conn = connect(
    host='localhost',
    port=18080,
    user='admin',
    catalog='postgres',
    schema='postgres'
)
```

**Using dbt:**
The connection is already configured in `airflow/dbt_projects/dbt_project_example/profiles.yml`

### From inside Docker containers:
- Host: `trino` (service name)
- Port: `8080` (internal port)
- User: `admin`
- Password: (empty)

## Customization

### Adding More dbt Models

1. Add SQL files to `airflow/dbt_projects/dbt_project_example/models/`
2. Update `airflow/dbt_projects/dbt_project_example/models/schema.yml` with model documentation
3. The DAG will automatically pick up new models

### Modifying Connections

Trino connection is automatically created during initialization. To modify:
- Edit the `airflow connections add` command in `docker-compose.yml`
- Or use the Airflow UI: Admin → Connections

## Troubleshooting

### Services won't start
- Check if ports 15432, 18080, 18081 are available
- Ensure Docker has enough resources allocated

### DAG not appearing
- Check `docker-compose logs airflow-scheduler` for errors
- Verify DAG file is in `airflow/dags/` directory
- Check for Python syntax errors

### Trino connection issues
- Verify Trino is running: `docker-compose ps trino`
- Check Trino logs: `docker-compose logs trino`
- Verify Postgres is accessible from Trino

## Clean Up

```bash
docker-compose down -v
```

This removes all containers and volumes.

## License

MIT
