<!DOCTYPE html>
<html lang="en-us">
	<head>
		<title>Etienne Perot — Reply to %title%</title>
		<include>head.include.html</include>
		%extracss%
	</head>
	<body>
		<div id="main">
			<exec>../../nav.py blog '%commentformurl%' 'Compose Reply'</exec>
			<include>sidebar.include.html</include>
			<div id="content">
				<h2>Replying to: <a href="%url%" title="%title%">%title%</a></h2>
				<form action="/comment" method="post" id="comment-form">
					%iscommentform%
					<input type="hidden" name="article" value="%urlname%" />
					<input type="hidden" name="nonce" value="<?php require('%commentsdir%/nonce.php'); echo htmlspecialchars(nonce_generate('%urlname%')); ?>" />
					<include>blog/comments/comment_form.include.html</include>
				</form>
			</div>
		</div>
		<include>footer.include.html</include>
	</body>
</html>
