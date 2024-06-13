<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <title>セキュリティ</title>
    <link rel="icon" href="S-favicon.ico">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
<style>

#video_id {
	width: 400px;
	height: 220px;
	margin: 0 auto;
	text-align: center;
}

</style>
<script>
// play cue video
function CueVideo( movie_file, seconds) {

	movie_url = movie_file;

	// setting video parameters
	var video = document.getElementById("video_id" );
	video.pause();
	video.src = movie_url;
	// load video file
	video.load();
	video.addEventListener("loadeddata", function() {
		video.currentTime = seconds;
		video.play();
	}, false);

}

</script>
</head>

<body>

<?php

// get a query from index.html
$query = $_GET['query'];

$client = $_SERVER['REMOTE_ADDR'];

$data = $query . "<sep>" . $client;

// display search sentence
echo "<div align='center'>search statement：$query<br /><br />\n";
ob_flush();
flush();

// cerate socket
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);

// connect server
$address = '192.168.13.250';
//$address = '127.0.0.1';
$port = 10000;
$result = socket_connect($socket, $address, $port);

if ($result === false) {
    echo "socket_connect() failed.\n";
    exit;
}

// send message
socket_write($socket, $data, strlen($data));


// recieve response from server
$n = 0;
while(true){
    $response = socket_read($socket, 1024);
    if ( strncmp( $response, 'end', strlen( "end" ) ) == 0 ){
        break;
    }
    
    // split with <sep>
    $res_split = explode( "<sep>", $response );
    
    // Store the document name, search result text, and likelihood value in array1.
    $array1[$n][0] = $res_split[0];
    $array1[$n][1] = $res_split[1];
    $array1[$n][2] = $res_split[2];
    $array1[$n][3] = $res_split[3];

    $n++;
    label1:
  }


// display
echo "<table border='1px'>\n";

for ($n=0; $n < count($array1); $n++) {
    $movie_url = str_replace(  "\\", "/", $array1[$n][0] );
    
    echo '<tr><td width="200px">' . $movie_url . '</td><td width="600px">'. $array1[$n][2] . '</td><td><a href="javascript:void(0);" onClick="CueVideo( \'' . $movie_url . '\',' . $array1[$n][1] . ')">cue</a></td></tr>';
    echo "\n";
}



echo "</table>\nsearch end\n</div>";


// close socket
socket_close($socket);
?>

<!-- display video -->
<center><video id="video_id" controls>
    <source src="movies/Bee - 39116.mp4" type="video/mp4" >
</video></center>



</body>
</html>