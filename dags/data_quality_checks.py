from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

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
    'data_quality_checks',
    default_args=default_args,
    description='DAG 4: Run standalone Great Expectations checks and validation reports',
    schedule_interval=None,
    catchup=False,
    tags=['dq', 'quality'],
) as dag:

    run_dq_job = BashOperator(
        task_id='run_standalone_dq_spark',
        bash_command='python /opt/airflow/spark_jobs/run_standalone_dq.py',
        env={
            'MINIO_ENDPOINT': 'http://minio:9000',
            'AWS_ACCESS_KEY_ID': 'minioadmin',
            'AWS_SECRET_ACCESS_KEY': 'minioadmin',
            'DQ_REPORT_DIR': '/opt/airflow/data/dq_reports',
        }
    )

    run_optimize_job = BashOperator(
        task_id='run_delta_optimizations',
        bash_command='python /opt/airflow/spark_jobs/optimize_lakehouse.py',
        env={
            'MINIO_ENDPOINT': 'http://minio:9000',
            'AWS_ACCESS_KEY_ID': 'minioadmin',
            'AWS_SECRET_ACCESS_KEY': 'minioadmin',
        }
    )

    run_catalog_job = BashOperator(
        task_id='run_catalog_registry',
        bash_command='python /opt/airflow/spark_jobs/register_catalog.py',
        env={
            'MINIO_ENDPOINT': 'http://minio:9000',
            'AWS_ACCESS_KEY_ID': 'minioadmin',
            'AWS_SECRET_ACCESS_KEY': 'minioadmin',
        }
    )

    run_dq_job >> run_optimize_job >> run_catalog_job


