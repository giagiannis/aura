var nodes, edges;
var network;
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
										id_plus_one = module.name+"/end"
								}
								nodelist.push({id: id, color: "gray"});
								edgelist.push({from: id, to: id_plus_one, label:id, arrows:"to", color: "gray", length:0.1});
								if (script.output) {
										for (var o in script.output) {
												edgelist.push({from: id_plus_one, arrows: "to", to: script.output[o], color: "gray", dashes: "true", length:0.15});
										}
								}
						}
						var id = module.name+"/end";
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
								$( id+"-status" ).html(scr_obj.status);
								$( id+"-status" ).attr("class", "script-span");
								$( id+"-status" ).addClass(scr_obj.status.toLowerCase());
								$( id+"-runs" ).html(scr_obj.runs);
								$( id+"-elapsed_time" ).html(Math.round(scr_obj.elapsed_time*100)/100);
						}
				}
				$( "#allocating_resources_time" ).html(Math.round(js.allocating_resources_time*100)/100);
				$( "#booting_time" ).html(Math.round(js.booting_time));
				$( "#running_time" ).html(Math.round(js.running_time*100)/100);

				// update the VIS network
				keys = {};
				for (m in js.modules) {
						for ( s in js.modules[m].scripts) {
								keys[js.modules[m].name+"/"+js.modules[m].scripts[s].seq] = js.modules[m].scripts[s].status
						}
				}
				for (var x in edges.get()) {
						current = edges.get()[x];
						color = "#333333";
						if (keys[current.from] == "DONE" ) {
								color="#4CAF50";
						}else if (keys[current.from] == "EXECUTING") {
								color="#3333FF";
						}else if (keys[current.from] == "ERROR") {
								color="#FF3333";
						}else if (keys[current.from] == "WAITING_FOR_MESSAGE") {
								color="#cccc00";
						}
						current.color =  color;
						edges.update(current);

						a = nodes.get(current.to)
						a.color = {background: color};
						nodes.update(a);

						b = nodes.get(current.from)
						b.color = {background: color};
						nodes.update(b);
				}

		});
}


createVIS();
updatePage();
setInterval(updatePage, 500);