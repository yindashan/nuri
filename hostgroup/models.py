# -*- coding: utf-8 -*-

from django.db import models, IntegrityError
from django.db.models import Q

from redissync.models import get_host

# ------ 数据库定义 ------
# 主机
class Host(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'host'
    # 主机ID
    host_id = models.CharField(max_length=32)
    # 主机IP
    host_ip = models.CharField(max_length=40)
    # 类型（1:GD, 2:FK, 0:未分类）
    type = models.IntegerField(default=1)
    
# 主机组信息
class HostGroupInfo(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'host_group_info'
    # 名称
    name = models.CharField(max_length=128, unique=True)
    # 描述
    desc = models.CharField(max_length=128)

# 主机组
class HostGroupRelation(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'host_group_relation'
    # 主机组的ID
    group = models.ForeignKey(HostGroupInfo)
    # 主机的ID（不是HOST_ID）
    host = models.ForeignKey(Host)


# ------ 数据库中各表的信息获取 ------
# 取得host_group_info表的全部行
def get_all_host_group_info():
    return HostGroupInfo.objects.all()

# 取得host表的全部行
def get_all_host():
    return Host.objects.all()

# select * from host_group_relation where group_id = gid
def get_host_group_relation_by_gid(gid):
    return HostGroupRelation.objects.filter(group_id=gid)

# select * from host_group_info where id = item_id
def get_host_group_info_by_id(item_id):
    return HostGroupInfo.objects.get(id=item_id)

# 取得除item_id外的所有host_group_info表中的信息
def get_host_group_info_exclude_id(item_id):
    return HostGroupInfo.objects.exclude(id=item_id)

# 取得在ip_list中的主机（host表）
def get_host_in_ip(ip_list):
    return Host.objects.filter(host_ip__in=ip_list)


# ------ views各函数相关的数据库操作 ------
# 生成copy_from模态框中显示的主机列表
def gen_copy_from_host_group_relation(gid, hid_list):
    host_group_relation = get_host_group_relation_by_gid(gid)
    host_group_relation = host_group_relation.exclude(host_id__in=hid_list)
    return host_group_relation

# host_group_info表保存（添加/编辑模块）
def host_group_info_save(group_name, group_desc, item_id=None):
    try:
        if item_id == None:
            host_group_info = HostGroupInfo()
        else:
            host_group_info = get_host_group_info_by_id(item_id)
        host_group_info.name = group_name
        host_group_info.desc = group_desc
        host_group_info.save()
        return ""
    except IntegrityError:
        return u"主机组名称存在重复！"
    except:
        return u"保存主机组信息失败！"

# 处理添加/编辑时不存在IP的情况
def deal_nonexistent_ip(ip_list):
    # 1. 获得数据库中不存在的IP列表
    exist_host_list = get_host_in_ip(ip_list)
    exist_ip_list = []
    for host in exist_host_list:
        exist_ip_list.append(host.host_ip)
    
    nonexistent_ip_list = list(set(ip_list) - set(exist_ip_list))
    
    # 2. 查询redis，如果有对应的host_id，则使用，否则伪造一个FK开头的host_id
    host_list = get_host(nonexistent_ip_list)

    # 3. 将新的主机加入到host表中
    res_list = []
    for i, host_id in enumerate(host_list):
        record = Host()
        record.host_id = host_id
        record.host_ip = nonexistent_ip_list[i]
        if host_id.startswith("GD"):
            record.type = 1
        elif host_id.startswith("FK"):
            record.type = 2
        else:
            record.type = 0
        res_list.append(record)
    
    if res_list:
        Host.objects.bulk_create(res_list)
    
# 添加模块host_group_relation表保存
def add_host_group_relation(group_name, ip_list):
    if ip_list != "":
        ip_list = ip_list.split(',')
        
        res_list = []
        host_dict = {}
        
        gid = HostGroupInfo.objects.get(name=group_name).id
        
        deal_nonexistent_ip(ip_list) # 处理数据库中目前不存在的IP
        host_list = get_host_in_ip(ip_list)
        
        for host in host_list:
            host_dict[host.host_ip] = host.id
            
        for ip in ip_list:
            record = HostGroupRelation()
            record.group_id = gid
            record.host_id = host_dict[ip]
            res_list.append(record)
            
        if res_list:
            HostGroupRelation.objects.bulk_create(res_list)

# 编辑模块host_group_relation表保存
def edit_host_group_relation(item_id, new_ip_list, old_ip_list):
    # 1. 生成添加列表和删除列表
    add_list = list(set(new_ip_list) - set(old_ip_list))
    del_list = list(set(old_ip_list) - set(new_ip_list))
    
    # 2. 取得IP对应的数据库ID
    host_list = {}
    deal_nonexistent_ip(add_list) # 处理数据库中目前不存在的IP
    hosts = Host.objects.filter(Q(host_ip__in=add_list) | Q(host_ip__in=del_list))
    for host in hosts:
        host_list[host.host_ip] = host.id
    
    # 3. 处理要添加的IP
    res_add_list = []
    for ip in add_list:
        record = HostGroupRelation()
        record.group_id = item_id
        record.host_id = host_list[ip]
        res_add_list.append(record)
    if res_add_list:
        HostGroupRelation.objects.bulk_create(res_add_list)
    
    # 4. 处理要删除的IP
    res_del_list = []
    for ip in del_list:
        res_del_list.append(host_list[ip])
    if res_del_list:
        HostGroupRelation.objects.filter(group_id=item_id, host_id__in=res_del_list).delete()

# 主机组搜索部分数据库逻辑
def search_host_group(name_or_desc, ip):
    hostgroup_list = get_all_host_group_info().order_by('id')
    
    if name_or_desc:
        hostgroup_list = hostgroup_list.filter(Q(name__icontains=name_or_desc) | Q(desc__icontains=name_or_desc))
    
    if ip:
        # 1. 取得IP对应主机的数据库ID
        hid_list = []
        host_list = Host.objects.filter(host_ip__icontains=ip)
        for host in host_list:
            hid_list.append(host.id)
        
        # 2. 取得IP对应的全部主机组ID
        gid_list = []
        group_ids = HostGroupRelation.objects.filter(host_id__in=hid_list).values("group_id").distinct()
        for group in group_ids:
            gid_list.append(group["group_id"])
        
        # 3. 得到IP对应的主机组列表
        hostgroup_list = hostgroup_list.filter(id__in=gid_list)
        
    return hostgroup_list
    
# 主机组编辑“移动主机组”模态框的保存部分数据库逻辑
def move_to_save_model(cur_gid, move_to_gid, move_type, old_ip_list, saved_ip_list, move_ip_list):
    ip_list = old_ip_list
    
    if move_ip_list != []:
        # 1. 取得移动列表的数据库ID
        host_list = {}
        hosts = get_host_in_ip(move_ip_list)
        for host in hosts:
            host_list[host.host_ip] = host.id
        
        # 2. 无论复制还是移出，都会在选中的主机组中添加新纪录
        res_list = []
        for ip in move_ip_list:
            record = HostGroupRelation()
            record.group_id = move_to_gid
            record.host_id = host_list[ip]
            res_list.append(record)
        if res_list:
            HostGroupRelation.objects.bulk_create(res_list)
        
        # 3. 移出操作
        if move_type == "1":  # 移出
            # 3.1 删除数据库，更新new_ip_list
            del_hid_list = []
            for ip in move_ip_list:
                del_hid_list.append(host_list[ip])
            if del_hid_list:
                HostGroupRelation.objects.filter(group_id=cur_gid, host_id__in=del_hid_list).delete()
                ip_list = list(set(old_ip_list) - set(move_ip_list))
            
            # 3.2 更新saved_ip_list
            saved_ip_list = list(set(saved_ip_list) - set(move_ip_list))
    
    return ip_list, saved_ip_list
