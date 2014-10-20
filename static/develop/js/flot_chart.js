// 前一次鼠标hover的点
var previousPoint = null;

// 绘制曲线图
function drawLineChart(obj){
	//################## 1. 准备数据  #################
	//-----------1.1 设置标题 --------------
	// Title
  	var chart_title = $(obj).attr("chart_title");
	$(obj).parent().parent().find('h2').html('<i class="icon-list-alt"></i>' + ' ' + chart_title);
	//-----------1.2 计算显示的开始和结束时间--------------
	var showEndTime = null;
	var showStartTime = null;

	var start_str = $(obj).attr("start_time") + ":00";
	showStartTime = parseDate(start_str).getTime()/1000;

	var end_str = $(obj).attr("end_time")+":00";
	showEndTime = parseDate(end_str).getTime()/1000;

	//-----------1.3 计算 date_pattern --------------
	var date_pattern = auto_date_pattern(showStartTime, showEndTime)

	//############### 2. 设置图中要显示的数据#################
	//---------label 标签-------
	var chart_labels = new Array();
	//---------图表上要显示的所有数据-------
	var chart_data = new Array();
	//---------不同的曲线对应的颜色-------
	var chart_colors = new Array();

	// ---------- 2.1  警告和错误 警戒线---------------
	var alert_line = $(obj).attr("alert_line");
	var alert_array = alert_line.split(';');
	for(var i=0;i<alert_array.length;i++){
		if(alert_array[i]){
			var temp_array = alert_array[i].split(',');
			chart_labels.push(temp_array[0]);
			value = parseFloat(temp_array[1])
			chart_data.push([[showStartTime*1000,value],[showEndTime*1000,value]]);
			chart_colors.push(temp_array[2]);
		}
	}
	//---------------- 2.2 设置监控项数据-------------
	var data_line = $(obj).attr("data_line");
	var data_array = data_line.split(';');
	for(var i=0;i<data_array.length;i++){
		if(data_array[i]){
			var temp_array = data_array[i].split(',');
			chart_labels.push(temp_array[0]);
			chart_colors.push(temp_array[2]);
			var url ="/monitoritem/fetch_data/"; 
			var data = {
					'point_id': temp_array[1],
					'start':start_str,
					'end':end_str
					};
		    	jQuery.ajax({
				type: 'GET',
				url: url,
				data: data,
				success: data_success(chart_data),
				error:data_error,
				dataType: 'text',
				async:false
			});
		}
	}
	var label_data = [];
	for(var i=0;i<chart_labels.length;i++){
		var item={};
		item['label'] = chart_labels[i];
		// 由于 flotchart 只能显示UTC 时间,因此需要对时间作fake操作
		// +8hour
		for(var j=0;j<chart_data[i].length;j++){
			chart_data[i][j][0]=chart_data[i][j][0] + 60*60*8*1000;
		}
		item['data'] = chart_data[i];
		label_data.push(item);
	}
	//########3. 绘图 ######
	$.plot($(obj), label_data, {
		series: {
			lines: { show: true },
			points: { show: true,
				  radius: '1.0',
				  symbol: "circle"}
		},
		colors: chart_colors,
		xaxis: {
			mode: "time",
    			timeformat: date_pattern
		},
		grid: {
			hoverable: true,
			backgroundColor: { colors: ["#fff", "#eee"] }
		}
	});
	$(obj).bind("plothover",flot_hover);

}

//获取图表数据点成功执行此函数  曲线图
function data_success(data_array){
	//注意这里的用法
	function deal_data(data){
		data = data.replace(new RegExp("NaN", 'g'), "null");
		var obj =  jQuery.parseJSON(data);  
		var monitor_data = [];
		for (var i =0;i<obj.length ;i++ ){
		    	// 每一个离散点由四个值来表示    1. 时间 2.值 
			var temp = [obj[i].time*1000,obj[i].value];
			monitor_data.push(temp);
		}
		data_array.push(monitor_data);
	}
	return deal_data;
}


//获取图表数据点失败执行此函数
function data_error(data){
    alert('获取图表数据点失败!');	
}

//自动计算横轴应该使用的时间格式
function auto_date_pattern(start, end){
	margin = end - start
	if(margin < 60*60*24*2){
		return '%H:%M'
	}else if(margin< 60*60*24*7){
		return '%m-%d %H:%M'
	}else{
		return '%m-%d'
	}
}

//在曲线上浮动时，显示曲线坐标　
function flot_hover(event, pos, item) {
	if (item) {
		if (previousPoint != item.dataIndex) {
			previousPoint = item.dataIndex;
			$("#tooltip").remove();
			var x = item.datapoint[0];
			var y = item.datapoint[1].toFixed(2);

			showTooltip(item.pageX, item.pageY,
				'(' + new Date(x-60*60*8*1000).format('MM-dd hh:mm') +',' + y + ')');
		}
	}
	else {
		$("#tooltip").remove();
		previousPoint = null;
	}
}


function showTooltip(x, y, contents) {
	$('<div id="tooltip">' + contents + '</div>').css( {
		position: 'absolute',
		display: 'none',
		top: y + 5,
		left: x + 5,
		border: '1px solid #fdd',
		padding: '2px',
		'background-color': '#dfeffc',
		opacity: 0.80
	}).appendTo("body").fadeIn(200);
}







