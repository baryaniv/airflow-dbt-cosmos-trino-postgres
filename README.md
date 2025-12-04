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
├── docker-compose.yml          # All services in one compose file
├── Dockerfile                  # Custom Airflow image with dbt in venv
├── requirements.txt            # Python dependencies
├── airflow/                    # All Airflow-related files
│   ├── dags/                  # Airflow DAGs
│   │   ├── simple_dbt_dag.py  # Main DAG using dbt_utils
│   │   └── utils/             # Utility modules
│   │       └── dbt_utils.py   # Cosmos integration utilities
│   ├── dbt_projects/          # dbt projects directory
│   │   └── dbt_project_example/  # Example dbt project
│   │       ├── dbt_project.yml
│   │       ├── profiles.yml   # dbt profile configuration
│   │       ├── models/
│   │       │   ├── customers.sql
│   │       │   ├── first_customer.sql
│   │       │   └── schema.yml
│   │       ├── analyses/      # dbt analyses (with .gitkeep)
│   │       ├── tests/         # dbt tests (with .gitkeep)
│   │       ├── seeds/         # dbt seeds (with .gitkeep)
│   │       ├── macros/        # dbt macros (with .gitkeep)
│   │       └── snapshots/     # dbt snapshots (with .gitkeep)
│   ├── logs/                  # Airflow logs
│   └── plugins/               # Airflow plugins
├── trino/                      # Trino catalog configuration
│   └── catalog/
│       └── postgres.properties
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM

### Setup

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to initialize** (especially the first time):
   ```bash
   docker-compose logs -f airflow-init
   ```
   Wait until you see the initialization complete.

3. **Access the services**:
   - **Airflow UI**: http://localhost:18081
     - Username: `admin`
     - Password: `admin`
   - **Trino UI**: http://localhost:18080
   - **Postgres**: localhost:15432
     - Username: `postgres`
     - Password: `postgres`
     - Database: `postgres`

### Running the DAG

1. Open the Airflow UI at http://localhost:18081
2. Find the `simple_dbt_cosmos_dag` DAG
3. Unpause it (toggle switch on the left)
4. Trigger it manually or wait for the schedule

### Verifying Results

After the DAG runs successfully, you can query the created tables through Trino:

**Using Trino CLI:**
```bash
trino --server http://localhost:18080 --user admin
```

Then run:
```sql
SELECT * FROM postgres.public.customers;
SELECT * FROM postgres.public.first_customer;
```

**Using Trino Web UI:**
1. Go to http://localhost:18080
2. Execute: `SELECT * FROM postgres.public.customers;`

**Note:** The tables are created in Trino's `postgres.public` schema (catalog.schema), not directly in Postgres. Trino acts as the query layer.

## Key Files

### `airflow/dags/utils/dbt_utils.py`

Contains utility functions for creating dbt TaskGroups with Cosmos:
- `TrinoUserProfileMapping` - Custom profile mapping class that maps Airflow HTTP connections to dbt Trino profiles
- `run_dbt_project()` - Main function to create a dbt TaskGroup for a given project path

The profile mapping:
- Reads from Airflow HTTP connection (`trino_test`)
- Extracts `database` from connection's `extra` field
- Maps connection parameters to dbt profile dynamically

### `airflow/dags/simple_dbt_dag.py`

Simple Airflow DAG that:
- Uses `run_dbt_project()` from `dbt_utils`
- Runs all dbt models in the `dbt_project_example` project
- Connects to Trino via the mapped profile

### `airflow/dbt_projects/dbt_project_example/`

dbt project containing:
- `profiles.yml` - dbt profile configuration (uses `method: none` for no authentication)
- `models/customers.sql` - Creates a customers table with sample data
- `models/first_customer.sql` - Creates a table with the first customer's name
- `models/schema.yml` - Model documentation and tests

**Note:** Models are materialized as `tables` (not views) because Trino's PostgreSQL connector doesn't support creating views.

## Services

- **Postgres** (port 15432): Source database
  - Username: `postgres`
  - Password: `postgres`
  - Database: `postgres`
- **Trino** (port 18080): Query engine connecting to Postgres
  - No authentication required (local development)
  - Web UI: http://localhost:18080
  - Connects to Postgres via catalog configuration
- **Airflow Webserver** (port 18081): Airflow UI
  - Username: `admin`
  - Password: `admin`
- **Airflow Scheduler**: Runs DAGs
- **Airflow Init**: Initializes database and creates connections

## Connections

The project creates an Airflow HTTP connection named `trino_test`:
- **Type**: `http`
- **Host**: `trino` (service name)
- **Port**: `8080` (internal port)
- **Login**: `admin`
- **Schema**: `public`
- **Extra**: `{"database": "postgres"}`

This connection is automatically created during `airflow-init` and is used by the `TrinoUserProfileMapping` to generate dbt profiles dynamically.

## Connecting to Trino

### From your local machine:

**Using Trino CLI:**
```bash
trino --server http://localhost:18080 --user admin
```

**Using JDBC URL:**
```
jdbc:trino://localhost:18080/postgres/public
```

**Using Python (trino library):**
```python
from trino.dbapi import connect

conn = connect(
    host='localhost',
    port=18080,
    user='admin',
    catalog='postgres',
    schema='public'
)
```

**Using dbt:**
The connection is configured in `airflow/dbt_projects/dbt_project_example/profiles.yml`

### From inside Docker containers:
- Host: `trino` (service name)
- Port: `8080` (internal port)
- User: `admin`
- Password: (empty, no authentication)

## Customization

### Adding More dbt Models

1. Add SQL files to `airflow/dbt_projects/dbt_project_example/models/`
2. Update `airflow/dbt_projects/dbt_project_example/models/schema.yml` with model documentation
3. The DAG will automatically pick up new models

### Modifying Connections

The Trino HTTP connection is automatically created during initialization in `docker-compose.yml`. To modify:
- Edit the `airflow connections add` command in `docker-compose.yml` (airflow-init service)
- Or use the Airflow UI: Admin → Connections → Edit `trino_test`

### Changing Trino Database

Update the `database` value in the connection's `extra` field:
- In `docker-compose.yml`: Change `--conn-extra '{"database": "postgres"}'`
- Or in Airflow UI: Edit connection → Extra → `{"database": "your_database"}`

## Technical Details

### dbt Profile Mapping

The `TrinoUserProfileMapping` class:
- Maps Airflow HTTP connections to dbt Trino profiles
- Reads `database` from connection's `extra` field
- Supports both `profile` (runtime) and `mock_profile` (DAG parsing) methods
- Automatically handles required fields like `database`, `host`, `user`, `schema`

### Docker Setup

- **Custom Dockerfile**: Extends `apache/airflow:2.10.0` and installs:
  - `astronomer-cosmos[trino]` in main environment
  - dbt packages in virtual environment (`/opt/airflow/dbt_venv`)
- **dbt executable**: Located at `/opt/airflow/dbt_venv/bin/dbt`
- **Ports**: Random ports (18080, 18081, 15432) to avoid conflicts

## Troubleshooting

### Services won't start
- Check if ports 15432, 18080, 18081 are available
- Ensure Docker has enough resources allocated
- Check logs: `docker-compose logs <service-name>`

### DAG not appearing
- Check `docker-compose logs airflow-scheduler` for errors
- Verify DAG file is in `airflow/dags/` directory
- Check for Python syntax errors or import issues

### Trino connection issues
- Verify Trino is running: `docker-compose ps trino`
- Check Trino logs: `docker-compose logs trino`
- Verify Postgres is accessible from Trino
- Check Airflow connection: Admin → Connections → `trino_test`

### dbt errors
- Verify dbt is installed: Check `/opt/airflow/dbt_venv/bin/dbt` exists
- Check dbt project structure: Ensure `dbt_project.yml` and `profiles.yml` are correct
- Check logs for profile generation errors
- Verify `database` field is present in generated profiles.yml

### "database is a required property" error
- Ensure `database` is in the connection's `extra` field
- Check that `TrinoUserProfileMapping` includes `database` in the profile
- Verify the profile mapping is correctly reading from the connection

## Clean Up

```bash
docker-compose down -v
```

This removes all containers and volumes.

## License

MIT
