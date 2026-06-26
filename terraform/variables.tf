# Variables definition for CartCo Infrastructure

variable "aws_region" {
  type        = string
  description = "The target AWS region to deploy resources"
  default     = "ap-south-1"
}

variable "environment" {
  type        = string
  description = "Execution environment naming tag"
  default     = "prod"
}

variable "db_username" {
  type        = string
  description = "Database administrator username"
  default     = "postgres"
}

variable "db_password" {
  type        = string
  description = "Database administrator password (use Secrets Manager in production)"
  default     = "CartCoPassSecure2026!"
  sensitive   = true
}

variable "subnet_ids" {
  type        = list(string)
  description = "VPC subnets for the Kafka brokers"
  default     = ["subnet-0123456789abcdef0", "subnet-0123456789abcdef1"]
}
