from os import getenv

RABBITMQ_USER = getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = getenv('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_HOST = getenv('RABBITMQ_HOST', '127.0.0.1')
# Kubernetes is injecting the full service URL instead of just the port number
# Handle both plain port numbers and full TCP URLs
raw_port = getenv('RABBITMQ_PORT', '5672')
RABBITMQ_PORT = int(raw_port.split(':')[-1]) if 'tcp://' in raw_port else int(raw_port)

broker_url = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//'
result_backend = 'rpc://'

# Broker connection retry settings
broker_connection_retry = True
broker_connection_retry_on_startup = True
broker_connection_max_retries = 10
broker_connection_timeout = 30

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True

# Task execution settings
task_track_started = True
task_time_limit = 300 
task_soft_time_limit = 240 

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 50

# Queue settings
task_default_queue = 'scraper_tasks'
task_queues = {
    'scraper_tasks': {
        'binding_key': 'scraper.#'
    }
}