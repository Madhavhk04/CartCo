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
    'bronze_to_silver',
    default_args=default_args,
    description='DAG 2: Cleansing, standardization, and validation from Bronze to Silver Delta',
    schedule_interval=None,  # Triggered by ingest_sources or run manually
    catchup=False,
    tags=['silver', 'transform'],
) as dag:

    run_silver_job = BashOperator(
        task_id='run_bronze_to_silver_spark',
        bash_command='python /opt/airflow/spark_jobs/bronze_to_silver_job.py',
        env={
            'MINIO_ENDPOINT': 'http://minio:9000',
            'AWS_ACCESS_KEY_ID': 'minioadmin',
            'AWS_SECRET_ACCESS_KEY': 'minioadmin',
            'DQ_REPORT_DIR': '/opt/airflow/data/dq_reports',
        }
    )

    trigger_gold = TriggerDagRunOperator(
        task_id='trigger_silver_to_gold',
        trigger_dag_id='silver_to_gold',
    )

    run_silver_job >> trigger_gold
