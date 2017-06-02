


var result;

// Get the modal
var modal = document.getElementById('myModal');
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal 
function openModal() {
    modal.style.display = "block";
};

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

function addDateInput(n){
	var modContent = document.getElementById('DateSelection');
	modContent.innerHTML = '';
	console.log("number of corpus" + n);
	if (n > 10){
		modContent.innerHTML = "Too much splits";
		exit();
	}
	
	for (i=1; i<Number(n)+1; i++){
		line = 'Corpus ' + i + ' start: <input name="Corpus'+i+'-start" type="date" min="1794-06-13" max="1805-12-31" value="1794-06-13"></input> '
				+'end: <input name= "Corpus'+i+'-end" type="date"  min="1794-06-13" max="1805-12-31"  value="1794-12-31"></input><br>';
		modContent.innerHTML += line;
	}
}

function hashCode(str) { // java String#hashCode
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
       hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return hash;
} 

function intToRGB(i){
    var c = (i & 0x00FFFFFF)
        .toString(16)
        .toUpperCase();

    return "00000".substring(0, 6 - c.length) + c;
}
function CorpusSelectionSubmit(){
	console.log("submit the corpusdates");
	
	 event.preventDefault();
	myForm = document.getElementById("CorpusSelectionForm");
	var formData = new FormData(myForm);
	result = {};

    for (var entry of formData.entries())
    {
		if(result.hasOwnProperty(entry[0].split('-')[0])){
			result[entry[0].split('-')[0]][entry[0].split('-')[1]]=entry[1];
		}else{
			result[entry[0].split('-')[0]]={};
			result[entry[0].split('-')[0]][entry[0].split('-')[1]]=entry[1];
		}
		console.log(entry);
    }
	console.log(JSON.stringify(result));
	modal.style.display = "none";
	updateApplicationWindow();
}

function updateApplicationWindow(){
	createWordCloud();
	
}

function CreateParallelWordClouds(j){
	console.log("Creating wordclouds");
	
	var api = "http://0.0.0.0:5000/ptagcloudapi";
	var xhr = new XMLHttpRequest();
	xhr.open('POST', 'http://0.0.0.0:5000/ptagcloudapi', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.onload = function(e) {
		console.log("wordcloud xhr-onload");

		//Cleaning the Application node
		
		node = document.getElementById("app");
		while (node.firstChild) {
			node.removeChild(node.firstChild);
		}
		var table = document.createElement("table");
		table.setAttribute("id","wordcloudtable");
		row = document.createElement("tr");
		table.appendChild(row);
		node.appendChild(table);
		console.log(JSON.parse(this.response));
		var objResponse = JSON.parse(this.response);
		
		//LOOP ADDING THE WORD COLUMNS
		colors= ["#FFFFFF", "#DDDDDD"];
		var i = 0;
		for (var corp in objResponse){
			console.log(objResponse[corp]);
			var col = document.createElement("td");
			i = (i+1) % 2;
			//col.setAttribute("bgcolor", colors[i]);
			for (var w in objResponse[corp]){
				console.log(w)
				var entry = document.createElement("tr");
				entry.innerHTML += w;
				var colorEntry = intToRGB(hashCode(w));
				console.log(colorEntry);
				entry.style.backgroundColor = "#" + colorEntry;
				col.append(entry);
			}
		row.appendChild(col);

		}
	}
	
	
	xhr.send(JSON.stringify(result));	
	console.log("Wordclouds Created");	
}


