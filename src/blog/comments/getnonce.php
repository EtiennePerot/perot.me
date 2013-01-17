<?php
include('nocache.php');

# Sanitize article
require('check_article.php');
require('nonce.php');
$nonce = nonce_generate($article);
if(isset($_REQUEST['json'])) {
	die(json_encode(array('nonce' => $nonce)));
}
die('What are you trying to do here?');
?>