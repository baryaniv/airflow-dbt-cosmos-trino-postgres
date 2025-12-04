FROM apache/airflow:2.10.0

WORKDIR /opt/airflow

USER root
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /opt/airflow/requirements.txt

RUN pip install --upgrade pip \
  && pip install --no-cache-dir astronomer-cosmos[trino]>=1.8.0

RUN python -m venv dbt_venv \
  && source dbt_venv/bin/activate \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r /opt/airflow/requirements.txt