# -*- coding:utf-8 -*-
from django.conf import settings

# 工厂方法用于产生检查规则    
class RuleFactory(object):
    # classname -- 规则类名
    # 返回 Connector 对象
    @staticmethod
    def genRule(classname):      
        return globals()[classname]()
        
# 使用应用 HOST_STATUS 的状态作为主机存活的判断规则
class HostStatusRule(object):
    # 　True    --表示 up
    #   False    -- 表示 down
    def check(self, host):
        # CRITICAL, UNKNOW
        status = settings.REDIS_DB.hget('ah_HOST_STATUS_' + host, 'current_status')
        if status !=None and (status == 'UNKNOW'):
            return False
        return True
    
# 使用应用 SYS_PING 的状态作为主机存活的判断规则
class SysPingRule(object):
    # 　True    --表示 up
    #   False    -- 表示 down
    def check(self, host):
        status = settings.REDIS_DB.hget('ah_SYS_PING_' + host, 'current_status')
        if status !=None and (status == 'CRITICAL' or status == 'UNKNOW'):
            return False
        return True
        
    