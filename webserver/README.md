#### Generate self-signed certificate & key
```bash
mkdir -p event_scraper_web/webserver/cert && cd event_scraper_web/webserver/cert

openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key
```

#### open connection with local port forwarding to access portal on VM from host
```bash
ssh -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -L 192.168.56.1:35443:10.0.2.15:35080 cheki@192.168.56.1 -p 30022 

curl -v -k https://192.168.56.1:35443/
```

##### putty opens connection on localhost
```bash
# command translation would be: 
ssh -L 127.0.0.1:35443:10.0.2.15:35080 cheki@192.168.56.1 -p 30022 

curl -v -k https://127.0.0.1:35443/
```

#### Celery
```bash
cd /home/cheki/workspace/event_scraper_web \
&& . bin/activate \
&& celery -A event_scraper_celery.tasks worker --loglevel=info -Q scraper_tasks
```

#### Gunicorn
```bash
cd /home/cheki/workspace/event_scraper_web/webserver/src \
&& . ../../bin/activate \
&& gunicorn webserver:app \
  --bind 0.0.0.0:35080 \
  --workers 2 \
  --timeout 120 \
  --keep-alive 5 \
  --log-level INFO \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --certfile=../cert/server.crt \
  --keyfile=../cert/server.key
```

#### rabbitmq (hosted in docker container)
```bash
rabbitmqctl status

# enable management plugin
rabbitmq-plugins enable rabbitmq_management

rabbitmqctl list_queues && rabbitmqctl list_exchanges && rabbitmqctl list_bindings
```