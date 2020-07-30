"""Includes functions for interacting with S3 buckets."""
import boto3
from pathlib import Path
import sys
import os
from collections import deque


def upload_file(file_name, bucket_name):
    """Uploads <file_name> to S3 bucket <bucket_name>."""
    object_name = file_name
    s3 = boto3.client("s3")

    try:
        response = s3.upload_file(file_name, bucket_name, object_name)
    except Exception as e:
        return e

    return response


def get_download_dir():
    home = str(Path(sys.executable).home())
    paths = deque()
    paths.append(home)
    while True:
        path = paths.popleft()
        for directory in os.listdir(path):
            if directory == "Downloads":
                return os.path.join(home, path) + "/Downloads"
            else:
                new_path = os.path.join(path, directory)
                if os.path.isdir(new_path):
                    paths.append(new_path)


def download_file(file_name, bucket_name):
    """Downloads <file_name> from S3 bucket <bucket_name>."""
    s3 = boto3.client("s3")
    path_to_downloads = get_download_dir()
    output = f"{path_to_downloads}/{file_name}"

    try:
        file = s3.get_object(Bucket=bucket_name, Key=file_name)["Body"].read()
    except Exception as e:
        return e

    return file


def list_files(bucket_name):
    """Lists files in S3 bucket <bucket_name>."""
    s3 = boto3.client("s3")
    files = []

    try:
        for item in s3.list_objects(Bucket=bucket_name)["Contents"]:
            files.append(item)
    except KeyError:
        pass

    return files
