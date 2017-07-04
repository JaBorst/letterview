var layout;

function createWordCloud(){
	
	
	console.log("Creating Simple Word Cloud");
	console.log(result);
	
	
	
	
	
	
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/tagcloudapi', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.onload = function(e) {
		//Empty Space
		node = document.getElementById("app");
		while (node.firstChild) {
			node.removeChild(node.firstChild);
		}
		//Parse Response
		console.log("wordcloud xhr-onload");
		var objResponse = JSON.parse(this.response);
		var corpusCount=0;
		//console.log("objResponse: ",objResponse);
		var table = document.createElement("table");
		node.appendChild(table);
		var currentRow ;
		for (var corp in objResponse){
			var words = objResponse[corp];
			//console.log(words.value);
			corpusCount += 1;

			if (corpusCount % 2 === 1){
				currentRow  = document.createElement("tr");
				table.appendChild(currentRow);
			}
			
			var currentField = document.createElement("td");
			currentField.setAttribute("id", corp);
			currentFieldID = corp;
			currentRow.appendChild(currentField);

			wordMap = words.map( function(d) { return {text: d.word, size: d.freq, test: "haha"}; } ) ; 
			console.log(wordMap);
			layout= d3.layout.cloud()
			   .size([300, 300])
			   .words(wordMap)
			   .padding(5)
			   .font("Impact")
			   .fontSize(function(d) { return d.size; })
			   .on("end", draw);
	   
			layout.start();
		}
		
		
		
	};
	xhr.send(JSON.stringify(result));
}
function draw(words) {
	console.log("draw has " + currentFieldID);
	d3.select("#"+currentFieldID).append("svg")
      .attr("width", layout.size()[0])
      .attr("height", layout.size()[1])
    .append("g")
      .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
    .selectAll("text")
      .data(words)
    .enter().append("text")
      .style("font-size", function(d) { return d.size + "px"; })
      .style("font-family", "Impact")
      .attr("text-anchor", "middle")
      .attr("transform", function(d) {
        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
      })
      .text(function(d) { return d.text; });
}