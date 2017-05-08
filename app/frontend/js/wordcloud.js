
node = document.getElementById("wordcloud");

table = document.createElement("table");
head = document.createElement("tr");
body = document.createElement("tr");


table.setAttribute("id","wordcloudtable");
head.setAttribute("id","wordcloudhead");
body.setAttribute("id","wordcloudbody");


table.appendChild(head);
table.appendChild(body);
head.innerHTML = '<button id="myBtn">Select Corpus</button>'
					+ '<!-- The Modal --><div id="myModal" class="modal">'
					+ '<!-- Modal content --><div class="modal-content">'
					+ '<span class="close">&times;</span><p>Some text in the Modal..</p>'
					+ '</div></div>';

// Get the modal
var modal = document.getElementById('myModal');


// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal 
btn.onclick = function() {
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

body.appendChild(document.createTextNode("hello"));

node.appendChild(table);

function CreateWordClouds(j){
	console.log("Creating wordclouds");
	
	var api = "http://0.0.0.0:5000/ptagcloudapi";
	
	
	
	
	
	
	var xhr = new XMLHttpRequest();
	xhr.open('POST', 'http://0.0.0.0:5000/ptagcloudapi', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.onload = function(e) {
		console.log("wordcloud xhr-onload");
		console.log(this.response)
		//node.innerHTML= this.response;
	}
	
	
	xhr.send(JSON.stringify({name:"John Rambo", time:"2pm"}));	
	console.log("Wordclouds Created");	
}


CreateWordClouds();