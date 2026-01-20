"""
Cloud skill: AWS S3 operations.
Requires boto3 library.
"""

import json
import os
import uuid
from typing import Dict, Optional

import boto3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cloud", log_level="ERROR")

# S3 client reuse
_s3_client = None


def _get_s3_client():
    """Get or create S3 client."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
    return _s3_client


@mcp.tool()
def s3_list_buckets() -> str:
    """
    List all S3 buckets in the account.
    """
    try:
        client = _get_s3_client()
        response = client.list_buckets()
        buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]
        return f"Buckets: {', '.join(buckets)}" if buckets else "No buckets found."
    except Exception as e:
        return f"Error listing buckets: {e}"


@mcp.tool()
def s3_create_bucket(bucket_name: str, region: Optional[str] = "us-east-1") -> str:
    """
    Create a new S3 bucket.

    Args:
        bucket_name: Globally unique bucket name.
        region: AWS region (default 'us-east-1').
    """
    try:
        client = _get_s3_client()
        if region == "us-east-1":
            client.create_bucket(Bucket=bucket_name)
        else:
            client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        return f"Bucket '{bucket_name}' created successfully in region '{region}'."
    except Exception as e:
        return f"Error creating bucket: {e}"


@mcp.tool()
def s3_upload_file(bucket_name: str, file_path: str, object_key: str) -> str:
    """
    Upload a local file to S3.

    Args:
        bucket_name: Target bucket.
        file_path: Local file path.
        object_key: S3 object key.
    """
    try:
        client = _get_s3_client()
        client.upload_file(file_path, bucket_name, object_key)
        return f"Uploaded '{file_path}' to s3://{bucket_name}/{object_key}"
    except Exception as e:
        return f"Error uploading file: {e}"


@mcp.tool()
def s3_download_file(bucket_name: str, object_key: str, output_path: str) -> str:
    """
    Download a file from S3 to local.

    Args:
        bucket_name: Source bucket.
        object_key: S3 object key.
        output_path: Local destination path.
    """
    try:
        client = _get_s3_client()
        client.download_file(bucket_name, object_key, output_path)
        return f"Downloaded s3://{bucket_name}/{object_key} to '{output_path}'"
    except Exception as e:
        return f"Error downloading file: {e}"


@mcp.tool()
def s3_list_objects(bucket_name: str, prefix: Optional[str] = "") -> str:
    """
    List objects in a bucket.

    Args:
        bucket_name: Bucket to list.
        prefix: Prefix filter (optional).
    """
    try:
        client = _get_s3_client()
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        objects = [obj["Key"] for obj in response.get("Contents", [])]
        if objects:
            return f"Objects in '{bucket_name}':\n" + "\n".join(objects)
        else:
            return f"No objects found in '{bucket_name}' with prefix '{prefix}'."
    except Exception as e:
        return f"Error listing objects: {e}"


@mcp.tool()
def s3_delete_object(bucket_name: str, object_key: str) -> str:
    """
    Delete an object from S3.

    Args:
        bucket_name: Bucket containing the object.
        object_key: Key of the object to delete.
    """
    try:
        client = _get_s3_client()
        client.delete_object(Bucket=bucket_name, Key=object_key)
        return f"Deleted s3://{bucket_name}/{object_key}"
    except Exception as e:
        return f"Error deleting object: {e}"
