"""Includes functions for interacting with S3 buckets."""
import boto3


def upload_file(file_name, bucket_name):
    """Uploads <file_name> to S3 bucket <bucket_name>."""
    object_name = file_name
    s3 = boto3.client('s3')

    try:
        response = s3.upload_file(file_name, bucket_name, object_name)
    except Exception as e:
        return e

    return response


def download_file(file_name, bucket_name):
    """Downloads <file_name> from S3 bucket <bucket_name>."""
    s3 = boto3.client('s3')
    output = f"downloads/{file_name}"

    try:
        s3.download_file(bucket_name, file_name, file_name)
    except Exception as e:
        return e

    return output


def list_files(bucket_name):
    """Lists files in S3 bucket <bucket_name>."""
    s3 = boto3.client('s3')
    files = []

    try:
        for item in s3.list_objects(Bucket=bucket_name)['Contents']:
            files.append(item)
    except KeyError:
        pass

    return files
