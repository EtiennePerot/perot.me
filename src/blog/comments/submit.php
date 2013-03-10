<?php
include('nocache.php');

define('MAX_POST_LENGTH', 1024*128); ## 128 KB
define('MAX_USERNAME_LENGTH', 512);
define('MAX_WEBSITE_LENGTH', 1024);
define('QUEUE_DIR', 'queue');
define('FILE_GROUP', 'perot');
define('ACCEPTABLE_WEBSITE', '%^https?://(?:[-\\w]+\\.)*[-\\w]+(?:/[^<>"\\s]*)?$%i');
define('ACCEPTABLE_ARTICLE', '%^[-_\\w]+$%');
define('DEFAULT_USERNAME', 'Anonymous');
define('TOTALLY_RANDOM_SALT', 'RDQWtaHejcAlpRUzwuqDWU3kni0BLqL5');
define('COMMENT_DATE_GRANULARITY', 'Y-m-d@H:'); # Not more than one post per IP per hour per article

# Sanitize article
require('check_article.php');

# Sanitize username
function email_obfuscate($match) {
	return str_replace('@', ' (at) ', str_replace('.', ' (dot) ', $match[0]));
}
$username = DEFAULT_USERNAME;
if(isset($_REQUEST['username']) && strlen(trim($_REQUEST['username'])) > 0) {
	$username = trim(str_replace("\n", '', str_replace("\r", '', $_REQUEST['username'])));
	if(strlen($username) > MAX_USERNAME_LENGTH) {
		error('Username too long.');
	}
	$username = preg_replace_callback('/\\S+@(?:[-\w]+\.)+[-\w]+/', 'email_obfuscate', $username);
}

# Sanitize website, but only if username is not default
$website = null;
if(strtolower($username) != strtolower(DEFAULT_USERNAME) && isset($_REQUEST['website']) && !empty($_REQUEST['website'])) {
	$website = $_REQUEST['website'];
	if(strtolower(substr($website, 0, 4)) == 'www.') {
		$website = 'http://'.$website;
	}
	if(!preg_match(ACCEPTABLE_WEBSITE, $website)) {
		error('Invalid website URL.');
	}
	if(strlen($website) > MAX_WEBSITE_LENGTH) {
		error('Website URL too long.');
	}
}

# Check nonce
if(!isset($_REQUEST['nonce']) || empty($_REQUEST['nonce'])) {
	error('No nonce provided. What exactly are you trying to pull here?');
}
require('nonce.php');
if(!nonce_validate($article, $_REQUEST['nonce'])) {
	error('Invalid nonce. Did you open the comment form in a more recent window? Open a fresh comment form and post your comment again. Also consider turning on JavaScript, with which this error should not happen.');
}

# Sanitize message
if(!isset($_REQUEST['message']) || empty($_REQUEST['message'])) {
	error('Message must not be empty.');
}
if(strlen($_REQUEST['message']) > MAX_POST_LENGTH) {
	error('Message too long. Keep things short!');
}
$message = trim(strip_tags($_REQUEST['message']));

# Check if the user can comment
$comments_dir = QUEUE_DIR.'/'.$article;
if(!file_exists(QUEUE_DIR)) {
	mkdir(QUEUE_DIR, 0770);
	chgrp(QUEUE_DIR, FILE_GROUP); # Apparently changes the permissions back to 0750
	chmod(QUEUE_DIR, 0770);       # So gotta change it back again
}
if(!file_exists($comments_dir)) {
	mkdir($comments_dir, 0770);
	chgrp($comments_dir, FILE_GROUP); # Apparently changes the permissions back to 0750
	chmod($comments_dir, 0770);       # So gotta change it back again
}
$filename_hash = hash('sha256', TOTALLY_RANDOM_SALT.'|'.$article.'|'.date(COMMENT_DATE_GRANULARITY).'|'.$_SERVER['REMOTE_ADDR']);
$filename = $comments_dir.'/'.$filename_hash.'.md';
if(file_exists($filename)) {
	error('You have already commented recently! Try again in a little while.');
}

# All checks passed, build the final contents of the message file
$full_file = '';
$full_file .= 'Author: '.$username."\n";
if($website != null) {
	$full_file .= 'Website: '.$website."\n";
}
$full_file .= 'Date: '.gmdate('Y-m-d H:i:s')."\n";
$full_file .= "\n";
$full_file .= $message."\n";

# Write the file
$handle = fopen($filename, 'wb');
fwrite($handle, $full_file);
fclose($handle);
chgrp($filename, FILE_GROUP);
chmod($filename, 0660);

# Send notification email
$num_comments = count(glob($comments_dir.'/*.md'));
if($num_comments == 1) {
	exec(escapeshellarg(dirname(__FILE__).'/mail.py').' '.escapeshellarg($article));
}

# Clean up nonce
nonce_cleanup($article);

# Show success message
$success_message = array(
	'Thanks! Your message has been successfully submitted.',
	'It will show up on the site after moderation.'
);
if(isset($_REQUEST['json'])) {
	die(json_encode(array('success' => implode("\n", $success_message))));
}
require('success.php');
?>