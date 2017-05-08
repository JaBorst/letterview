/* send XMLHTTP request to the local server 127.0.0.1:8887 for the query of sqlite db, it seems the only way to bind sqlite database and html as far as I know for now, and 'sql.js' must be downloaded and included, if back-end server is built, this step can be skipped, all the infos can be transfered to the front via json data*/
console.log("Creating Timeline");
var xhr = new XMLHttpRequest();
xhr.open('GET', 'http://0.0.0.0:5000/db', true);
xhr.responseType = 'arraybuffer';

xhr.onload = function(e) {
  console.log(this.response);
  var uInt8Array = new Uint8Array(this.response);   
  var db = new SQL.Database(uInt8Array);
  contents = db.exec("SELECT * FROM letters LIMIT 10"); // show the contents of table letters
  // contents is now [{columns:['col1','col2',...], values:[[first row], [second row], ...]}]

  //console.log(contents[0].values.length);
  contentsLen = contents[0].values.length;
  var direction;
  var author;
  var monthAbbr = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."];
  /* the letters from goethe are on the left of timeline, schiller on the right, the direction is decided by the 7th paramether of each letter object,
  but some of them are not correct I think(not sure), and many dates (parameter 2,3,4) are not correct also*/
  for (var i=0; i< contentsLen; i++) {

    console.log(contentsLen);
    if (contents[0].values[i][7]=="G") {
      direction = "direction-l";
      author = "Goethe" ;
    } else {
      direction = "direction-r";
      author = "Schiller"; 
    }
    var dayThisLetter = contents[0].values[i][2] * 365 + contents[0].values[i][3] * 30 + contents[0].values[i][4];
    var dayNextLetter = contents[0].values[i+1][2] * 365 + contents[0].values[i+1][3] * 30 + contents[0].values[i+1][4];
    var intervalTwoLetters = dayNextLetter - dayThisLetter;
    /*the space between two vertical adjacent letters is ajusted according to the time difference, each day for 5px*/
    var correspondingPaddingBottomNum = Math.abs(intervalTwoLetters * 5 + 18);
    if (correspondingPaddingBottomNum > 1000) {
      correspondingPaddingBottomNum = 150;
    }
    var correspondingPaddingBottom = correspondingPaddingBottomNum + "px";
    var dateTime = contents[0].values[i][4] + "&nbsp&nbsp" + monthAbbr[parseInt(contents[0].values[i][3])-1] + "&nbsp" + contents[0].values[i][2];
    linkUrl = contents[0].values[i][6];
    letterContent = contents[0].values[i][5].slice(0, 200);
    $("#mainTimeLine").append("<li style='padding-bottom:"+ correspondingPaddingBottom +"'><div class='"+direction+"'><div class='flag-wrapper'><span class='flag'>"+author+"</span><span class='time-wrapper'><span class='time'>"+dateTime+"</span></span></div><div class='desc'>"+letterContent+"..."+"<a href='"+linkUrl+"' target='_blank'>Mehr dazu</a></div></div></li>");
  }
};
xhr.send();