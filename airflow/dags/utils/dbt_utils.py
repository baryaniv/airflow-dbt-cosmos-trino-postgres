"""
dbt_utils.py - Astronomer Cosmos integration utilities for Airflow
Uses profiles.yml from the dbt project directly.
"""
import os
from typing import Union, Any
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import BaseProfileMapping


class TrinoUserProfileMapping(BaseProfileMapping):
    """
    Maps Airflow Trino connections using user authentication to dbt profiles.
    """
    airflow_connection_type: str = "http"
    dbt_profile_type: str = "trino"
    required_fields = [
        "host",
        "user",
        "schema",
    ]

    airflow_param_mapping = {
        "host": "host",
        "user": "login",
        "schema": "schema",
        "database": "extra.database",
    }

    @property
    def profile(self) -> dict[str, Union[Any | None]]:
        """Gets profile. The password is stored in an environment variable if provided."""
        profile = {
            "type": "trino",
            "port": 8080,
            "method": "userpass",
            "threads": 1,
            **self.mapped_params,
            **self.profile_args,
        }

        filtered = self.filter_null(profile)
            
        return filtered

    @property
    def mock_profile(self) -> dict[str, Union[Any | None]]:
        """Gets mock profile for DAG parsing (used before execution)."""
        # Same as profile since we're using hardcoded values
        return self.profile


def run_dbt_project(project_path: str, group_id: str = None):
    """
    Create a dbt TaskGroup for running a dbt project using Cosmos.
    Uses profiles.yml from the dbt project.
    
    Args:
        project_path: Path to the dbt project directory
        group_id: Optional unique identifier for the task group (defaults to project folder name)
    
    Returns:
        DbtTaskGroup instance ready to use in a DAG
    """
    if group_id is None:
        group_id = os.path.basename(project_path.rstrip("/"))

    profile_config = ProfileConfig(
        profile_name="run",
        target_name="dev",
        profile_mapping=TrinoUserProfileMapping(conn_id="trino_test", profile_args={"password": ""}),
    )

    return DbtTaskGroup(
        group_id=group_id,
        project_config=ProjectConfig(dbt_project_path=project_path),
        profile_config=profile_config,
        execution_config=ExecutionConfig(dbt_executable_path="/opt/airflow/dbt_venv/bin/dbt"),
        operator_args={"append_env": False},
    )