from flask import Flask, render_template, jsonify, request
from logging import getLogger
from pathlib import Path
from queue import Queue
from sys import path
from ssl import SSLContext, PROTOCOL_TLS_SERVER, CERT_OPTIONAL
from sqlalchemy.orm import joinedload

celery_path = '/app'
path.extend([str('/app/'), str(celery_path)])
# Docker image has tasks in the same level as webserver - not an issue
from tasks import run_scraper_task
from db import Database, Event

logger = getLogger(__name__)

def verify_dir(path: Path, dir_type: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"{dir_type} directory not found: {path}")
    return str(path)


template_dir = verify_dir(Path('/app/html'), 'Template')
static_dir = verify_dir(Path('/app/static'), 'Static')
cert_dir = verify_dir(Path('/app/cert'), 'Cert')

logger.debug("Template_dir: %s", template_dir)
logger.debug("Static_dir: %s", static_dir)
logger.debug(f"Certificate: {cert_dir}/server.crt")
logger.debug(f"Certificate Key: {cert_dir}/server.key")

process_queue = Queue()
app = Flask(
    __name__, 
    template_folder=template_dir,
    static_folder=static_dir
)


context = SSLContext(PROTOCOL_TLS_SERVER)
context.verify_mode = CERT_OPTIONAL
context.load_cert_chain(certfile=f"{cert_dir}/server.crt", keyfile=f"{cert_dir}/server.key")
context.load_verify_locations(cafile="/etc/ssl/certs/ca-certificates.crt")


context.load_cert_chain(
    certfile=f"{cert_dir}/server.crt", 
    keyfile=f"{cert_dir}/server.key"
)


@app.route('/healthz')
def health():
    return jsonify({"status": "healthy"}), 200


@app.route('/')
def index():
    try:
        db_path = Path('events.sqlite')
        events = []
        if db_path.exists():
            db = Database()
            with db.get_db() as session:
                events = session.query(Event).all()
        return render_template('index.html', events=events)
    except Exception as e:
        app.logger.error(f"Failed to render template: {str(e)}")
        return f"Error loading template: {str(e)}", 500


@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    try:
        task = run_scraper_task.delay()
        return jsonify({
            'status': 'Task started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500


@app.route('/task-status/<task_id>')
def task_status(task_id):
    task = run_scraper_task.AsyncResult(task_id)
    response = {
        'state': task.state,
    }
    
    if task.state == 'SUCCESS':
        result = task.get()
        response.update({
            'status': f'Task {task_id} completed',
            'result': result
        })
        db = Database()
        db.parse_and_save_result(result)
        
    elif task.state == 'FAILURE':
        response.update({
            'status': f'Task {task_id} failed',
            'error': str(task.info)
        })
    else:
        response.update({
            'status': f'Task {task_id} in progress',
        })
    
    return jsonify(response)


@app.route('/get-hosts', methods=['GET'])
def get_hosts():
    hosts_file_path = Path('/app/.auth/.hosts.txt')
    if hosts_file_path.exists():
        with open(hosts_file_path, 'r') as file:
            hosts_content = file.read().splitlines()
        return jsonify({"hosts": hosts_content}), 200
    else:
        return jsonify({"error": "Hosts file not found"}), 404


@app.route('/update-hosts', methods=['POST'])
def update_hosts():
    data = request.get_json()
    hosts = data.get('hosts', [])
    hosts_file_path = '/app/.auth/.hosts.txt'
    if hosts:
        with open(hosts_file_path, 'w') as file: 
            for host in hosts:
                file.write(host + '\n')  
        return jsonify({"status": "Hosts updated"}), 200
    return jsonify({"status": "Error", "message": "No hosts provided"}), 400


@app.route('/get-events', methods=['GET'])
def get_events():
    try:
        db_path = Path('events.sqlite')
        events = []
        if db_path.exists():
            db = Database()
            events = db.session.query(Event).options(joinedload(Event.host)).all()
            db.session.close()
        return jsonify(
            {"status": "SUCCESS", 
             "events": [{
                "venue": event.host.name, 
                "name": event.event, 
                "when": event.when, 
                "link": event.link
            } for event in events]}
        ), 200
    except Exception as e:
        app.logger.error(f"Failed to fetch events: {str(e)}")
        return jsonify({"status": "ERROR", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(ssl_context=context)
