# -*- coding:utf-8 -*-
from django.db import models
from monitoritem.models import MonitorItem, parse_threshold
from monitorpoint.models import MonitorPoint
from appitem.models import AppService
from redissync.models import host2ip
from authority.models import Permission
        
#组织结构节点表
#+----+--------------+-----------+-------+
#| id | text         | parent_id | level |
#+----+--------------+-----------+-------+
#|  1 | 高德软件       |       -1 |     1 |
#+----+--------------+-----------+-------+
# 此节点作为展示的根节点
class ShowNode(models.Model):
    class Meta:
        db_table = "show_node"
    # 主键由Django生成
    # 节点显示文本
    text = models.CharField(max_length=64)
    # 父节点id
    parent_id = models.IntegerField()
    # 在树中的层级
    level = models.IntegerField()
    
# 单数据源图
class Chart(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'chart'
    # 主键由Django生成
    # 监控点ID
    point_id = models.IntegerField()
    
    #外键  应用服务
    node = models.ForeignKey(ShowNode) # 多对一关联

# 为了展现需要,　不会存储在数据库中   
class ShowChart(object):
    def __init__(self, chart, start_time, end_time):
        self.start_time = start_time
        self.end_time =  end_time 
        mp = MonitorPoint.objects.get(id=chart.point_id)
        
        ip = host2ip(mp.host)
        monitor_item = MonitorItem.objects.get(id=mp.mid)
        self.title = mp.appname + " " + ip + " " + monitor_item.desc
        
        self.id = chart.id
        self.app_desc = AppService.objects.get(app_name=mp.appname).desc
        self.host_ip = ip
        self.monitor_desc = monitor_item.desc
        
        
        # label1,point_id1,color1;label2,point_id2,color2;
        self.data_line = 'monitor,%s,#0000ff;' % chart.point_id
        
        # label,data,color;label2,data2,color2;... ...
        self.alert_line = ''
        
        # 警告线
        (mtype,t,t1,t2) = parse_threshold(monitor_item.warning_threshold)
        if mtype == 1 or mtype == 2:
            self.alert_line += 'warning,%s,#f8fb03;' % t
        else:
            self.alert_line += 'warning_min,%s,#f6f852;' % t1
            self.alert_line += 'warning_max,%s,#f8fb03;' % t2
        
        # 错误线
        (mtype,t,t1,t2) = parse_threshold(monitor_item.critical_threshold)
        if mtype == 1 or mtype == 2:
            self.alert_line += 'critical,%s,#ff0000;' % t
        else:
            self.alert_line += 'critical_min,%s,#fcbaba;' % t1
            self.alert_line += 'critical_max,%s,#ff0000;' % t2
        
# node ID 转换成 节点权限字符串
def nodeid2AuthStr(node_id,ptype):
    return "node_" + str(node_id) + '_' + ptype
    
# 用于配置读写权限
def right_tree_struct(node_id, control_level, purpose, auth_set):
    dd = {}
    auth_str = nodeid2AuthStr(node_id, purpose)
    #获取子树的根节点
    node = ShowNode.objects.get(id=node_id)
    dd["id"] = node.id
    dd["text"] = node.text
    
    permission_id = Permission.objects.get(codename=auth_str).id
    dd["attributes"] = {"permission_id":permission_id}
        
    if node.level < control_level:
        #判断其是否由子节点
        node_list = ShowNode.objects.filter(parent_id=node_id).order_by('text')
        child_list = []
        if node_list:
            for item in node_list:
                child_list.append(right_tree_struct(item.id, control_level, purpose, auth_set))
            dd["state"] = "closed"   
            dd["children"] = child_list
            
    # 复选框是否被选中
    if auth_str in auth_set:
        if node.level == control_level:
            dd["checked"] = True
        elif (node.level < control_level) and ("children" not in dd):
            dd["checked"] = True

    return dd
    
# 提取树形结构,并返回以node_id 为根的树形结构对应的字典
# 加入权限控制  auth_set--权限集合 pnode_permission---父节点是有操作权限　control_level---权限控制层级
# 如果节点的层级大于control_level,则使用父节点的权限
def tree_structure(node_id, auth_set, pnode_permission, control_level):
    root_node = ShowNode.objects.get(id=node_id)
    if (root_node.level <= control_level) and (nodeid2AuthStr(node_id, 'read') not in auth_set) :
        return None
        
    dd = {}
    #获取子树的根节点
    dd["id"] = root_node.id
    dd["text"] = root_node.text
    attributes = {}
    # 小于等于权限控制级别时检查节点权限，大于时，使用父节点的权限
    if root_node.level <= control_level:
        if nodeid2AuthStr(node_id, 'operate') in auth_set:
            attributes["operate_permission"] = True
        else:
            attributes["operate_permission"] = False
    else:
        attributes["operate_permission"] = pnode_permission
        
    dd["attributes"] = attributes

    #判断其是否由子节点
    node_list = ShowNode.objects.filter(parent_id=node_id).order_by('text')
    child_list = []
    if node_list:
        for item in node_list:
                item_struct = tree_structure(item.id, auth_set, attributes["operate_permission"], control_level)
                if item_struct:
                    child_list.append(item_struct)
        if child_list:
            dd["state"] = "closed"   
            dd["children"] = child_list
        
    return dd;
    
# 删除树中的节点,注意此节点可能有子节点    
def delete_node(node_id):
    # 遍历以此节点为根的子树
    id_list = []
    queue = [node_id]  
    #　广度优先遍历
    while len(queue) > 0 :
        # 访问次节点
        nid = queue.pop(0);
        id_list.append(nid);
        #判断其是否由子节点
        node_list = ShowNode.objects.filter(parent_id=nid)
        if node_list:
            for item in node_list:
                queue.append(item.id)
    
    # 删除节点上对应的图表
    Chart.objects.filter(node_id__in=id_list).delete()
    
    # 删除show_node表中的记录
    ShowNode.objects.filter(id__in=id_list).delete()
    
# 增加子节点
def append_node(parent_id, text, control_level):
    parent_node = ShowNode.objects.get(id=parent_id)
    node = ShowNode();
    node.text = text;
    node.parent_id = parent_id;
    node.level = parent_node.level + 1
    node.save();
    
    # 加入权限记录
    if node.level <= control_level:
        Permission(codename=nodeid2AuthStr(node.id, "read"), type=4).save()
        Permission(codename=nodeid2AuthStr(node.id, "operate"), type=4).save()
        
    return node;    

# 更新节点的显示文字
def update_node(node_id,text):
    node = ShowNode.objects.get(id=node_id)
    node.text = text
    node.save();
    
# 绑定图表到节点上
def config_chart(node_id, chart_id_list):
    node = ShowNode.objects.get(id=node_id)
    Chart.objects.filter(node=node).update(node=-1)
    Chart.objects.filter(id__in=chart_id_list).update(node=node.id)

def get_chart_list(node_id, start_time, end_time):
    chart_list = Chart.objects.filter(node_id=node_id).order_by('id')
    res_list = []
    for chart in chart_list:
        mp = MonitorPoint.objects.get(id=chart.point_id)
        if mp.is_valid == 1:
            res_list.append(ShowChart(chart, start_time, end_time))
    return res_list
    
    
    