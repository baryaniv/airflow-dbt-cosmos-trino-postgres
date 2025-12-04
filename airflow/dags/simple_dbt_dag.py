"""
Simple Airflow DAG showcasing dbt with Astronomer Cosmos
Connects to Trino which is connected to Postgres
"""
from datetime import datetime
from airflow import DAG
from utils.dbt_utils import run_dbt_project
from airflow.operators.dummy import DummyOperator
# DAG configuration
with DAG(
    dag_id="simple_dbt_cosmos_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["dbt", "cosmos", "trino"],
) as dag:
    
    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")
    # Run dbt project - just pass the project directory path
    dbt_task = run_dbt_project("/opt/airflow/dbt_projects/dbt_project_example")

    start >> dbt_task >> end

