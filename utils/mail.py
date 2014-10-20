#!/usr/bin/env  python
# *-*coding:utf-8*-*
import smtplib
import logging
from email.mime.text import MIMEText
from django.conf import settings

# 发送邮件
# to_addrs --此参数可以是list或着string
def send_mail(from_addr, to_addrs, sub, content):
    logger = logging.getLogger('django.notify')
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = from_addr
    
    if isinstance(to_addrs, basestring):
        msg['To'] = to_addrs
    else:
        msg['To'] = ';'.join(to_addrs)
        
    agent_from = "<" + settings.MAIL_USER + "@autonavi.com>"
    
    try:
        server = smtplib.SMTP()
        server.connect(settings.MAIL_SERVER)
        server.login(settings.MAIL_USER, settings.MAIL_PASSWORD)
        server.sendmail(agent_from, to_addrs, msg.as_string())
        server.quit()
    except Exception, e:
        logger.error(u'邮件发送失败:' + str(e))
        print u'邮件发送失败:' + str(e)
        
        
