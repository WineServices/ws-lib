import os

import boto3
from io import BytesIO

from fastapi.responses import StreamingResponse
from urllib.parse import quote


def get_file_object(bucket_name: str, file_path: str):
    session = boto3.Session(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )
    s3 = session.resource("s3")

    files = list(s3.Bucket(bucket_name).objects.filter(Prefix=file_path))
    assert len(files) == 1, f"Many or None files are found: {files}"

    return files[0]


def stream_file_from_s3(bucket_name: str, file_path: str):
    file_object = get_file_object(bucket_name=bucket_name, file_path=file_path)
    content = file_object.get()['Body'].read()

    stream = BytesIO(content)

    response = StreamingResponse(iter([stream.getvalue()]))
    file_name = file_path.split("/")[-1]

    content_disposition_filename = quote(file_name)
    if content_disposition_filename != file_name:
        content_disposition = "attachment; filename*=utf-8''{}".format(
            content_disposition_filename
        )
    else:
        content_disposition = f'attachment; filename="{file_name}"'

    response.headers["Content-Disposition"] = content_disposition
    return response
