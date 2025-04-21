from minio import Minio
import zipfile
import tempfile
import os
import json
from logging import getLogger

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio.eventscraper.svc.cluster.local:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "bucket-scraper-tasks")

class MinioClient():
    def __init__(self):
        self.logger = getLogger(__name__)
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )


    def process_file_from_minio(self, file_path: str) -> list:
        """
        Download a file from MinIO, extract its contents, and save the events to the database.
        """
        self.logger.info(f"Downloading file from MinIO bucket {MINIO_BUCKET}: {file_path}")
        result = []

        with tempfile.TemporaryDirectory() as tmpdir:

            zip_path = os.path.join(tmpdir, os.path.basename(file_path))
            self.client.fget_object(MINIO_BUCKET, os.path.basename(file_path), zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for name in zipf.namelist():
                    with zipf.open(name) as file:
                        raw_string = file.read().decode('utf-8')

                        start = raw_string.find("['") + 2
                        end = raw_string.rfind("']")
                        json_blob = raw_string[start:end]

                        parts = json_blob.split('\n}')
                        json_objects = [p + '\n}' for p in parts if p.strip()]

                        for obj_str in json_objects:
                            try:
                                event = json.loads(obj_str)
                                result.append(event)
                            except json.JSONDecodeError as e:
                                print("Skipping invalid JSON:", e)

            return result

if __name__ == '__main__': 
    c = MinioClient()
    print(c.process_file_from_minio('/bucket-scraper-tasks/events_20250421143120.zip'))
