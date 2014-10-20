#!/bin/bash
PATH=`dirname $0`
# worker进程数
WORKER_COUNT=4

Start(){
	# 1. 启动 uwsgi
	/usr/bin/uwsgi $PATH/nuri/uwsgi.ini
	
	# 2. 启动 celery beat 服务
	/usr/bin/nohup /usr/bin/python $PATH/manage.py celery beat -s /var/log/nuri/celerybeat-schedule --logfile=/var/log/nuri/celerybeat.log &
	# 3. 启动 celery worker
	/usr/bin/nohup /usr/bin/python $PATH/manage.py celery worker --concurrency=$WORKER_COUNT --logfile=/var/log/nuri/celery.log -l info &
}

Start


