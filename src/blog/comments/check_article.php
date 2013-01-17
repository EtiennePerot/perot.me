<?php
$title = 'Unknown article';
$url = '/';
function error($error_message) {
	global $title, $url;
	if(isset($_REQUEST['json'])) {
		die(json_encode(array('error' => $error_message)));
	}
	require('error.php');
	die();
}

if(!isset($_REQUEST['article'])) {
	error('Invalid article name. What exactly are you trying to pull here?');
}
$article = $_REQUEST['article'];
require('article_list.gen.php');
if(!array_key_exists($article, $all_articles)) {
	error('Invalid article name. What exactly are you trying to pull here?');
}
$title = $all_articles[$article]['title'];
$url = $all_articles[$article]['url'];
?>