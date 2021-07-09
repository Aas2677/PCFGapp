function render(num,parses,tables){

 


  


  // remove old tooltips and svg 
  $(".my-tooltip").remove();
  $(".tooltip").remove();

  d3.select("svg").remove();


  // function to render table 

  function render_table(num){
    
    var rawtabledata =  document.getElementById("derivation_tables").innerHTML
    var tabledata = JSON.parse(rawtabledata)
    var thistable = tabledata[num]
    // console.log(thistable)

    var list_data = [] 

    for(var i in thistable){
      list_data.push(thistable[i])
    }

    // add rankings to elements 
    for(var i in list_data){
      list_data[i]["step"] = i
    }

    console.log(list_data)


    var sortValueAscending = function (a, b) { return valueFunc(a) - valueFunc(b) }
    var sortValueDescending = function (a, b) { return valueFunc(b) - valueFunc(a) }
    var sortNameAscending = function (a, b) { return textFunc(a).localeCompare(textFunc(b)); }
    var sortNameDescending = function (a, b) { return textFunc(b).localeCompare(textFunc(a)); }
    var metricAscending = true;
    var nameAscending = true;






     // some setup for the tables 
     var table = document.getElementById("table_box");
     var width = table.offsetWidth 
     var height = table.offsetHeight 

     var tablewidth = (width - 25) +"px";
     var dheight = (height-60) + "px";
     

     var columns = ["nonterminal","rule","rule_rank","current_string"]

     var valueFunc = function(data) { return data.value; }
     var textFunc = function(data) { return data.fullname; }


     var outerTable = d3.select("#table_box").append("table").attr("width", width+"px");

     outerTable.append("tr").append("td")
        .append("table").attr("class", "headerTable").attr("width", tablewidth)
        .append("tr").selectAll("th").data(columns).enter()
		    .append("th").text(function (column) { return column; })
        .on("click", function (d) {
            // Choose appropriate sorting function.
            if (d === columns[1]) {
			    var sort = metricAscending ? sortValueAscending : sortValueDescending;
                metricAscending = !metricAscending;
            } else if(d === columns[0]) {
				var sort = nameAscending ? sortNameAscending : sortNameDescending
                nameAscending = !nameAscending;
            }
			
            var rows = tbody.selectAll("tr").sort(sort);
        });

     var inner = outerTable.append("tr").append("td")
        .append("div").attr("class", "scroll").attr("width", width+"px").attr("style", "height:" + dheight + ";")
        .append("table").attr("class", "bodyTable").attr("border", 1).attr("width", tablewidth).attr("height", height+"px").attr("style", "table-layout:fixed");
    

     var tbody = inner.append("tbody");
      // Create a row for each object in the data and perform an intial sort.
     var rows = tbody.selectAll("tr").data(list_data).enter().append("tr").sort(sortValueDescending);

     var cells = rows.selectAll("td")
        .data(function (d) {
            return columns.map(function (column) {
                return { column: column, text: textFunc(d), value: valueFunc(d)};
            });
          }).enter().append("td")
		      .text(function (d) {
			         if (d.column === columns[0]) return d.text;
			         else if (d.column === columns[1]) return d.value;
		        });

      
    
  
    




  }

  if(tables){
    render_table(num=num)
  }




  




  var tooltip = d3.select("body")
        .append("div")
        .attr("class", "my-tooltip")//add the tooltip class
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden");



// get the tree data from the html 
var treedata =  document.getElementById("parses").innerHTML
var data = JSON.parse(treedata)





// update the tree button 


// console.log(data["1"])

var treeData = parses[num]



// Setup SVG Element - Start

var margin = {top: 20, right: 30, bottom: 20, left: 30},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var zoom = d3.zoom();


var vis = d3.select(".tree_box")
        .append("svg:svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .call(zoom.on("zoom", function() {
          vis.attr("transform",d3.event.transform)
        }))
        .style("background-color","#f3e4f3")
      .append("svg:g")
        .attr("class","drawarea")
      .append("svg:g")
        .attr("transform", "translate(" + margin.bottom + "," + margin.top + ")");
        

var i = 0,
    duration = 750,
    root;



// setup the tooltip 
var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 1e-6);





// Setup tree

var treemap = d3.tree()
    .size([width, height]);

// Get the root



treedata = data[num]
root = d3.hierarchy(treedata, function(d) { return d.children; });

root.x0 = 0;
root.y0 = width / 3;

   // Collapse all children, except root's

root.children.forEach(collapse);
   // root.children = null;

   // Let's draw the tree
draw(root);


// console.log(root);

function draw(source) {

  // Get the treemap, so that we can get nodes and links
  var treeData = treemap(root);

  // Get nodes and links
  var nodes = treeData.descendants(),
      links = treeData.descendants().slice(1);

  // Adjust the position of y of each node. Comment out just this line and see how it's different  
  nodes.forEach(function(d){ d.y = d.depth * 100});

  // Add unique id for each node, else it won't work
  var node = vis.selectAll('g.node')
      .data(nodes, function(d) {return d.id || (d.id = ++i);   });


  // Let's append all enter nodes
  var nodeEnter = node
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr("transform", function(d) {
        return "translate(" + source.x0 + "," + source.y0 + ")";
      })
      .on('click',click)
      .on("mouseover",mouseover)
      .on("mouseover", mouseover)
      .on("mousemove", function(d){mousemove(d);})
      .on("mouseout", mouseout);

  // Add circle for each enter node, but keep the radius 0

  nodeEnter.append('circle')
      .attr('class', 'node')
      .attr('r', 1e-6)
      .style("fill", function(d) {
          return d._children ? "lightsteelblue" : "#fff";
      });

  // Add text

  nodeEnter.append('text')
    .attr("dy", ".35em")
    .attr("x", function(d) {
        return d.children || d._children ? -13 : 13;
    })
    .attr("text-anchor", function(d) {
        return d.children || d._children ? "end" : "start";
    })
    .text(function(d) { return d.data.name; });

  // https://github.com/d3/d3-selection/issues/86 to check what merge does
  var nodeUpdate = nodeEnter.merge(node);

  // Do transition of node to appropriate position
  nodeUpdate.transition()
    .duration(duration)
    .attr("transform", function(d) { 
        return "translate(" + d.x + "," + d.y + ")";
     });
  


  // Let's update the radius now, which was previously zero.

  nodeUpdate.select('circle.node')
    .attr('r', 10)
    .style("fill", function(d) {
        return d._children ? "lightsteelblue" : "#fff";
    })
    .attr('cursor', 'pointer');

  // Let's work on exiting nodes
  
  // Remove the node
  
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) {
          return "translate(" + source.x + "," + source.y + ")";
      })
      .remove();

  // On exit reduce the node circles size to 0
  nodeExit.select('circle')
    .attr('r', 1e-6);

  // On exit reduce the opacity of text labels
  nodeExit.select('text')
    .style('fill-opacity', 1e-6);

  
  // Let's draw links

  var link = vis.selectAll('path.link')
      .data(links, function(d) { return d.id; });
  
  // Work on enter links, draw straight lines

  var linkEnter = link.enter().insert('path', "g")
      .attr("class", "link")
      .attr('d', function(d){
        var o = {x: source.x0, y: source.y0}
        return diagonal(o, o)
      });

  // UPDATE
  var linkUpdate = linkEnter.merge(link);

  // Transition back to the parent element position, now draw a link from node to it's parent
  linkUpdate.transition()
      .duration(duration)
      .attr('d', function(d){ return diagonal(d, d.parent) });

  // Remove any exiting links
  var linkExit = link.exit().transition()
      .duration(duration)
      .attr('d', function(d) {
        var o = {x: source.x, y: source.y}
        return diagonal(o, o)
      })
      .remove();

  // Store the old positions for transition.
  nodes.forEach(function(d){
    d.x0 = d.x;
    d.y0 = d.y;
  });


}

function diagonal(s, d) {
  
  
  var path = `M ${s.x} ${s.y}
          C ${(s.x + d.x) / 2} ${s.y},
            ${(s.x + d.x) / 2} ${d.y},
            ${d.x} ${d.y}`

  return path
}



function collapse(d) {
  if(d.children) {
    d._children = d.children
    d._children.forEach(collapse)
    d.children = null
  }
}

function click(d)
{
  if (d.children) {
      d._children = d.children;
      d.children = null;
    } else {
      d.children = d._children;
      d._children = null;
    }
  // If d has a parent, collapse other children of that parent
  // if (d.parent) {
  //   d.parent.children.forEach(function(element) {
  //     if (d !== element) {
  //       collapse(element);
  //     }
  //   });
  // }

  draw(d);
}

function mouseover() {
  div.transition()
  .duration(0)
  .style("opacity", 1);
}
function mousemove(d) {
  div
  .style("left", (d3.event.pageX+10) + "px")
  .style("top", (d3.event.pageY) + "px")
  .html(
      "<table style='font-size: 10px; font-family: sans-serif;' >"+
      "<tr><td>NonTerminal: </td><td>"+d.data.name+"</td></tr>"+
      "<tr><td>Rule: </td><td>"+d.data.rule+"</td></tr>"+
      "<tr><td>Cumulative Probability: </td><td>"+d.data.cumulative_prob+"</td></tr>"+
      "<tr><td>Derivation Step: </td><td>"+d.data.step+"</td></tr>"+
      
      "</table>"
  );
}
function mouseout() {
  div.transition()
  .duration(0)
  .style("opacity", 1e-6);
}


}