var treeData =
  {
    "name": "Top Level",
    "children": [
      { 
        "name": "Level 2: A",
        "children": [
          { "name": "Son of A", "children" : [{"name" : "level3"},{ "name": "Son of A" },
          { "name": "Daughter of A" }]},
          { "name": "Daughter of A" },
          { "name": "Daughter2 of A" , "children" : [{"name" : "level3"},{ "name": "Son of A" },
          { "name": "Daughter of A" }]}
        ]
      },
      { "name": "Level 2: B",
        "children": [
          { "name": "Son of A" },
          { "name": "Daughter of A" }
        ] 
      }
    ]
  };

// Setup SVG Element - Start

var margin = {top: 20, right: 20, bottom: 30, left: 20},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var svg = d3.select("div")
        .append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)

var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// Setup SVG Element - End

var i = 0,
    duration = 750,
    root;

// Setup tree

var treemap = d3.tree()
    .size([width, height]);

// Get the root

root = d3.hierarchy(treeData, function(d) { return d.children; });

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
  var node = g.selectAll('g.node')
      .data(nodes, function(d) {return d.id || (d.id = ++i);   });


  // Let's append all enter nodes
  var nodeEnter = node
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr("transform", function(d) {
        return "translate(" + source.x0 + "," + source.y0 + ")";
      })
      .on('click',click);

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

  var link = g.selectAll('path.link')
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
  
  // Here we are just drawing lines, we can also draw curves, comment out below path for it.

  var path = `M ${s.x} ${s.y}
          L ${d.x} ${d.y}`;
  
//   var path = `M ${s.x} ${s.y}
//           C ${(s.x + d.x) / 2} ${s.y},
//             ${(s.x + d.x) / 2} ${d.y},
//             ${d.x} ${d.y}`

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
  if (d.parent) {
    d.parent.children.forEach(function(element) {
      if (d !== element) {
        collapse(element);
      }
    });
  }

  draw(d);
}

