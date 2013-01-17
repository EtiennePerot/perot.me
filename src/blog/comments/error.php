<!DOCTYPE html>
<html lang="en-us">
	<head>
		<title>Etienne Perot — Error on post <?php echo htmlspecialchars($title); ?></title>
		<include>head.include.html</include>
		%extracss%
		<style>@import "status_boxes.scss";</style>
	</head>
	<body>
		<div id="main">
			<exec>../../nav.py blog 'Error'</exec>
			<include>sidebar.include.html</include>
			<div id="content">
				<h1>Error while posting on: <a href="<?php echo htmlspecialchars($url); ?>" title="<?php echo htmlspecialchars($title); ?>"><?php echo htmlspecialchars($title); ?></a></h1>
				<div class="error">
					<header>
						<h2>Error</h2>
					</header>
					<p><?php echo htmlspecialchars($error_message); ?></p>
				</div>
				<p>If you didn't expect this error, please contact Etienne Perot; contact information is available in the sidebar.</p>
				<p>Back to <a href="<?php echo htmlspecialchars($url); ?>" title="<?php echo htmlspecialchars($title); ?>"><?php echo htmlspecialchars($title); ?></a>.</p>
			</div>
		</div>
		<include>footer.include.html</include>
	</body>
</html>