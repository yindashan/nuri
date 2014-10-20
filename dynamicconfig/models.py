# -*- coding:utf-8 -*-

# django library
from django.db import models

# stdandard library
import ldap


# LDAP 
class LDAPConf(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'ldapconf'
    server = models.CharField(max_length=64) # server地址
    base_dn = models.CharField(max_length=64) # Base DN值
    domainname = models.CharField(max_length=64) # 域名
    loginname = models.CharField(max_length=32) # 登录名
    username = models.CharField(max_length=32) # 用户名
    password = models.CharField(max_length=32) # 密码
    
    def __str__(self):
        return self.server

# 获取LDAP配置对象
def get_ldapconf():
    ldapconfs = LDAPConf.objects.all()
    if ldapconfs:
        ldapconf = ldapconfs[0]
        return ldapconf
    else:
        return None
        
        
# 添加用户时认证LDAP中是否有该用户名
def validate_ldap(validateusername):
    ldapconf = get_ldapconf()
    if ldapconf == None:
        return False
    username = ldapconf.username
    password = ldapconf.password
    flag = False
    try:
        Server = ldapconf.server
        baseDN = ldapconf.base_dn
        searchScope = ldap.SCOPE_SUBTREE
        searchFilter = ldapconf.loginname + "=" + validateusername
        username = ldapconf.domainname + "\\" + username
        retrieveAttributes = None
        conn = ldap.initialize(Server)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.protocol_version = ldap.VERSION3
        conn.simple_bind_s(username, password)
        ldap_result_id = conn.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = conn.result(ldap_result_id, 0)
            if(result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)
                    Name,Attrs = result_data[0]
                    if hasattr(Attrs, 'has_key') and Attrs.has_key('mail'):
                        pass
                        #print Attrs['mail'][0]
                    if hasattr(Attrs, 'has_key') and Attrs.has_key('sAMAccountName'):
                        pass
                        #print Attrs['sAMAccountName'][0]
                    flag = True  
        
    except ldap.LDAPError, e:
        flag = False
    return flag
    
# LDAP登录认证
def login_ldap(username, password):
    ldapconf = get_ldapconf()
    if ldapconf == None:
        return False
    flag = False
    try:
        Server = ldapconf.server
        baseDN = ldapconf.base_dn
        searchScope = ldap.SCOPE_SUBTREE
        searchFilter = ldapconf.loginname + "=" + username
        username = ldapconf.domainname + "\\" + username
        retrieveAttributes = None
        conn = ldap.initialize(Server)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.protocol_version = ldap.VERSION3
        conn.simple_bind_s(username, password)
        flag = True
    except ldap.LDAPError, e:
        flag = False
    return flag    