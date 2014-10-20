function hostgroup_error() {
	alert("something is error!");
}

function change_host_search() {
	var url = "/hostgroup/changehostsearch";
	var ip_list = $("#ip_list").val();
	var data = {'ip_list': ip_list};
	
    jQuery.ajax({
		type: 'GET',
		url: url,
		data: data,
		success: function(data) {
			var i = 0;
			var available_ip = [];
			var chosen_ip = [];
			
			for (i = 0; i < data["available_ip"].length; i++) {
				available_ip.push({"value": data["available_ip"][i], "content": data["available_ip"][i]});
			}
			for (i = 0; i < data["chosen_ip"].length; i++) {
				chosen_ip.push(data["chosen_ip"][i]);
			}
			
			$('#change_host_transfer').html("");
			var t = $('#change_host_transfer').bootstrapTransfer({
				'target_id': 'multi-select-input',
				'height': '15em',
				'hilite_selection': true
			});
			
			t.populate(available_ip);
			t.set_values(chosen_ip);
		},
		error: hostgroup_error,
		dataType: 'json',
		async: false
	});
}

function copy_from_search() {
	var url = "/hostgroup/copyfromsearch";
	var gid = $("#copy_from_gid").val();
	var ip_list = $("#ip_list").val();
	var data = {'gid': gid, 'ip_list': ip_list};
	
    jQuery.ajax({
		type: 'GET',
		url: url,
		data: data,
		success: function(data) {
			var i = 0;
			var available_ip = [];
			
			for (i = 0; i < data.length; i++) {
				available_ip.push({"value": data[i], "content": data[i]});
			}
			
			$('#copy_from_transfer').html("")
			var t = $('#copy_from_transfer').bootstrapTransfer({
				'target_id': 'multi-select-input',
				'height': '15em',
				'hilite_selection': true
			});

			t.populate(available_ip);
		},
		error: hostgroup_error,
		dataType: 'json',
		async: false
	});
}

function move_to_search() {
	var url = "/hostgroup/movetosearch";
	var gid = $("#move_to_gid").val();
	var saved_ip_list = $("#saved_ip_list").val()
	var data = {'gid': gid, 'saved_ip_list': saved_ip_list};
	
    jQuery.ajax({
		type: 'GET',
		url: url,
		data: data,
		success: function(data) {
			if (gid == "") {
				$("#move_to_save_btn").attr("disabled", "disabled");
			} else {
				$("#move_to_save_btn").removeAttr("disabled");
			}
			
			var i = 0;
			var available_ip = [];
			
			for (i = 0; i < data.length; i++) {
				available_ip.push({"value": data[i], "content": data[i]});
			}
			
			$('#move_to_transfer').html("")
			var t = $('#move_to_transfer').bootstrapTransfer({
				'target_id': 'multi-select-input',
				'height': '15em',
				'hilite_selection': true
			});

			t.populate(available_ip);
		},
		error: hostgroup_error,
		dataType: 'json',
		async: false
	});
}

function change_host_save() {
	var url = "/hostgroup/changehostsave/";  // POST必须要有最后的slash
	var new_ip_list = $('#change_host_transfer').data().bootstrapTransfer.get_values();
	var data = {'new_ip_list': new_ip_list.join(',')};
	
	jQuery.ajax({
		type: 'POST',
		url: url,
		data: data,
		success: function(data) {
			$("#ip_list").val(data["ip_list"].join(','));
			render_ip_range_list(data["ip_range_list"]);
		},
		error: hostgroup_error,
		dataType: 'json',
		async: false
	});
}

function copy_from_save() {
	var url = "/hostgroup/copyfromsave/";
	var old_ip_list = $("#ip_list").val();
	var new_ip_list = $('#copy_from_transfer').data().bootstrapTransfer.get_values();
	var data = {'old_ip_list': old_ip_list, 'new_ip_list': new_ip_list.join(',')};
	
	jQuery.ajax({
		type: 'POST',
		url: url,
		data: data,
		success: function(data) {
			$("#ip_list").val(data["ip_list"].join(','));
			render_ip_range_list(data["ip_range_list"]);
		},
		error: hostgroup_error,
		dataType: 'json',
		async: false
	});
}

function move_to_save() {
	var url = "/hostgroup/movetosave/";
	var cur_gid = $("#cur_gid").val();  // 当前主机组的ID
	var move_to_gid = $("#move_to_gid").val();  // 选中主机组的ID
	var move_type = $("input[name='move_type']:checked").val();  // 0:复制, 1:移出
	var old_ip_list = $("#ip_list").val();
	var saved_ip_list = $("#saved_ip_list").val();
	var move_ip_list = $('#move_to_transfer').data().bootstrapTransfer.get_values();
	
	var data = {
			'cur_gid': cur_gid, 
			'move_to_gid': move_to_gid, 
			'move_type': move_type, 
			'old_ip_list': old_ip_list,
			'saved_ip_list': saved_ip_list,
			'move_ip_list': move_ip_list.join(',')
	};
	
    jQuery.ajax({
		type: 'POST',
		url: url,
		data: data,
		success: function(data) {
			if (move_ip_list.length > 0) {
				if (move_type == "0") {
					alert("复制成功！");
				} else if (move_type == "1") {
					alert("移出成功！");
				}

				$("#ip_list").val(data["ip_list"].join(','));
				$("#saved_ip_list").val(data["saved_ip_list"].join(','));
				render_ip_range_list(data["ip_range_list"]);
			}
		},
		error: hostgroup_error,
		dataType: 'json',
		async: false
	});
}

function manual_add_save() {
	var url = "/hostgroup/manualaddsave/";
	var old_ip_list = $("#ip_list").val();
	var manual_ip_list = $('#manual_ip_list').val();
	var data = {'old_ip_list': old_ip_list, 'manual_ip_list': manual_ip_list};
	
    jQuery.ajax({
		type: 'POST',
		url: url,
		data: data,
		success: function(data) {
			if (data["wrong_ip_list"].length > 0) {
				alert("以下IP地址输入有误，未被添加：\n" + data["wrong_ip_list"].join(',') + "\n\n其余IP已添加至列表中！");
			}
			
			$("#ip_list").val(data["ip_list"].join(','));
			$("#manual_ip_list").val("");
			render_ip_range_list(data["ip_range_list"]);
		},
		error: hostgroup_error,
		dataType: 'json',
		async: false
	});
}

function render_ip_range_list(data) {
	$("#ip_range_list").html("");
	var i = 0;
	for (i = 0; i < data.length; i++) {
		var t = "";
		if (data[i]["type"] == "single") {
			t = data[i]["start_ip"];
		} else if (data[i]["type"] == "continuous") {
			t = data[i]["start_ip"] + "&nbsp;-&nbsp;" + data[i]["end_ip"];
		}
		$("#ip_range_list").append("<tr><td>" + t + "</tr></td>");
	}
	if (data.length == 0) {
		$("#ip_range_list").append("<tr><td>暂无主机</tr></td>");
	}
}