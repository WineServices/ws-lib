import os
from io import BytesIO
from urllib.parse import quote

import boto3
import unidecode
from fastapi.responses import StreamingResponse


def get_file_object(bucket_name: str, file_path: str):
    session = boto3.Session(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )
    s3 = session.resource("s3")

    files = list(s3.Bucket(bucket_name).objects.filter(Prefix=file_path))
    assert len(files) == 1, f"Many or None files are found: {files}"

    return files[0]


def get_file_e_tag(bucket_name: str, file_path: str):
    file = get_file_object(bucket_name, file_path)
    return file.e_tag.replace("\"", "")


def upload_to_s3(bucket_name: str, file_path: str, file_content: bytes) -> None:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )
    s3_client.put_object(Body=file_content, Bucket=bucket_name, Key=file_path)


def stream_file_from_s3(bucket_name: str, file_path: str):
    file_object = get_file_object(bucket_name=bucket_name, file_path=file_path)
    content = file_object.get()['Body'].read()
    stream = BytesIO(content)
    response = StreamingResponse(iter([stream.getvalue()]))
    file_name = file_path.split("/")[-1]

    content_disposition_filename = quote(file_name)
    if content_disposition_filename != file_name:
        content_disposition_filename_ascii = unidecode.unidecode(file_name)
        content_disposition = "attachment; filename*=utf-8''{}; filename=\"{}\"".format(
            content_disposition_filename,
            content_disposition_filename_ascii
        )
    else:
        content_disposition = f'attachment; filename="{file_name}"'

    response.headers["Content-Disposition"] = content_disposition
    response.headers["Access-Control-Expose-Headers"] = 'Content-Disposition'
    return response


def get_file_url(bucket_name: str, file_path: str):
    # make sure file exists
    get_file_object(bucket_name=bucket_name, file_path=file_path)
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )
    signed_url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            "Bucket": bucket_name,
            "Key": file_path
        }
    )
    return signed_url

