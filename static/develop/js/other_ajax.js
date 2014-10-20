//  报表搜索查询操作
function displayCallback(obj){
	//校验失败，直接返回
	if(!$(obj).valid()){
		alert("表单校验失败，无法提交!");
		return false;
	}
	var url = $(obj).attr("action");
	jQuery.ajax({
		type: 'GET',
		url: url,
		data:$(obj).serializeArray(),
		success: display_success,
		error:error,
		dataType:'html',
		async:false
	});
	return false;
}

function display_success(data){
	$(".display_chart").remove();
	$("#content").append(data);
	$(".flotchart").each(function(){drawLineChart(this);});
}

// 时间选择的快捷方式
function show_span_click(){
	var show_type = $(this).attr('show_type');
	// 1:4小时, 2: 1天, 3: 3天, 4:1周, 5:1个月 
	var span_array = {'1':60*60*4, '2':60*60*24, '3':60*60*24*3, '4':60*60*24*7, '5':60*60*24*30};
	var endTime = new Date().getTime(); // 单位毫秒
	var startTime = endTime - span_array[show_type]*1000;
	$("#start_time").val(new Date(startTime).format('yyyy-MM-dd hh:mm'));
	$("#end_time").val(new Date(endTime).format('yyyy-MM-dd hh:mm'));
}


function drill_down(){
	var anOpen = [];
	$('#drill_down td.control').live( 'click', function () {
		  var nTr = this.parentNode;
		  var i = $.inArray( nTr, anOpen );
		  if ( i === -1 ) {
		    	anOpen.push( nTr );
			$('img', this).attr( 'src', "/static/img/details_close.png" );
			$('div.innerDetails', $(nTr).next()[0]).slideDown();
		    
		  }
		  else {
			anOpen.splice( i, 1 );
			$('img', this).attr( 'src', "/static/img/details_open.png" );
			$('div.innerDetails', $(nTr).next()[0]).slideUp();
		  }
	} );
}



