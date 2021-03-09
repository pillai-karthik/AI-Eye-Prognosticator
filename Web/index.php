<?php

session_start();

include './Constants/index.php';

$error=null;

$link=mysqli_connect($server,$user,$pass,$db);

if(isset($_POST["submit"])){
	//FORM SUBMITTED
	if(!mysqli_connect_error()){
		if(array_key_exists("username", $_POST) AND array_key_exists("password", $_POST)){
			if(!($_POST["username"]=="" OR $_POST["password"]=="")){
				//USER HAS ENTERED EVERYTHING
				// echo md5(mysqli_real_escape_string($link,$_POST['password']))."<br>";
				// echo md5($_POST['password']);
				$query="SELECT * FROM `users` WHERE `username`='".mysqli_real_escape_string($link,$_POST['username'])."'"." AND `passwordHash`='".md5(mysqli_real_escape_string($link,$_POST['password']))."'";

				$result=mysqli_query($link,$query);//IF SUCH USER EXISTS HE WILL BE STORED IN $RESULT

				if(mysqli_num_rows($result)>0){//USER EXISTS WITH GIVE USERNAME AND PASSWORD
					//STORING SESSION VARIABLESS AND REDIRECTING TO userPanel.php

					$row=mysqli_fetch_array($result);
					$_SESSION['userID']=$row['userID'];
					$_SESSION['username']=$row['username'];

					$error=null;
					header("Location: ./Dashboard/");
					
					exit;

				}else{
					$error="Incorrect username or password!";//USER DOES NOT EXITS
				}
			}
		}
	}
}


?>

<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<!-- Bootstrap CSS -->
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" integrity="sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorigin="anonymous">

	<link rel="stylesheet" type="text/css" href="index.css">
	<title>AI Eye</title>
</head>
<body>

<div class="wrapper fadeInDown">
  <div id="formContent">
    <!-- Tabs Titles -->

    <!-- Icon -->
    <!-- <div class="fadeIn first">
      <img src="http://danielzawadzki.com/codepen/01/icon.svg" id="icon" alt="User Icon" />
    </div> -->

    <h1 style="margin: 10px;"><u>Admin Login</u></h1>

    <?php 

    if($error!=null){
    	echo '
    	<div class="alert alert-danger" role="alert" style="margin: 10px;">
	  		<b>'.$error.'</b>
		</div>';
    }

    ?>
    

    <!-- Login Form -->
    <form method="POST">
      <input type="text" id="username" class="fadeIn second" name="username" placeholder="Username" required autocomplete="off">
      <input type="password" id="password" class="fadeIn third" name="password" placeholder="Password"  required autocomplete="off">
      <input type="submit" class="fadeIn fourth" value="Log In" name="submit">
    </form>

    <!-- Remind Passowrd -->
    <!-- <div id="formFooter">
      <a class="underlineHover" href="#">Forgot Password?</a>
    </div> -->

  </div>
</div>









</body>
</html>