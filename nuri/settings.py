# -*- coding:utf-8 -*-
# Django settings for nuri project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
HERE = os.path.dirname(os.path.dirname(__file__))
#print HERE
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nuri',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'root',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(HERE, 'media').replace('\\','/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(HERE, 'static').replace('\\','/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(HERE,'static/develop/').replace('\\','/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'aup47ns$^=ec2uvcp6@i#a!w=6%h@%c690)=$980wpvy!q=ar6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'nuri.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'nuri.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(HERE,'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'djcelery',
    'django.contrib.admin',
    'common',
    'appitem',
    'monitoritem',
    'dynamicconfig',
    'log',
    'authority',
    'account',
    'role',
    'shownode',
    'message',
    'notification',
    'urlinfo',
    'tcpinfo',
    'nocip',
    'monitorindex',
    'hostalive',
    'business',
    'hostgroup',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {

            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/nuri/all.log', #或者直接写路径：'c://logs/all.log',
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'notify': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/nuri/notify.log', #或者直接写路径：'c://logs/all.log',
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'django.notify': {
            'handlers': ['notify'],
            'level': 'INFO',
            'propagate': True
        },
    }
}             

# The URL where requests are redirected for login, especially when using the login_required() decorator.
# 登录页URL 
LOGIN_URL = "/loginpage"

# 设置 用户关闭浏览器，则session失效
SESSION_EXPIRE_AT_BROWSER_CLOSE = "true"

# 会话ID在cookie中的名称
SESSION_COOKIE_NAME = "nuri_sessionid"

# CSRF token在cookie 中的名称
CSRF_COOKIE_NAME = "nuri_csrftoken"

# session 的失效时间
SESSION_COOKIE_AGE = 4*60*60

# 使用本地内存作为cache
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#        'LOCATION': 'unique-snowflake'
#    }}
    
# session 引擎 
#SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# 节点控制级别
CONTROL_LEVEL = 3

# -------------　邮件发送 --------------------
# smtp 服务器用户名
MAIL_USER = "test"

# smtp 服务器密码
MAIL_PASSWORD = "test"

# 邮件服务器
MAIL_SERVER = "smtp.company.com"


# -------------- 短信发送 ------------------
# *** 注意短信内容必须是GBK编码 ***
# 短信通道用户名
SMS_USER = "test"

# 短信通道密码
SMS_PASSWORD = "test"

# 短信服务器
SMS_SERVER = "10.13.35.134"

# 端口
SMS_PORT = 443

# servlet_url 
SERVLET_URL = "/smmp"


# ------------  redis --------------------
import redis
from redis.connection import BlockingConnectionPool
# redis 连接池
REDIS_HOST = '10.2.161.15'
REDIS_PORT = 6379
# Redis 访问密码
REDIS_PASSWORD = 'N6MXWf'
REDIS_DB_NUM = 0

# redis数据库
# 显式使用连接池
# 阻塞式连接池
pool = BlockingConnectionPool(max_connections=20, timeout=5, socket_timeout=5, \
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_NUM, password=REDIS_PASSWORD)
REDIS_DB = redis.StrictRedis(connection_pool=pool)


# ------------  异步框架Celery相关参数 --------------------
# celery命令行工具本身是不支持以daemon方式运行
# 可以使用nohup 或　Supervisord 进行管理
# nohup python manage.py celery worker --concurrency=4 --logfile=/var/log/nuri/celery.log -l info &
# nohup python manage.py celery beat -s /var/log/nuri/celerybeat-schedule --logfile=/var/log/nuri/celerybeat.log  &  
# 如需以指定用户执行
# nohup python manage.py celery worker --concurrency=4 --logfile=/var/log/nuri/celery.log -l info  --uid=panda &
# nohup python manage.py celery beat -s /var/log/nuri/celerybeat-schedule --logfile=/var/log/nuri/celerybeat.log  --uid=panda &
# ------------------------------------------------------

import djcelery
from celery.schedules import crontab
from datetime import timedelta
djcelery.setup_loader()

# 某个程序中出现的队列，在broker中不存在，则立刻创建它
CELERY_CREATE_MISSING_QUEUES = True

# 单次回写，最大回写数量
MAX_RETURN_COUNT = 200

# 在单个任务中, 最大回写数量
TASK_MAX_WRITEBACK = 20000

CELERY_IMPORTS = ("monitorpoint.models", "message.models", "other.models", 
    "notification.models", "monitorindex.models", "hostalive.models", "notify.models")

# 使用redis 作为任务队列
BROKER_URL = 'redis://:N6MXWf@10.2.161.15:6379/0'

CELERY_TIMEZONE = 'Asia/Shanghai'

# 定时器
CELERYBEAT_SCHEDULE = {
    # 监控点数据回写
    'point_data_writeback': {
        'task': 'monitorpoint.models.point_data_writeback',
        'schedule': timedelta(seconds=3),
    },
    # 消息回写
    'message_writeback': {
        'task': 'message.models.message_writeback',
        'schedule': timedelta(seconds=60),
    },
    # 通知自动回写
    'notification_writeback': {
        'task': 'notification.models.notification_writeback',
        'schedule': timedelta(seconds=60),
    },
    # 通知自动回写
    'host_event_writeback': {
        'task': 'notification.models.host_event_writeback',
        'schedule': timedelta(seconds=120),
    },
    # 主机自动发现
    'host_auto_find': {
        'task': 'other.models.host_auto_find',
        'schedule': timedelta(seconds=300),
    },
    # 检查主机存活性
    'check_host_alive': {
        'task': 'hostalive.models.check_host_alive',
        'schedule': timedelta(seconds=60),
    },
    # 监控健康指数计算
    'monitor_index_calculate': {
        'task': 'monitorindex.models.monitor_index_calculate',
        'schedule': crontab(hour=0, minute=30),
    },
}

# ---------------- 以下函数也是异步执行的 ------------
# 1) 主机报警
# notify.models.notify_host
# 2) 应用报警
# notify.models.notify_app




