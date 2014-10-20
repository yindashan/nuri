# -*- coding:utf-8 -*-
from django.utils.datastructures import SortedDict

# 日志级别字典
log_level_dict = {0:'DEBUG', 1:'INFO', 2:'WARN', 3:'ERROR'}

# 监控项类型字典
monitor_item_dict = {1:'单个变量', 2:'计算公式'}

# 图表类型
show_type_dict = {1:'4小时', 2:'1天', 3:'1个月', 4:'1年'}
#show_type_dict = {1:'4小时', 2:'1天', 3:'1个月', 4:'1年', 5:'3天', 6:'1周'}

# 权限类型
#permission_type_dict = {1:'模块',2:'应用项',3:'监控项',4:'节点',5:'监控指数'}
permission_type_dict = {1:'模块',2:'应用项',3:'监控项',4:'节点',5:'监控指数',6:'配置管理',7:'其他'}

# 日志类型
log_type_dict = {0:'其他日志', 1:'用户管理日志', 2:'角色管理日志', 3:'应用项管理日志', \
 4:'监控项管理日志', 5:'节点管理日志', 6:'监控指数管理日志'}

# 联合图表类型
combine_type_dict = {1:'曲线图',2:'饼图',3:'柱形图'}

# 图表类型
chart_type_dict = {0:'单数据源曲线图',1:'多数据源曲线图',2:'饼图',3:'柱形图'}

# 是否报警
alarm_type_dict = {0:'否', 1:'是'}

# 机房信息
noc_info_dict = {
                 'BJM1':u'亦庄移动机房',
                 'GS-BJ-DD-1':u'北京大地机房',
                 'BGP-BJ-ShuBei-1':u'数字北京蓝汛机房',
                 'BGP-HK-1':u'香港机房',
                 'BGP-NJ-DX-1':u'南京电信机房',
                 'BGP-QD-EXN-1':u'青岛二枢纽机房',
                 'BGP-TJ-HY-1':u'天津华苑国际数据港机房',
                 'GS-BJ-CP-1':u'北京昌平机房',
                 'GS-BJ-FH-1':u'北京方恒机房',
                 'GS-BJ-DH-1':u'北京大恒机房',
                 'BGP-BJ-SD-1':u'上地蓝讯机房',
                 'BGP-BJ-YZ-1':u'亦庄世纪互联机房'
                 }

# 是否有效
valid_type_dict = {0:'否', 1:'是'}

# 计算方法
calc_method_dict = {0:'平均值', 1:'最大值', 2:'最小值'}

# 应用项类型
app_type_dict = {1:'Http', 2:'Ping', 3:'TCP', 4:'其它', 5:'host_status'}

# 通知间隔
notify_dict = SortedDict()
notify_dict[1] = u'不限'
notify_dict[10] = u'10分钟'
notify_dict[60] = u'1小时'
notify_dict[360] = u'6小时'

# 重试次数
retry_dict = SortedDict()
retry_dict[1] = u'1次'
retry_dict[2] = u'2次'
retry_dict[3] = u'3次'

# 检查间隔
check_dict = SortedDict()
check_dict[1] = u'1分钟'
check_dict[5] = u'5分钟'








