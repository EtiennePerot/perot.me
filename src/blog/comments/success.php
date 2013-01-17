<!DOCTYPE html>
<html lang="en-us">
	<head>
		<title>Etienne Perot — Comment posted on <?php echo htmlspecialchars($title); ?></title>
		<include>head.include.html</include>
		%extracss%
		<style>@import "status_boxes.scss";</style>
	</head>
	<body>
		<div id="main">
			<exec>../../nav.py blog 'Comment posted'</exec>
			<include>sidebar.include.html</include>
			<div id="content">
				<h1>Comment posted on: <a href="<?php echo htmlspecialchars($url); ?>" title="<?php echo htmlspecialchars($title); ?>"><?php echo htmlspecialchars($title); ?></a></h1>
				<div class="success">
					<header>
						<h2>Success</h2>
					</header>
					<p><?php echo implode('</p><p>', $success_message); ?></p>
				</div>
				<p>Back to <a href="<?php echo htmlspecialchars($url); ?>" title="<?php echo htmlspecialchars($title); ?>"><?php echo htmlspecialchars($title); ?></a>.</p>
			</div>
		</div>
		<include>footer.include.html</include>
	</body>
</html>

