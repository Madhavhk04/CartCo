# Output parameters for CartCo Infrastructure

output "lakehouse_s3_bucket" {
  value       = aws_s3_bucket.lakehouse_bucket.id
  description = "The conformed Delta Lake S3 bucket name"
}

output "metadata_db_endpoint" {
  value       = aws_db_instance.metadata_db.endpoint
  description = "Database cluster connection string"
}

output "msk_bootstrap_brokers" {
  value       = aws_msk_cluster.kafka_source.bootstrap_brokers
  description = "Connection endpoints for the retail POS Kafka brokers"
}
