---
name: cloud
description: Amazon Web Services (AWS) S3 storage operations.
allowed-tools:
  - s3_list_buckets
  - s3_create_bucket
  - s3_upload_file
  - s3_download_file
  - s3_list_objects
  - s3_delete_object
---

# Cloud Skill

This skill enables the agent to interact with AWS S3 (Simple Storage Service) for cloud storage operations.

## Prerequisites

- AWS account with S3 access
- AWS credentials configured via environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) or AWS configuration files.

## Tools

### s3_list_buckets
List all S3 buckets in the account.

### s3_create_bucket
Create a new S3 bucket.
- `bucket_name`: Name of the bucket (must be globally unique).
- `region`: AWS region (optional, default 'us-east-1').

### s3_upload_file
Upload a local file to S3.
- `bucket_name`: Target bucket.
- `file_path`: Local path to the file.
- `object_key`: Key (path) for the object in S3.

### s3_download_file
Download a file from S3 to local.
- `bucket_name`: Source bucket.
- `object_key`: Key of the object.
- `output_path`: Local path to save the file.

### s3_list_objects
List objects in a bucket, optionally with prefix.
- `bucket_name`: Bucket to list.
- `prefix`: Prefix filter (optional).

### s3_delete_object
Delete an object from S3.
- `bucket_name`: Bucket containing the object.
- `object_key`: Key of the object to delete.
