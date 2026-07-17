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
    'silver_to_gold',
    default_args=default_args,
    description='DAG 3: Compute aggregated business marts from Silver to Gold Delta',
    schedule_interval=None,
    catchup=False,
    tags=['gold', 'mart'],
) as dag:

    run_gold_job = BashOperator(
        task_id='run_silver_to_gold_spark',
        bash_command='python /opt/airflow/spark_jobs/silver_to_gold_job.py',
        env={
            'MINIO_ENDPOINT': 'http://minio:9000',
            'AWS_ACCESS_KEY_ID': 'minioadmin',
            'AWS_SECRET_ACCESS_KEY': 'minioadmin',
        }
    )

    trigger_dq = TriggerDagRunOperator(
        task_id='trigger_data_quality_checks',
        trigger_dag_id='data_quality_checks',
    )

    run_gold_job >> trigger_dq
