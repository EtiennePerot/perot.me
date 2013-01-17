<?php
define('NONCES_DIR', dirname(__FILE__).'/nonces');
define('FILE_GROUP', 'perot');
define('NONCE_EXPIRE_SECONDS', 18*3600); # 18 hours
define('TOTALLY_RANDOM_SALT_NONCE', 'zZGdYC_viFwf4VYZpQX1L34xvjvoV0tU');
define('DEFAULT_PREVIOUS_NONCE', 'OX3Fxg3Or3nOP9b4mxSwwwqIqU7EfPoj');

function nonce_getfile($article) {
	return NONCES_DIR.'/'.hash('sha256', TOTALLY_RANDOM_SALT_NONCE.'|'.$article.'|'.$_SERVER['REMOTE_ADDR']).'.nonce';
}

function nonce_generate($article) {
	nonce_sweep();
	$previous_nonce = DEFAULT_PREVIOUS_NONCE;
	$nonce_file = nonce_getfile($article);
	if(!file_exists(NONCES_DIR)) {
		mkdir(NONCES_DIR, 0770);
		chgrp(NONCES_DIR, FILE_GROUP);
	} elseif(file_exists($nonce_file)) {
		if(filemtime($nonce_file) + NONCE_EXPIRE_SECONDS > time()) {
			$previous_nonce .= file_get_contents($nonce_file);
		}
	}
	$new_nonce = hash('sha512', $nonce_file.'|'.$previous_nonce.'|'.microtime().'|'.strval(mt_rand()));
	$handle = fopen($nonce_file, 'w');
	fwrite($handle, $new_nonce);
	fclose($handle);
	chgrp($nonce_file, FILE_GROUP);
	chmod($nonce_file, 0660);
	return $new_nonce;
}

function nonce_validate($article, $nonce) {
	$nonce_file = nonce_getfile($article);
	if(file_exists($nonce_file) && filemtime($nonce_file) + NONCE_EXPIRE_SECONDS > time()) {
		return file_get_contents($nonce_file) == $nonce;
	}
	return false;
}

function nonce_cleanup($article) {
	$nonce_file = nonce_getfile($article);
	if(file_exists($nonce_file)) {
		unlink($nonce_file);
	}
}

function nonce_sweep() {
	if(!file_exists(NONCES_DIR)) {
		return;
	}
	$nonce_files = glob(NONCES_DIR.'/*.nonce');
	$time = time();
	for($i = 0; $i < count($nonce_files); $i++) {
		if(filemtime($nonce_files[$i]) + NONCE_EXPIRE_SECONDS < $time) {
			unlink($nonce_files[$i]);
		}
	}
}
?>