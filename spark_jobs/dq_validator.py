import os
import json
from datetime import datetime
from great_expectations.dataset.sparkdf_dataset import SparkDFDataset

def validate_dataframe(df, table_name, rules):
    """
    Validates a PySpark DataFrame using Great Expectations SparkDFDataset.
    rules is a list of dicts specifying expectations.
    """
    print(f"Running Data Quality checks for {table_name}...")
    ge_dataset = SparkDFDataset(df)
    
    for rule in rules:
        exp_type = rule.get("type")
        column = rule.get("column")
        args = rule.get("args", {})
        
        if exp_type == "unique":
            ge_dataset.expect_column_values_to_be_unique(column)
        elif exp_type == "not_null":
            ge_dataset.expect_column_values_to_not_be_null(column)
        elif exp_type == "set":
            ge_dataset.expect_column_values_to_be_in_set(column, args.get("value_set"))
        elif exp_type == "min":
            ge_dataset.expect_column_values_to_be_between(column, min_value=args.get("min_value"))
        elif exp_type == "max_value":
            ge_dataset.expect_column_values_to_be_between(column, max_value=args.get("max_value"))
            
    validation_result = ge_dataset.validate()
    
    # Save validation results summary
    report = parse_validation_results(table_name, validation_result)
    save_dq_report(table_name, report)
    
    return report

def parse_validation_results(table_name, results):
    """
    Parses Great Expectations results object into a simple SaaS-style report schema.
    """
    stats = results.get("statistics", {})
    evaluated_expectations = results.get("results", [])
    
    checks = []
    for eval_res in evaluated_expectations:
        success = eval_res.get("success")
        expectation_config = eval_res.get("expectation_config", {})
        method = expectation_config.get("expectation_type")
        kwargs = expectation_config.get("kwargs", {})
        
        # Human readable description
        column = kwargs.get("column", "table-level")
        desc = f"Check {column} using {method}"
        if "value_set" in kwargs:
            desc += f" (values: {kwargs['value_set']})"
        elif "min_value" in kwargs:
            desc += f" (>= {kwargs['min_value']})"
            
        checks.append({
            "expectation": method,
            "column": column,
            "success": success,
            "description": desc,
            "observed_value": eval_res.get("result", {}).get("observed_value")
        })
        
    return {
        "table_name": table_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success": results.get("success", False),
        "evaluated_expectations": stats.get("evaluated_expectations", 0),
        "successful_expectations": stats.get("successful_expectations", 0),
        "failed_expectations": stats.get("unsuccessful_expectations", 0),
        "percent_success": round(stats.get("success_percent", 0.0), 2),
        "details": checks
    }

def save_dq_report(table_name, report):
    # Output to a shared volume directory where Streamlit and Airflow can both access it
    report_dir = os.getenv("DQ_REPORT_DIR", "/opt/airflow/data/dq_reports")
    # Try to create the directory; fallback to local if there is a permission error or it's unavailable
    try:
        os.makedirs(report_dir, exist_ok=True)
    except Exception:
        report_dir = os.path.join(os.getcwd(), "data", "dq_reports")
        os.makedirs(report_dir, exist_ok=True)
        
    report_path = os.path.join(report_dir, f"{table_name}_dq_report.json")
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
    print(f"Data quality report saved to {report_path}")
