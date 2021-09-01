/*
Main render function contains all logic to render parse trees and tables onto the interface.

This code uses the Tabulator library, available at https://github.com/olifolkerd/tabulator. Licenced under the MIT License:

The MIT License (MIT)

Copyright (c) 2015-2020 Oli Folkerd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This code also uses the D3.js library, available at https://github.com/d3/d3. Licensed under the ISC license:


Copyright 2010-2021 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.



Part of this program is adapted from the following example from Mike Bostock: https://bl.ocks.org/mbostock/4339083. Released under the GNU Public Licnse, version 3: https://opensource.org/licenses/GPL-3.0


*/






function render(num,parses,tables,probs,svg_number){


    // setup html elements depending on wether we are rendering in svg# or svg#2
 
  if (svg_number == '1'){
    var lookup = {my_tooltip : ".my-tooltip", my_tooltip_name : "my-tooltip",tooltip : ".tooltip", tooltip_name : "tooltip", tree_box : ".tree_box", svg_id : "#svg_1",svg : "svg_1", master_buttons :"master_buttons", button: "all_button" }

  }
  else{
    var lookup = {my_tooltip : ".my-tooltip_2",tooltip : ".tooltip_2", my_tooltip_name : "my-tooltip_2", tooltip_name : "tooltip_2", tree_box :".tree_box_2", svg_id : "#svg_2",svg : "svg_2", master_buttons :"master_buttons_2", button: "all_button_2" }

  }


  // remove old tooltips and svg 
  $(lookup.my_tooltip).remove();
  $(lookup.tooltip).remove();

  d3.select(lookup.svg_id).remove();

  

  // expand/collape all buttons need resetting every time render is called - since they are called via instance attribute of render

  var all_buttons = document.getElementsByClassName(lookup.button)

  while(all_buttons[0]){
    all_buttons[0].parentNode.removeChild(all_buttons[0])
  }

  createButton(lookup.master_buttons,expandAll,"Expand all");
  createButton(lookup.master_buttons,collapseAll,"Collapse all");




  
  

  // function to render table 

  function render_table(num){
    
    var rawtabledata =  document.getElementById("derivation_tables").innerHTML
    var tabledata = JSON.parse(rawtabledata)
    var thistable = tabledata[num]
   

    var list_data = [] 

    for(var i in thistable){
      list_data.push(thistable[i])
    }

    // add rankings to elements 
    for(var i in list_data){
      list_data[i]["step"] = i
    }

    


    if (!probs){
      var table = new Tabulator("#table_box", {

        data:list_data,
    
        layout:"fitDataFill",
        // virtualDomHoz:true,
        columns:[
          {title:"step",field:"step"},
          {title:"Nonterminal expanded",field:"nonterminal"},
          {title: "Rule used",field:"rule"},
          {title:"Cumulative string", field:"current_string",formatter:"textarea"}
        ]
    
        })

    }
    else{
      var table = new Tabulator("#table_box", {

        data:list_data,
       
        layout:"fitDataFill",
        // virtualDomHoz:true,
        columns:[
          {title:"step",field:"step"},
          {title:"Nonterminal expanded",field:"nonterminal"},
          {title: "Rule used",field:"rule"},
          {title:"Rule probability",field:"probability"},
          {title:"Rule ranking",field:"rule_rank"},
          {title:"Cumulative string", field:"current_string",formatter:"textarea"}
        ]
    
        })

    }
  }

  if(tables){
    render_table(num=num)
  }




  





  var tooltip = d3.select("body")
        .append("div")
        .attr("class", lookup.my_tooltip_name)
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden");



// get the tree data from the html 
var treedata =  document.getElementById("parses").innerHTML
var data = JSON.parse(treedata)


// select the correct data
var treeData = parses[num]



// Setup SVG 

var margin = {top: 20, right: 30, bottom: 20, left: 30},
    width = 940 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

// set up the zoom object
var zoom = d3.zoom();



var vis = d3.select(lookup.tree_box)
        .append("svg:svg")
        .attr("id",lookup.svg)
        .call(zoom.on("zoom", function() {
          vis.attr("transform",d3.event.transform)
        }))
        .style("background-color","#f3e4f3")
        .style("border","solid","10px","#000000")
      .append("svg:g")
        .attr("class","drawarea")
      .append("svg:g")
        .attr("transform", "translate(" + margin.bottom + "," + margin.top + ")");
        

var i = 0,
    root,
    duration = 705;
  



// setup the tooltip 
var div = d3.select("body").append("div")
    .attr("class", lookup.tooltip_name)
    .style("opacity", 1e-6);





// Setup tree

var treestruct = d3.tree()
    .size([width, height]);

// Get the root
treedata = data[num]
root = d3.hierarchy(treedata, function(d) { return d.children; });



if (num_nodes < 40){
root.x0 =  height/2;
root.y0 = 0 ;
}
else{
  root.x0 = 0; 
  root.y0 = width / 3;
}


// collapse the tree, and then draw the root, including its immediate children
root.children.forEach(collapse);
update(root);



function update(source) {

 
  var treeData = treestruct(root);

  // Get nodes and links
  var nodes = treeData.descendants(),
      links = treeData.descendants().slice(1);


   nodes.forEach(function(d){ d.y = d.depth * 100});

 
  var node = vis.selectAll('g.node')
      .data(nodes, function(d) {return d.id || (d.id = ++i);   });




  // Setup the node entries. Slightly messy due to needing to check if we are in probablistic-mode or not and check how many nodes we have in total.
  if (probs){

    if(num_nodes < 40){
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
  }
  else{
    var nodeEnter = node
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr("transform", function(d) {
      return "translate(" + source.y0 + "," + source.x0 + ")";
    })
    .on('click',click)
    .on("mouseover",mouseover)
    .on("mouseover", mouseover)
    .on("mousemove", function(d){mousemove(d);})
    .on("mouseout", mouseout);
}

  }
  else{
    if(num_nodes < 40){
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
      .on("mousemove", function(d){mousemove_non(d);})
      .on("mouseout", mouseout);

    }
    else{
    var nodeEnter = node
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr("transform", function(d) {
      return "translate(" + source.y0 + "," + source.x0 + ")";
    })
    .on('click',click)
    .on("mouseover",mouseover)
    .on("mouseover", mouseover)
    .on("mousemove", function(d){mousemove_non(d);})
    .on("mouseout", mouseout);
  }
}




  // Add circle for each enter node

  nodeEnter.append('circle')
      .attr('class', 'node')
      .attr('r', 1e-6)
      .style("fill", function(d) {
          return d._children ? "#95c4e6" : "#fff";
      });

  // Add text to the nodes

  nodeEnter.append('text')
    .attr("dy", ".32em")
    .attr("x", function(d) {
        return d.children || d._children ? 12 : 12;
    })
    .attr("text-anchor", function(d) {
        return d.children || d._children ? "start" : "start";
    })
    .text(function(d) { return d.data.name; });

  var nodeUpdate = nodeEnter.merge(node);


  
  if (num_nodes < 40){
    nodeUpdate.select('circle.node')
    .attr('r', 10)
    .style("fill", function(d) {
        return d._children ? "#95c4e6" : "#fff";
    })

  // Transition nodes -- must check number of nodes here too!
  nodeUpdate.transition()
    .duration(duration)
    .attr("transform", function(d) { 
        return "translate(" + d.x + "," + d.y + ")";
     });

  
  
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) {
          return "translate(" + source.x + "," + source.y + ")";
      })
      .remove();
  }

  else{
    nodeUpdate.select('circle.node')
    .attr('r', 10)
    .style("fill", function(d) {
        return d._children ? "#95c4e6" : "#fff";
    })

  // Transition nodes
  nodeUpdate.transition()
    .duration(duration)
    .attr("transform", function(d) { 
        return "translate(" + d.y + "," + d.x + ")";
     });

  
  
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) {
          return "translate(" + source.y + "," + source.x + ")";
      })
      .remove();
  }

  

  // On node exit, make the size of the circle and text 0.
  nodeExit.select('circle')
    .attr('r', 1e-6);

  nodeExit.select('text')
    .style('fill-opacity', 1e-6);

  
  // Draw the links

  var link = vis.selectAll('path.link')
      .data(links, function(d) { return d.id; });
  
  

  var linkEnter = link.enter().insert('path', "g")
      .attr("class", "link")
      .attr('d', function(d){
        var o = {x: source.x0, y: source.y0}
        return diagonal(o, o)
      });

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

  // Store the old positions of the nodes.
  nodes.forEach(function(d){
    d.x0 = d.x;
    d.y0 = d.y;
  });


}




function diagonal(s, d) {

  // Function to create linked bwttn nodes, needs to be different depending on if tree is vertical of horizontal (number of nodes)

  if (num_nodes < 40){
    link_path = 
    `M ${s.x} ${s.y}
     C ${(s.x + d.x) / 2} ${s.y},
    ${(s.x + d.x) / 2} ${d.y},
    ${d.x} ${d.y}`
  }
  else{

    link_path = `M ${s.y} ${s.x}
    C ${(s.y + d.y) / 2} ${s.x},
      ${(s.y + d.y) / 2} ${d.x},
      ${d.y} ${d.x}`
  }

  return link_path
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
  
  update(d);
}

function mouseover() {
  div.transition()
  .duration(0)
  .style("opacity", 1);
}
function mousemove(d) {
  

  // Make sure to check if the node is a leaf or not, because leaf nodes need a different tooltip! 
  if(d.data.rule == 'Leaf - not applicable'){
   
    div
  .style("left", (d3.event.pageX+10) + "px")
  .style("top", (d3.event.pageY) + "px")
  .html(
      "<table style='font-size: 10px; font-family: sans-serif;' >"+
      
      "<tr><td>Leaf terminal: </td><td>"+d.data.name+"</td></tr>"+
     
      "</table>"
  );
  }
  else{
    div
    .style("left", (d3.event.pageX+10) + "px")
    .style("top", (d3.event.pageY) + "px")
    .html(
        "<table style='font-size: 10px; font-family: sans-serif;' >"+
        "<tr><td>Non-terminal: </td><td>"+d.data.name+"</td></tr>"+
        "<tr><td>Rule: </td><td>"+d.data.rule+"</td></tr>"+
        "<tr><td>Cumulative Probability: </td><td>"+d.data.cumulative_prob+"</td></tr>"+
        "<tr><td>Derivation Step: </td><td>"+d.data.step+"</td></tr>"+
        
        "</table>"
    );   

  }

    }
 



function mousemove_non(d) {
  if(d.data.rule == 'Leaf - not applicable'){
  div
  .style("left", (d3.event.pageX+10) + "px")
  .style("top", (d3.event.pageY) + "px")
  .html(
      "<table style='font-size: 10px; font-family: sans-serif;' >"+
      "<tr><td>Leaf terminal: </td><td>"+d.data.name+"</td></tr>"+
   
      
      "</table>"
  );
  }
else{
  div
  .style("left", (d3.event.pageX+10) + "px")
  .style("top", (d3.event.pageY) + "px")
  .html(
      "<table style='font-size: 10px; font-family: sans-serif;' >"+
      "<tr><td>NonTerminal: </td><td>"+d.data.name+"</td></tr>"+
      "<tr><td>Rule: </td><td>"+d.data.rule+"</td></tr>"+
      "<tr><td>Derivation Step: </td><td>"+d.data.step+"</td></tr>"+
      
      "</table>"
  );
}
}


function mouseout() {
  div.transition()
  .duration(0)
  .style("opacity", 1e-6);
}

// Add attributes to the render function to access the expand/collapse functions externally

render.expand = expand
render.expandAll = expandAll
render.collapseAll = collapseAll

// collapse and expand all button functionality
function expand(d){   
  var children = (d.children)?d.children:d._children;
  if (d._children) {        
      d.children = d._children;
      d._children = null;       
  }
  if(children)
    children.forEach(expand);
}

function collapse(d) {
  if (d.children) {
    d._children = d.children;
    d._children.forEach(collapse);
    d.children = null;
  }
}

function expandAll(){
  
  expand(root); 
  update(root);
}

function collapseAll(){
  root.children.forEach(collapse);
  collapse(root);
  update(root);
}

// creating some buttons 

function createButton(div, func,text) {
  var button = document.createElement("button");
  button.type = "button"
  button.className = lookup.button;
  button.innerHTML = text;
  button.onclick = func
 
  var master_buttons = document.getElementById(lookup.master_buttons);
  master_buttons.appendChild(button);
}
}





