"""Functions for interacting with AWS S3."""
import boto3


def upload_file(file_name: str, bucket_name: str) -> None:
    """Uploads <file_name> to S3 bucket <bucket_name>."""
    s3 = boto3.client("s3")
    try:
        s3.upload_file(file_name, bucket_name, file_name)
    except Exception as e:
        print(e)


def download_file(file_name: str, bucket_name: str) -> bytes:
    """Downloads <file_name> from S3 bucket <bucket_name>."""
    s3 = boto3.client("s3")
    try:
        file = s3.get_object(Bucket=bucket_name, Key=file_name)["Body"].read()
    except Exception as e:
        print(e)
        return b""
    return file


def get_file_list(bucket_name: str) -> list:
    """Lists files in S3 bucket <bucket_name>."""
    s3 = boto3.client("s3")
    files = []
    try:
        for item in s3.list_objects(Bucket=bucket_name)["Contents"]:
            files.append(item)
    except KeyError:  # Bucket is empty and has no key `Contents`.
        pass

    return files
