<?php

include './Constants/index.php';
$link=mysqli_connect($server,$user,$pass,$db);

function randomTimeStamp($min, $max)
{
    // Convert to timetamps
    // $min = strtotime($start_date);
    // $max = strtotime($end_date);

    $val = rand($min, $max);

    return date('Y-m-d H:i:s', $val);
}

$starting=1620172800;//WITH THIS TIME SCRIPT IS NOT RUN ITS NEW MAY 5th
$ending=$starting+(86400*15);//15 days

$start_date=$starting-3600;//JAN 1, 2021
$end_date=$starting+3599-3600;// +3600 means 1 hour

echo "Next starting: ".$ending."<br>";

// while($start_date<=$ending-3600){

// 	$noOfPeopleInAnHour=rand(3,11);

// 	for ($i=0; $i < $noOfPeopleInAnHour; $i++) { 
		
// 		$timestamp=randomTimeStamp($start_date,$end_date);
// 		$tracking_id=rand(1,100);
// 		$isIncoming=rand(0,1);

// 		$query="INSERT INTO `detections` (`timestamp`, `class_name`, `tracking_id`, `isIncoming`) VALUES ('{$timestamp}','person','{$tracking_id}','{$isIncoming}')";

// 		if(mysqli_query($link,$query)){
// 			echo "S";
// 		}else{
// 			echo "N";
// 		}

// 	}

// 	$start_date=$start_date+3600;
// 	$end_date=$end_date+3600;
// }



// echo strtotime("2021-05-06 09:52:53")."<br>";
// echo date('Y-m-d H:i:s',1620287573);

?>

