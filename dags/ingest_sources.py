from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    'owner': 'cartco_de',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'ingest_sources',
    default_args=default_args,
    description='DAG 1: Generate synthetic commerce data and ingest raw CSVs to Bronze Delta Tables',
    schedule_interval='@daily',
    catchup=False,
    tags=['bronze', 'ingestion'],
) as dag:

    generate_data = BashOperator(
        task_id='generate_synthetic_data',
        bash_command='python /opt/airflow/spark_jobs/data_generator.py /opt/airflow/data',
    )

    ingest_to_bronze = BashOperator(
        task_id='ingest_to_bronze_delta',
        bash_command='python /opt/airflow/spark_jobs/ingest_to_bronze.py',
        env={
            'DATA_DIR': '/opt/airflow/data',
            'MINIO_ENDPOINT': 'http://minio:9000',
            'AWS_ACCESS_KEY_ID': 'minioadmin',
            'AWS_SECRET_ACCESS_KEY': 'minioadmin',
        }
    )

    trigger_silver = TriggerDagRunOperator(
        task_id='trigger_bronze_to_silver',
        trigger_dag_id='bronze_to_silver',
    )

    generate_data >> ingest_to_bronze >> trigger_silver
