//当组织结构树中的节点被单击时触法此函数
function clickNode(node){
	var url = "/shownode/display";
	var data = {'node_id':node.id}
	jQuery.ajax({
		type: 'GET',
		url: url,
		data: data,
		success: success,
		error:error,
		dataType: 'html',
		async:false
	});
}
//右键菜单
function open_context_menu(e,node){
	//检查权限
    if(node.attributes.operate_permission){
    	e.preventDefault();
	$("#mm").menu('show', {left: e.pageX,top: e.pageY  }); 
	$("#hide_id").val(node.id);
    }else{
    	e.preventDefault();
    	alert("你没有对此节点的操作权限!");
    }
} 
// 右键菜单点击动作的处理函数
function context_menu_click(item){  
	var node_id = parseInt($("#hide_id").val());
	var node = $('#show_tree').tree('find', node_id);
	$("#hide_action").val(item.id);
	if(item.id=='add'){
		$('#node_div').modal('show');

	}else if(item.id=='update'){
		//初始化，过去的设置内容
		init_node_div(node);
		$('#node_div').modal('show');

	}else if(item.id=='remove'){
		//处理前端展示
		$("#show_tree").tree('remove',node.target);
		//处理后台数据
		node_remove(node);
	}
}
//清理增加、编辑节点面板
function clear_node_div(){
	$('#node_div').modal('hide');
	$("#hide_id").val("");
	//-----------节点配置面板------------------
	
	//节点名称
	$("#curr_node").val("");
	//单数据源
	$("#node_table tbody tr").remove();
	$("#app option:eq(0)").attr("selected",true);
	$("#host option:gt(0)").remove();
	$("#monitor option:gt(0)").remove();
	$("#show_type option:eq(0)").attr("selected",true);
}
//编辑节点----初始化node_div
function init_node_div(node){
	$("#curr_node").val(node.text);
	jQuery.ajax({
		type: 'GET',
		url: "/shownode/get_relation/",
		data: {'node_id':node.id},
		success: update_init_success,
		error:error,
		dataType: 'json',
		async:true
	});
}
function update_init_success(data){
	var i=0;
	//单数据源图表
	single_array = data.single_charts
	for(i=0;i<single_array.length;i++){
		var item = $("<tr></tr>");
		//app_desc
		var app_td = $("<td></td>");
		app_td.text(single_array[i].app_desc);
		item.append(app_td);
		//host_ip
		var host_td = $("<td></td>");
		host_td.text(single_array[i].host_ip);
		item.append(host_td);
		//monitor_desc
		var monitor_td = $("<td></td>");
		monitor_td.text(single_array[i].monitor_desc);
		item.append(monitor_td);
		//删除
		item.append($("<td><button onclick='remove_item(this);' class='btn btn-mini btn-danger'>删除</button></td>"))
		
		item.attr("chart_id",single_array[i].id);
		
		$("#node_table tbody").append(item);
	}
}
//删除某个已选定的图表
function remove_item(obj){
	$(obj).parent().parent().remove();
}

//显示与所选应用对应的host和监控项
function node_config_success(data){
	//重新设置下拉列表
	$("#host option:gt(0)").remove();
	$("#monitor option:gt(0)").remove();

	host_array = data.host_list
	monitor_array = data.monitor_list;
	//主机
	var i=0;
	for(i=0;i< host_array.length;i++){
		var t = $("<option></option>")
		t.val(host_array[i]);
		t.text(host_array[i]);
		$("#host").append(t);
	}
	//监控项
	i=0;
	for(i=0;i< monitor_array.length;i++){
		var m = $("<option></option>")
		m.val(monitor_array[i].id);
		m.text(monitor_array[i].desc);
		$("#monitor").append(m);
	}
	$("#host,#monitor").chosen({no_results_text: "没有找到",search_contains:true}); 
	$("#host,#monitor").trigger("liszt:updated");
}

//显示与所选host对应的应用
function node_host_config_success(data){
	//重新设置下拉列表
	$("#app_id option:gt(0)").remove();

	//主机
	var i=0;
	for(i=0;i< data.length;i++){
		var t = $("<option></option>")
		t.val(data[i].app_id);
		t.text(data[i].app_name);
		$("#app_id").append(t);
	}
	$("#app_id").chosen({no_results_text: "没有找到",search_contains:true}); 
	$("#app_id").trigger("liszt:updated");
}

//添加单数据源曲线图
function chart_add_click(){
	//-------------------内部函数 定义----------------
	function getChartIdSuccess(data){
		chart_id = data;
	}
	//---------------------------------------------------


	var app_id = $("#app").val();
	var monitor_id = $("#monitor").val();
	var app_text = $("#app option:selected").html();
	var host = $("#host").val();
	var monitor_text = $("#monitor option:selected").html();
	//后面查询得到的值会覆盖此值
	var chart_id = "undefinded";
	//每一个选项都不能为空
	if(app_id&&host&&monitor_id){
		var item = $("<tr></tr>");
	
		var app_td = $("<td></td>");
		app_td.text(app_text);
		item.append(app_td);
	
		var host_td = $("<td></td>");
		host_td.text(host);
		item.append(host_td);
	
		var monitor_td = $("<td></td>");
		monitor_td.text(monitor_text);
		item.append(monitor_td);
	
		//删除
		item.append($("<td><button onclick='remove_item(this);' class='btn btn-mini btn-danger'>删除</button></td>"))
	
		//同步请求获取此showchart表记录的id
		data = {"app_id":app_id,"host":host,"monitor_id":monitor_id};
		jQuery.ajax({
			type: 'GET',
			url: "/showchart/get_chart_id/",
			data: data,
			success: getChartIdSuccess,
			error:error,
			dataType: 'text',
			async:false
		});
		item.attr("chart_id",chart_id);
	
		//检查此item是否已存在
		tr_array = $("#node_table").find("tr");
		for(var i=0;i<tr_array.length;i++){
			tr_id = $(tr_array[i]).attr("chart_id");
			if(tr_id==chart_id){
				//已存在
				alert("该图表已存在，无法添加");
				return;
			}
		}
		$("#node_table tbody").append(item);
	}else{
		alert("配置信息缺失!");
	}
}

//新增节点和编辑节点都使用此函数　编辑节点，同时提交节点和图表的对应关系
function node_confirm_click(){
	var node_id = parseInt($("#hide_id").val());
	var node = $('#show_tree').tree('find', node_id);
	var node_text = $("#curr_node").val();
	//图表ID数组
	var id_array = [];
	$("#node_table tbody tr").each(function(){
		var id = $(this).attr("chart_id");
		if(id){
			id_array.push(id);
		}
	});
	var action = $("#hide_action").val()
	if(action == 'add'){
		//处理前端展示
		$("#show_tree").tree('append', {
			parent: node.target,
			data: [{"id":"undefined","text": node_text,"attributes":{"operate_permission":true}}]
		});
		//处理后台数据
		node_add(node,node_text,id_array);
	}else if(action == 'update'){
		//处理前端展示
		$("#show_tree").tree('update', {
			target: node.target,
			text: node_text
		});
		//处理后台数据
		node_update(node,node_text,id_array);
	}
	//清理node_div
	clear_node_div();
	//clickNode();
}

function node_add(parent_node,node_text,id_array){
    jQuery.ajax({
		type: 'POST',
		data:{'action':'append','parent_id':parent_node.id,'text':node_text,'related_ids':id_array.join(',')},
		url: "/shownode/manipulate_tree/",
		success: append_success,
		error:manipulate_error,
		dataType: 'json',
		async:false
	});	
	node = $('#show_tree').tree('find', 'undefined');
	$("#show_tree").tree('update', {
		target: node.target,
		id: $("#hide_id").val()
	});
}
function node_update(node,node_text,id_array){
    jQuery.ajax({
		type: 'POST',
		data:{'action':'update','node_id':node.id,'text':node_text,'related_ids':id_array.join(',')},
		url: "/shownode/manipulate_tree/",
		success: manipulate_success,
		error:manipulate_error,
		dataType: 'json',
		async:false
	});	
}
function manipulate_success(data){
	alert("操作成功!");
}
function append_success(data){
    //节点的id号暂存一下
	$("#hide_id").val(data.node_id)
	alert("操作成功!");
}
function manipulate_error(data){
	alert("操作失败!");
}
function node_remove(node){
    jQuery.ajax({
		type: 'POST',
		data:{'action':'delete','node_id':node.id},
		url: "/shownode/manipulate_tree/",
		success: manipulate_success,
		error:manipulate_error,
		dataType: 'json',
		async:true
	});	
}

