# -*- coding:utf-8 -*-
import logging
import traceback
from django.conf import settings
from utils.utils import is_private_ip, mask_repr

# 内存信息
class MemInfo(object):
    def __init__(self):
        # 5.1 生产厂商
        self.mem_mf = ''
        # 5.2 型号
        self.mem_model = ''
        # 5.3 容量 (GB)
        self.mem_size = 0
        # 5.4 数量
        self.mem_number = 0
        
class HardDiskInfo(object):
    def __init__(self):
        # 6.1 编号
        self.hd_sn = ''
        # 6.2 生产厂商
        self.hd_mf = ''
        # 6.3 接口类型
        self.hd_interface = ''
        # 6.4 型号
        self.hd_model = ''
        # 6.5 转速
        self.hd_speed = 0
        # 6.6 单盘容量(G)
        self.hd_size = 0
        # 6.7 数量
        self.hd_number = 0

# 主机硬件信息
class HostHardware(object):
    def __init__(self):
        # 1. 机器信息
        # 1.1 机器生产厂商
        self.machine_mf = ''
        # 1.2 机器型号
        self.machine_model = ''
        # 1.3 机器序列号
        self.machine_sn = ''
        
        # 2. 操作系统
        # 2.1 OS类型
        self.os_type = ''
        # 2.2 OS位数
        self.os_bit = ''
        # 2.3 OS版本
        self.os_version = ''
        
        # 3. IP信息
        # 3.1 管理IP 
        self.manage_ip = ''
        # 3.2 内网IP (有多个则逗号分隔)
        self.private_ip = ''
        # 3.3 外网IP (有多个则逗号分隔)
        self.public_ip = ''
        # 3.4 是否Bond
        self.is_bond = False
        # 3.5 域名服务器
        self.nameserver = ''
        
        # 4. CPU信息
        # 4.1 CPU生产厂商
        self.processor_mf = ''
        # 4.2 型号
        self.processor_model = ''
        # 4.3 内核数
        self.processor_cores = 0
        # 4.4 数量(个数)
        self.processor_number = 0
        
        # 5. 内存信息
        self.mem_list = []
        
        # 6. 磁盘信息
        self.hard_disk_list = []

def parse_ip_info(data):
    private_ip_list = []
    public_ip_list = []
    item_list = data.split(';')
    for item in item_list:
        temp_list = item.split(':')
        tt = '%s/%s %s' % (temp_list[1], mask_repr(temp_list[2]), temp_list[3])
        
        if is_private_ip(temp_list[1]):
            private_ip_list.append(tt)
        else:
            public_ip_list.append(tt)
            
    data = data.lower()  
       
    is_bond = True
    if data.find('bond') == -1:
        is_bond = False
        
    return ','.join(private_ip_list), ','.join(public_ip_list), is_bond
   
    
def parse_mem_info(data):
    res_list = []
    item_list = data.split(';')
    for item in item_list:
        temp_list = item.split(':')
        m = MemInfo()
        m.mem_mf = temp_list[0]
        m.mem_model = temp_list[1]
        m.mem_size = temp_list[2]
        m.mem_number = temp_list[3]
        res_list.append(m)
    return res_list
    
# 到处所有机器的硬件信息列表        
def export_hardware_info():
    logger = logging.getLogger("django")
    pipe = settings.REDIS_DB.pipeline()
    
    # 通过硬件检查结果得到
    ip_host_dict = settings.REDIS_DB.hgetall("ip_host")
    
    host_set = set()
    logger.info("获取ip_host列表")
    for ip in ip_host_dict:
        logger.info("IP:%s, host_id:%s", ip, ip_host_dict[ip])
        host = ip_host_dict[ip]
        # 只提取真实主机的信息
        if host.startswith('GD'):
            host_set.add(host)
            
    host_list = list(host_set)       
    for host in host_list:
        pipe.hgetall(host + '_hc') 
     
    item_list = pipe.execute()
    res_list = []
    # 失败数
    fail_count = 0
    count = len(item_list)
    for i in range(len(item_list)):
        host = host_list[i]
        logger.info("开始处理主机硬件信息, host_id:%s", host)
        
        item = item_list[i]
        if not item:
            continue
        try: 
            temp = HostHardware()
            temp.machine_mf = item['MANUFACTURER'] 
            temp.machine_model = item['PRODUCT_NAME']
            temp.machine_sn = item['SERIAL_NUMBER']
            
            temp.os_type = item['OS_TYPE']
            temp.os_bit = item['OS_BIT']
            temp.os_version = item['OS_VERSION']
            
            temp.manage_ip = item['MANAGE_IP']
            #temp.manage_ip = ''
            temp.private_ip, temp.public_ip, temp.is_bond = parse_ip_info(item['SYS_NETWORK'])
            
            #temp.private_ip = item['IP']
            
            temp.nameserver = item['NAMESERVER']
            
            temp.processor_mf = item['PROCESSOR_MANUFACTURER']
            temp.processor_model = item['PROCESSOR_TYPE']
            temp.processor_cores = item['PROCESSOR_CORES']
            temp.processor_number = item['PROCESSOR_NUMBER']
            
            temp.mem_list = parse_mem_info(item['MEM_INFO'])
            
            # 目前没有取得硬盘信息, 插入一条空记录
            hd = HardDiskInfo()
            hd.hd_sn = ''
            hd.hd_mf = ''
            hd.hd_interface = ''
            hd.hd_model = ''
            hd.hd_speed = ''
            hd.hd_size = ''
            hd.hd_number = ''
            
            temp.hard_disk_list = [hd]
            
            res_list.append(temp)
        except BaseException:
            fail_count = fail_count + 1
            logger.error("处理主机硬件信息异常,host_id:%s, 附加信息:\n%s", host, traceback.format_exc())
            
    logger.error("共处理主机数:%s, 失败数:%s", count, fail_count)
    return res_list
        
        

        
        

        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    

    
    