# Terraform Configuration for CartCo Unified Commerce Lakehouse

terraform {
  required_version = ">= 1.2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ----------------------------------------------------
# 1. Network & VPC Security Groups
# ----------------------------------------------------
resource "aws_security_group" "lakehouse_sg" {
  name        = "cartco-lakehouse-security-group"
  description = "Security group for Airflow, Postgres RDS and EMR clusters"
  
  ingress {
    description = "Allow inbound PostgreSQL traffic"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow inbound HTTP for UI components"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Project     = "CartCo-Lakehouse"
  }
}

# ----------------------------------------------------
# 2. S3 Object Storage (Delta Lake Medallion Bucket)
# ----------------------------------------------------
resource "aws_s3_bucket" "lakehouse_bucket" {
  bucket        = "cartco-lakehouse-storage-${var.environment}"
  force_destroy = true

  tags = {
    Environment = var.environment
    Project     = "CartCo-Lakehouse"
  }
}

resource "aws_s3_bucket_public_access_block" "lakehouse_s3_lockdown" {
  bucket = aws_s3_bucket.lakehouse_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "lakehouse_versioning" {
  bucket = aws_s3_bucket.lakehouse_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ----------------------------------------------------
# 3. Relational DB (RDS PostgreSQL for Airflow/Marquez)
# ----------------------------------------------------
resource "aws_db_instance" "metadata_db" {
  identifier             = "cartco-metadata-db"
  allocated_storage      = 20
  db_name                = "cartco_metadata"
  engine                 = "postgres"
  engine_version         = "13"
  instance_class         = "db.t3.micro"
  username               = var.db_username
  password               = var.db_password
  vpc_security_group_ids = [aws_security_group.lakehouse_sg.id]
  skip_final_snapshot    = true

  tags = {
    Environment = var.environment
    Project     = "CartCo-Lakehouse"
  }
}

# ----------------------------------------------------
# 4. IAM Roles & Policies for EMR/Spark S3 Access
# ----------------------------------------------------
resource "aws_iam_role" "emr_execution_role" {
  name = "cartco-emr-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "elasticmapreduce.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3_access_policy" {
  name = "cartco-emr-s3-policy"
  role = aws_iam_role.emr_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.lakehouse_bucket.arn,
          "${aws_s3_bucket.lakehouse_bucket.arn}/*"
        ]
      }
    ]
  })
}

# ----------------------------------------------------
# 5. Streaming Source Infrastructure (Managed Kafka / MSK)
# ----------------------------------------------------
resource "aws_msk_cluster" "kafka_source" {
  cluster_name           = "cartco-pos-kafka-stream"
  kafka_version          = "2.8.1"
  number_of_broker_nodes = 2

  broker_node_group_info {
    instance_type = "kafka.t3.small"
    client_subnets = var.subnet_ids
    security_groups = [aws_security_group.lakehouse_sg.id]
    
    connectivity_info {
      public_access {
        type = "DISABLED"
      }
    }
  }

  tags = {
    Environment = var.environment
    Project     = "CartCo-Lakehouse"
  }
}
