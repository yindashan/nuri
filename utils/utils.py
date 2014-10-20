# -*- coding:utf-8 -*-
import time
import re
import random
import urlparse

'''
* 匹配IP地址
* @param ip
* @return MatchObject ip地址正确;
*         None ip地址错误;
'''
def isIP(ip):
    return re.search(r'^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$', ip)

'''
* 匹配电话号码，
* 如：（010）-12345678， （010） 12345678，（010）12345678， 010-12345678，010 12345678， 01012345678 
*    （0913）-1234567， （0913） 1234567，（0913）1234567， 0913-1234567，0913 1234567， 09131234567
* @param tel
* @return MatchObject tel正确;
*         None tel错误;
'''
def isTel(tel):
    return re.search(r'^(0\d{2})[- ]?\d{8}|0\d{2}[- ]?\d{8}|(0\d{3})[- ]?\d{7}|0\d{3}[- ]?\d{7}$', tel)

'''
* 匹配手机号码
* @param mobile
* @return MatchObject mobile正确;
*         None mobile错误; 
'''
def isMobile(mobile):
    return re.search(r'1[358]\d{9}', mobile)      

'''
* 匹配端口号0~65535
* @param port
* @return MatchObject port正确;
*         None port错误; 
'''   
def isPort(port):
    return re.search(r'^6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}|0$', port)

'''
* 匹配电流，单位：“ma”，范围：0~13000
* @param amp
* @return MatchObject amp正确;
*         None amp错误;
* 
'''
def isAmp(amp):
    return re.search(r'^13000|1[0-2]\d{3}|[1-9]\d{0,3}|0$', amp)

'''
* os位数，只有32、64两种
* @param osbyte
* @return MatchObject osbyte正确;
*         None osbyte错误; 
'''
def isOSByte(osbyte):
    return re.search(r'^32|64$', osbyte)

'''
* 日期格式 ：“yyyy/MM/dd”， 范围：2000/1/1~2999/12/31
* @param date
* @return MatchObject date正确;
*         None date错误; 
'''
def isDate(date):
    return re.search(r'^2\d{3}[/-]([1-9]|1[0-2])[/-]([1-9]|[1-2]\d|3[0-1])$', date)


def isInt(num):
    return re.search(r'^[1-9]\d*|0', num)
'''
* 机房状态： 0:'备用', 1:'使用', 2:'报废'
* @param status
* @return MatchObject status正确;
*         None status错误; 
'''
def isNOCStatus(status):
    return re.search(r'^[0-2]{1}$', status)

'''
* 机架状态： 0:'备用', 1:'使用', 2:'报废'
* @param status
* @return MatchObject status正确;
*         None status错误; 
'''
def isRackStatus(status):
    return re.search(r'^[0-2]{1}$', status)

'''
* 机架总空间，只有42、48两种
* @param space
* @return MatchObject space正确;
*         None space错误; 
'''
def isRackSpace(space):
    return re.search(r'^42|48$', space)

'''
* 设备状态： 0:'备用', 1:'使用', 2:'报废', 3:'报修', 4:'修理', 5:'闲置'
* @param status
* @return MatchObject status正确;
*         None status错误; 
'''
def isEquipmentStatus(status):
    return re.search(r'^[0-5]{1}$', status)

'''
* IP地址类型： 0:'内网', 1:'外网'
* @param type
* @return MatchObject type正确;
*         None type错误; 
'''
def isIPType(iptype):
    return re.search(r'^[0,1]{1}$', iptype)

'''
* IP地址状态：0:'备用', 1:'使用'
* @param status
* @return MatchObject status正确;
*         None status错误; 
'''
def isIPStatus(status):
    return re.search(r'^[0,1]{1}$', status)

'''
* datestr转换成secs
* 将时间字符串转化为秒("2012-07-20 00:00:00"->1342713600.0)
* @param datestr;
* @return secs;
*
'''
def datestr2secs(datestr):
    tmlist = []
    array = datestr.split(' ')
    array1 = array[0].split('-')
    array2 = array[1].split(':')
    for v in array1:
        tmlist.append(int(v))
    for v in array2:
        tmlist.append(int(v))
    tmlist.append(0)
    tmlist.append(0)
    tmlist.append(0)
    if len(tmlist) != 9:
        return 0
    return int(time.mktime(tmlist))


'''
* secs转换成datestr
* 将秒转化为时间字符串(1342713600.0->"2012-07-20 00:00:00")
* @param secs;
* @return datestr;
*
'''
def secs2datestr(secs):
    if int(secs) < 0:
        return ""
    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs)))


'''
* datestr转换成datestr
* 将时间字符串转化为时间字符串("2012-07-20"->"2012-07-20 00:00:00")
* @param datestr;
* @return datestr;
*
'''
def datestr2datestr(datestr):
    # 字符串->time
    datestr = time.strptime(datestr, "%Y-%m-%d")
    # time->字符串
    datestr = time.strftime("%Y-%m-%d %H:%M:%S", datestr)
    # 字符串->time
    return datestr

#把链表中的数据转换成字符串　例: [1,2,3]  -->  '1,2,3'
def listToStr(slist):
    num = len(slist)
    ids = ''
    for i in range(num):
        if i !=0:
            ids += (',' + str(slist[i]))
        else:
            ids += str(slist[i])
    return ids
# 主要用于在SQL 拼装中使用
def listToStr2(slist):
    num = len(slist)
    ids = ''
    for i in range(num):
        if i !=0:
            ids += ("," + "\'"  + slist[i] + "\'")
        else:
            ids += ("\'"  + slist[i] + "\'")
    return ids

# 以指定的百分比产生True
def percentTrue(num):
    t = random.randint(1,100)
    if t<=num:
        return True
    else:
        return False
        
# 把形如 var1=123&var2=456　转换为字典
def body2Dict(string):
    dd = {}
    param_list = urlparse.parse_qs(string)
    for key in param_list:
        dd[key] = param_list[key][0]
    return dd 

# IP字符串转换为整数    
def ip2num(ip):
    temp_list = ip.split('.')
    res = 0
    for item in temp_list:
        res = res* 256
        res += int(item)
        
    return res
    
# 子网掩码的数字表示形式
# 如 255.255.255.0 -> 24
def mask_repr(mask):
    num = ip2num(mask)
    i = 0
    while(num > 0):
        if (num & 0x01) == 0:
            i = i + 1
        num = num / 2
    return 32 - i
        
    
# 过滤IP列表防止出现重复的IP地址 
# 按IP地址大小排序       
def filterIP(ip_list):
    ip_list = list(set(ip_list))
    ip_list.sort(cmp=ip_cmp)
    return ip_list

# x,y --IP字符串
def ip_cmp(x, y):
    if ip2num(x) < ip2num(y):
        return -1
    elif ip2num(x) == ip2num(y):
        return 0
    else:
        return 1
           
# 判断是否是私有IP  
# 判断方法, 把IP转换为数值, 在此数值间，即为私有IP
#        私有IP：A类  10.0.0.0-10.255.255.255   
#               B类  172.16.0.0-172.31.255.255   
#               C类  192.168.0.0-192.168.255.255  
#        环回地址 127.0.0.0-127.255.255.255
# 
def is_private_ip(ip):
    segment_list = []
    # A 类
    segment_list.append( (ip2num('10.0.0.0'), ip2num('10.255.255.255')) )
    
    # B 类
    segment_list.append( (ip2num('172.16.0.0'), ip2num('172.31.255.255')) )
    
    # C 类
    segment_list.append( (ip2num('192.168.0.0'), ip2num('192.168.255.255')) )
    
    # 环回
    segment_list.append( (ip2num('127.0.0.0'), ip2num('127.255.255.255')) )
    
    number = ip2num(ip)
    for seg in segment_list:
        if number >= seg[0] and number <= seg[1]:
            return True
            
    return False 
    
    
    
    
    
