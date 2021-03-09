<?php

session_start();

if(!isset($_SESSION['userID'])){
    header("Location: ../");
    exit;
}
include '../../../Constants/index.php';
$link=mysqli_connect($server,$user,$pass,$db);

$dataPoints1=array();
$dataPoints2=array();

if(!mysqli_connect_error()){
	$query="SELECT `timestamp`, count(*)  As count
			FROM `detections`
			WHERE `isIncoming`=1 AND `timestamp` BETWEEN '2021-02-11 12:00:00' AND '2021-02-11 12:59:59'
			GROUP BY year( `timestamp` ), month( `timestamp` ), day( `timestamp` ), hour(`timestamp`), minute(`timestamp`)";

	$result=mysqli_query($link,$query);
	if(mysqli_num_rows($result)>0){
		while ($row=mysqli_fetch_array($result)) {
      		$timestamp=$row['timestamp'];
      		$count=$row['count'];
      		// $singleData=array("x"=> $timestamp,"y"=> $count);
      		$singleData=array("label"=> substr($timestamp, 0, -3),"y"=> $count);

      		array_push($dataPoints1,$singleData);
      	}
	}

}

if(!mysqli_connect_error()){
	$query="SELECT `timestamp`, count(*)  As count
			FROM `detections`
			WHERE `isIncoming`=0 AND `timestamp` BETWEEN '2021-02-11 12:00:00' AND '2021-02-11 12:59:59'
			GROUP BY year( `timestamp` ), month( `timestamp` ), day( `timestamp` ), hour(`timestamp`), minute(`timestamp`)";

	$result=mysqli_query($link,$query);
	if(mysqli_num_rows($result)>0){
		while ($row=mysqli_fetch_array($result)) {
      		$timestamp=$row['timestamp'];
      		$count=$row['count'];
      		// $singleData=array("x"=> $timestamp,"y"=> $count);
      		$singleData=array("label"=> substr($timestamp, 0, -3),"y"=> $count);

      		array_push($dataPoints2,$singleData);
      	}
	}

}
 


?>

<!DOCTYPE html>
<html>
<head>
	<title></title>
	<script>
	window.onload = function () {
	 
	var chart = new CanvasJS.Chart("chartContainer", {
		animationEnabled: true,
		theme: "light2",
		title:{
			text: "Incoming/Outgoing Chart"
		},
		axisY:{
			includeZero: true
		},
		legend:{
			cursor: "pointer",
			verticalAlign: "center",
			horizontalAlign: "right",
			itemclick: toggleDataSeries
		},
		data: [{
			type: "column",
			name: "Incoming",
			indexLabel: "{y}",
			//yValueFormatString: "$#0.##",
			showInLegend: true,
			dataPoints: <?php echo json_encode($dataPoints1, JSON_NUMERIC_CHECK); ?>
		},{
			type: "column",
			name: "Outgoing",
			indexLabel: "{y}",
			//yValueFormatString: "$#0.##",
			showInLegend: true,
			dataPoints: <?php echo json_encode($dataPoints2, JSON_NUMERIC_CHECK); ?>
		}]
	});
	chart.render();
	 
	function toggleDataSeries(e){
		if (typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
			e.dataSeries.visible = false;
		}
		else{
			e.dataSeries.visible = true;
		}
		chart.render();
	}
	 
	}
	</script>
</head>
<style type="text/css">

</style>
<body>

<div id="chartContainer" style="height: 370px; width: 100%;"></div>


<script src="https://canvasjs.com/assets/script/canvasjs.min.js"></script>
</body>
</html>