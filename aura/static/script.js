function createVIS() {
	a = $.get( window.location.href+"/status", function( data ) {
		js = JSON.parse(data);
		var nodelist = [], edgelist = [];
		for (var m in js.modules ){
			var module = js.modules[m];
			for (var s in js.modules[m].scripts) {
				var script = module.scripts[s];
				var id = module.name+"/"+script.seq;
				var id_plus_one = module.name+"/"+(parseInt(script.seq)+1).toString();
				if (s == module.scripts.length-1) {
					id_plus_one = module.name+"/"+String(module.scripts.length+1)
				}
				nodelist.push({id: id, color: "gray"});
				edgelist.push({from: id, to: id_plus_one, label:id, arrows:"to", color: "gray", length:0.1});
				if (script.output) {
					for (var o in script.output) {
						edgelist.push({from: id_plus_one, arrows: "to", to: script.output[o], color: "gray", dashes: "true", length:0.15});
					}
				}
			}
			var id = module.name+"/"+String(module.scripts.length+1);
			nodelist.push({id: id, color: "gray"});
		}
		// create a network
		nodes = new vis.DataSet(nodelist);
		edges = new vis.DataSet(edgelist);
		var container = document.getElementById('viscanvas');
		var data = {
			nodes: nodes,
			edges: edges
		};
		var options = {
			//              "physics": {
			//                              "enabled": false,
			//                              "solver": "forceAtlas2Based"
			//              },
			//              "layout": {
			//                              "hierarchical": {
			//                                              "enabled":true,
			//                                              "direction": "LR",
			//                                              "sortMethod":"directed",
			//                                              "levelSeparation":100,
			//                              }
			//              }
		};
		network = new vis.Network(container, data, options);
	});
}

function updatePage() {
	$.get( window.location.href+"/status", function( data ) {
		//  $( ".result" ).html( data );
		js = JSON.parse(data);
		$( "#generalstate" ).html(js.status);
		if (js.status != "DONE") {
			$( "#generalstate" ).attr("class", "general-status-active")
		} else {
			$( "#generalstate" ).attr("class", "")
		}
		for (var m in js.modules ){
			var obj = js.modules[m];
			$( "#"+obj.name+"-address" ).html(obj.address);
			for (var s in js.modules[m].scripts) {
				var id="#"+js.modules[m].name+js.modules[m].scripts[s].seq;
				var scr_obj = js.modules[m].scripts[s];
				if(scr_obj.status) {
					$( id+"-status" ).html(scr_obj.status);
					$( id+"-status" ).attr("class", "script-span");
					$( id+"-status" ).addClass(scr_obj.status.toLowerCase());
					$( id+"-runs" ).html(scr_obj.runs);
					$( id+"-elapsed_time" ).html(Math.round(scr_obj.elapsed_time*100)/100);
					$( id+"-snap_time" ).html(Math.round(scr_obj.snap_time*100)/100);
				}
			}
		}
		$( "#allocating_resources_time" ).html(Math.round(js.allocating_resources_time*100)/100);
		$( "#booting_time" ).html(Math.round(js.booting_time));
		$( "#running_time" ).html(Math.round(js.running_time*100)/100);

		// update the VIS network
		keys = {};
		for (m in js.modules) {
			var last_status = "";
			for ( s in js.modules[m].scripts) {
				keys[js.modules[m].name+"/"+js.modules[m].scripts[s].seq] = js.modules[m].scripts[s].status
				last_status = js.modules[m].scripts[s].status
			}
			keys[js.modules[m].name+"/"+String(js.modules[m].scripts.length+1)] = last_status
		}

		for (var x in edges.get()) {
			current = edges.get()[x];
			color = "#333333";
			if(current.dashes) {		// that's a message edge
					var splitted_name = current.from.split("/");
					var suffix = splitted_name[1];
					prev_id = splitted_name[0]+"/"+String(parseInt(suffix)-1);
					if(keys[prev_id] == "DONE") {
						color="#4CAF50";
						current.color =  color;
						edges.update(current);
					}
			} else if (keys[current.from] == "DONE" ) {	// everything else is a script edge
				color="#4CAF50";
				current.color =  color;
				edges.update(current);

				a = nodes.get(current.to)
				a.color = {background: color};
				nodes.update(a);

				b = nodes.get(current.from)
				b.color = {background: color};
				nodes.update(b);

			}else if (keys[current.from] == "EXECUTING" ) {
				color="#3333FF";
				current.color =  color;
				edges.update(current);

				a = nodes.get(current.to)
				a.color = {background: color};
				nodes.update(a);

				if (current.from.split("/")[1] == "1") { // if a script is executed, the primary state is cool
					b = nodes.get(current.from)
					b.color = {background: "#4CAF50"};
					nodes.update(b);
				}

			}else if (keys[current.from] == "ERROR" ) {
				color="#FF3333";
				current.color =  color;
				edges.update(current);

				a = nodes.get(current.to)
				a.color = {background: color};
				nodes.update(a);
			}else if (keys[current.from] == "WAITING_FOR_MESSAGE") { // just yellow the node
				color="#cccc00";
				b = nodes.get(current.from)
				b.color = {background: color};
				nodes.update(b);
			}
		}

	});
}

function create_alert(app_id) {
	$.get("/application/"+app_id+"/json", function (data) {
		var finalDiv = "<div><table>";
		js = JSON.parse(data);
		var ids = [];
		for (i in js.modules) {
			var current_id = js.modules[i].name;
			ids.push(current_id);
			var multi = 1;
			if (js.modules[i].multiplicity>1) {
				multi = js.modules[i].multiplicity
			}
			finalDiv = finalDiv + ("<tr><td>"+js.modules[i].name +"</td><td><input id='"+current_id+"' type='text' value="+multi+"></input></td></tr>");
		}
		finalDiv = finalDiv+"<tr><td></td><td><button style='float:right;' onclick='my_dialog_handler(\""+ids+"\", \""+app_id+"\")' class='ui-button ui-widget ui-corner-all'>Deploy</button></td></tr>";
		finalDiv = finalDiv+ "</table>";
		finalDiv = finalDiv+"</div>";
		$( finalDiv ).dialog({height: "auto", width: "auto", title: "Number of VMs"});
	});
}

function my_dialog_handler(ids, app_id) {
	var url = "/application/"+app_id+"/deploy?";
	var ids_split = ids.split(",");
	for (i in ids_split ) {
		url = url + ids_split[i] +"="+$( "#"+ids_split[i] ).val();
		if (i < ids_split.length -1 ){
			url = url+"&";
		}
	}
	window.location.href = url;
}



function show_logs(script) {
	var a= script.split("/");
	var module_name = a[0], script_seq = parseInt(a[1]);
	var finalDiv = "<div>";
	finalDiv = finalDiv + "<textarea class='console' readonly>";
	a = $.get( window.location.href+"/status", function( data ) {
		js = JSON.parse(data);
		for (i in js.modules){
			for (j in js.modules[i].scripts) {
				if (js.modules[i].name == module_name && js.modules[i].scripts[j].seq == script_seq) {
					finalDiv = finalDiv + js.modules[i].scripts[j]["file-content"];
				}
			}
		}
		finalDiv = finalDiv + "</textarea>";
		finalDiv = finalDiv + "</div>";
		$( finalDiv ).dialog({height:"auto", width:"600px", title: script+" content"})
	})
}
