from flask_socketio import SocketIO
from kafka import KafkaConsumer
import json
from time import sleep
import threading
import os
from flask import Flask
import logging

from minioclient import MinioClient

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "scraped_data")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")


class KafkaClient:

    def __init__(self, app: Flask):
        self.logger = logging.getLogger(__name__)
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id="flask-group"
        )
        self.minioclient = MinioClient()

    
    def start_kafka_consumer(self):
        """
        Start kafka listener thread
        """
        thread = threading.Thread(target=self.consume_messages)
        thread.daemon = True
        thread.start()


    def consume_messages(self):
        """
        Run in a separate thread to consume Kafka messages and emit them via WebSocket.
        """
        while True:
            msg_pack = self.consumer.poll(timeout_ms=1000)
            if not msg_pack:
                sleep(1)
                continue

            for topic_partition, messages in msg_pack.items():
                for message in messages:
                    self.logger.info(f"Received Kafka message: {message.value}")
                    file_info = message.value
                    try:
                        task_id = file_info.get("task_id")
                        file_path = file_info.get("file_path")  # e.g., "/bucket-scraper-tasks/events_20250420.zip"

                        self.logger.info(f"File path received: {task_id}, {file_path}",)

                        if not file_path:
                            self.logger.error("No file path in Kafka message.")
                            continue

                        events = self.minioclient.process_file_from_minio(file_path=str(file_path.split("/")[-1]))
                        self.logger.info(f"Emitted Kafka message to websocket: {events}")
                        kafka_message = {
                            "status": "processed", 
                            "task_id": task_id, 
                            "result": events
                        }

                    except Exception as e:
                        self.logger.error(f"Error processing Kafka message: {str(e)}")
                        kafka_message = {
                            "status": "error",
                            "task_id": task_id,
                            "error": str(e)
                        }

                    self.socketio.emit("kafka_message", kafka_message)
