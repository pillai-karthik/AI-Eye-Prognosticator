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


// BETWEEN '2021-02-11 12:00:00' AND '2021-02-11 12:59:59'

if(!mysqli_connect_error()){

	if(isset($_GET['selectedYear']) AND $_GET['selectedYear']!=""){
		for($month=1;$month<=12;$month++){

			$paddedMonth=sprintf('%02d', $month);

			$query="SELECT `timestamp`, count(*)  As count
				FROM `detections`
				WHERE `isIncoming`=1 AND `timestamp` BETWEEN '".$_GET['selectedYear']."-".$paddedMonth."-01 00:00:00' AND '".$_GET['selectedYear']."-".$paddedMonth."-31 23:59:59'";


			$result=mysqli_query($link,$query);

			$row=mysqli_fetch_array($result);

			$label=$paddedMonth.'/'.$_GET['selectedYear'];
			$count=$row['count'];
			$singleData=array("label"=> $label,"y"=> $count);

			array_push($dataPoints1,$singleData);

		}
	}

}


if(!mysqli_connect_error()){

	if(isset($_GET['selectedYear']) AND $_GET['selectedYear']!=""){
		for($month=1;$month<=12;$month++){

			$paddedMonth=sprintf('%02d', $month);

			$query="SELECT `timestamp`, count(*)  As count
				FROM `detections`
				WHERE `isIncoming`=0 AND `timestamp` BETWEEN '".$_GET['selectedYear']."-".$paddedMonth."-01 00:00:00' AND '".$_GET['selectedYear']."-".$paddedMonth."-31 23:59:59'";


			$result=mysqli_query($link,$query);

			$row=mysqli_fetch_array($result);

			$label=$paddedMonth.'/'.$_GET['selectedYear'];
			$count=$row['count'];
			$singleData=array("label"=> $label,"y"=> $count);

			array_push($dataPoints2,$singleData);

		}
	}

}

?>

<!DOCTYPE html>
<html>
<head>
	<title></title>
	<!-- Bootstrap CSS CDN -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">

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

<body>

<form class="alert alert-primary" method="GET" style="padding: 10px; border: 3px solid black; margin: 15px; border-radius: 20px;">
	<label for="selectedYear" style="font-size: 22px; margin-right: 10px; font-weight: bold;">SELECT YEAR</label>

	<select class="custom-select" style="width: 15%;" name="selectedYear">
	  <?php
	  	for($year=2015;$year<=2021;$year++){
	  		echo "<option value=\"".$year."\" selected>".$year."</option>";
	  	}
	  ?>
	</select>

	<input type="submit" class="btn btn-primary" style="font-weight: bold; margin-left: 10px;" value="SHOW RESULT">
</form>

<?php if(isset($_GET['selectedYear']) AND $_GET['selectedYear']!="") : ?>

	<div class="alert alert-success" role="alert" style="margin: 10px 15px; text-align: center; font-weight: bold;font-size: 20px;">
	  SELECTED YEAR : <span style="font-size: 25px; margin-left: 5px;"><?php echo $_GET['selectedYear']; ?></span>
	</div>


<div id="chartContainer" style="height: 370px; width: 98%;"></div>

<?php endif; ?>




<script src="https://canvasjs.com/assets/script/canvasjs.min.js"></script>
<!-- jQuery CDN - Slim version (=without AJAX) -->
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<!-- Popper.JS -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js" integrity="sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ" crossorigin="anonymous"></script>
<!-- Bootstrap JS -->
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
<!-- jQuery Custom Scroller CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/malihu-custom-scrollbar-plugin/3.1.5/jquery.mCustomScrollbar.concat.min.js"></script>


</body>
</html>