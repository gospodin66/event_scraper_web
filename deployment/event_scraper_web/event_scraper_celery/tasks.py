import datetime
import tempfile
import zipfile
from celery import Celery
from paramiko import SSHClient, AutoAddPolicy
from kafka import KafkaProducer
import json
import os
from minio import Minio

app = Celery('tasks')
app.config_from_object('celeryconfig')

# SSH Configuration (replace with your actual credentials or use environment variables for security)
REMOTE_HOST = os.getenv("REMOTE_HOST", "scraper")
USERNAME = os.getenv("USERNAME", "scraper")
PASSWORD = os.getenv("PASSWORD", "scraper123") # same password set in scraper Dockerfile 
PORT = os.getenv("PORT", 30022)

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio.eventscraper.svc.cluster.local:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "bucket-scraper-tasks")

def on_send_success(record_metadata):
    print(f"Message sent to Kafka topic {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")

def on_send_error(excp):
    print(f"Error sending message: {excp}")


@app.task(bind=True)
def run_scraper_task(self):
    try:
        print("Initializing Kafka Producer..")
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("BOOTSTRAP_SERVERS", "kafka.eventscraper.svc.cluster.local:9092"),
            value_serializer=lambda m: json.dumps(m).encode('utf-8'),
            request_timeout_ms=60000,
            retries=5,
            api_version_auto_timeout_ms=10000 
        )

        print("Connecting to the event scraper node and executing scraper script...")
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(REMOTE_HOST, username=USERNAME, password=PASSWORD, port=PORT)
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 /app/init.py")
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        if error:
            raise Exception(f"Scraper failed with error: {error}")
        
        print("Parsing output..")
        events = []
        venues = [section for section in output.split('\n\n') if ':' in section and 'Script' not in section]
        for venue in venues:           
            venue_name, *event_lines = venue.split(':\n')

            for event in event_lines:
                for evt in event.split('\n'):
                    e = evt.split(' :: ')
                    events.append({
                        'venue': venue_name,
                        'name': e[0],
                        'where': e[1],
                        'when': e[2],
                        'link': e[3],
                    } if len(e) > 1 else {
                        "venue": venue_name,
                        'name': e[0]
                    })

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        file_basename = f"events_{timestamp}"

        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = os.path.join(tmpdir, f"{file_basename}.txt")

            print(f"Creating temp dir and writing scraped events to {txt_path} file")
            with open(txt_path, 'w') as f:
                for event in events:
                    f.write(json.dumps(event, indent=2) + "\n")
            
            zip_path = os.path.join(tmpdir, f"{file_basename}.zip")

            print(f"Zipping the {txt_path} file to {zip_path}")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(txt_path, arcname=os.path.basename(txt_path))

            minio_client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=False
            )
            print(f"Uploading file {zip_path} to MinIO...")

            if not minio_client.bucket_exists(MINIO_BUCKET):
                minio_client.make_bucket(MINIO_BUCKET)

            minio_client.fput_object(
                MINIO_BUCKET,
                os.path.basename(zip_path),
                zip_path,
                content_type="application/zip"
            )

        f_dest_path = f"/{MINIO_BUCKET}/{os.path.basename(zip_path)}"

        print(f"Sending {f_dest_path} bucket path to Kafka...")

        producer.send('scraped_data', {
            "task_id": self.request.id,
            "file_path": f_dest_path,
        }).add_callback(on_send_success).add_errback(on_send_error)
        
        producer.flush() 

        return {
            "task_id": self.request.id,
            'status': 'SUCCESS',
            "file_path": f_dest_path,
            'error': error if error else None
        }
        
    except Exception as e:
        return {
            "task_id": self.request.id,
            'status': 'ERROR',
            'error': str(e)
        }
