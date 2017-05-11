
// Get the <span> element that closes the modal
//var span = document.getElementsByClassName("close")[1];

var letter = document.getElementById('myLetter');
var spanLetter = document.getElementById("letterClose");
spanLetter.onclick = function() {
    letter.style.display = "none";
};
// When the user clicks on the button, open the modal 
function openLetter(url) {
	console.log("Trying to open Letter");// Get the modal
	var letterView =  document.getElementById('letterContent');
	while ( letterView.firstChild){
		letterView.removeChild(letterView.firstChild);
	}
	var ifr = document.createElement("iframe");
	ifr.setAttribute("width","100%");
	ifr.setAttribute("height","500px");
    ifr.setAttribute("src", url);
	letterView.appendChild(ifr);
	letter.style.display = "block";
};


// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == letter) {
        letter.style.display = "none";
    }
};