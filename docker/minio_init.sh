#!/bin/sh
# Wait for MinIO to start
echo "Waiting for MinIO..."
sleep 5

# Set connection alias using mc (MinIO Client)
# Default admin credentials are used: minioadmin / minioadmin
mc alias set localminio http://minio:9000 minioadmin minioadmin

# Create target bucket for Delta Lake
mc mb localminio/lakehouse

# Set policy to download for anonymous reads (useful for reports and web page views)
mc anonymous set download localminio/lakehouse

echo "MinIO buckets 'lakehouse' created and configured!"
exit 0
