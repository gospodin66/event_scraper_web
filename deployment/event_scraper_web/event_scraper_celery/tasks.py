from celery import Celery
from paramiko import SSHClient, AutoAddPolicy

app = Celery('tasks')
app.config_from_object('celeryconfig')

# SSH Configuration (replace with your actual credentials or use environment variables for security)
REMOTE_HOST = "scraper"
USERNAME = "scraper"
PASSWORD = "scraper123" # same password set in scraper Dockerfile 
PORT = 30022

@app.task(bind=True)
def run_scraper_task(self):
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(REMOTE_HOST, username=USERNAME, password=PASSWORD, port=PORT)
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 /app/init.py")
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        if error:
            raise Exception(f"Scraper failed with error: {error}")
        
        output = output.split('\n\n', 1)[1] if '\n\n' in output else output
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
