from celery import Celery
from paramiko import SSHClient, AutoAddPolicy
from kafka import KafkaProducer
import json
import os

app = Celery('tasks')
app.config_from_object('celeryconfig')

# SSH Configuration (replace with your actual credentials or use environment variables for security)
REMOTE_HOST = "scraper"
USERNAME = "scraper"
PASSWORD = "scraper123" # same password set in scraper Dockerfile 
PORT = 30022

def on_send_success(record_metadata):
    print(f"Message sent to Kafka topic {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")

def on_send_error(excp):
    print(f"Error sending message: {excp}")


@app.task(bind=True)
def run_scraper_task(self):
    try:
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("BOOTSTRAP_SERVERS", "kafka.eventscraper.svc.cluster.local:9092"),
            value_serializer=lambda m: json.dumps(m).encode('utf-8'),
            request_timeout_ms=60000,
            retries=5,
            api_version_auto_timeout_ms=10000 
        )
        
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(REMOTE_HOST, username=USERNAME, password=PASSWORD, port=PORT)
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 /app/init.py")
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        if error:
            raise Exception(f"Scraper failed with error: {error}")
        
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

        producer.send('scraped_data', {
            "task_id": run_scraper_task.request.id,
            "result": events
        }).add_callback(on_send_success).add_errback(on_send_error)
        
        producer.flush() 

        return {
            'status': 'SUCCESS',
            'events': events,
            'error': error if error else None
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e)
        }
