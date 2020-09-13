const API_URL = "http://api.wimc.ctf.allesctf.net/1.0";
var visited = ["home"];
var loggedInUser;

function interactApi(endpoint, postContent) {
    endpoint = endpoint || '';
    let options = {headers: {"X-API-TOKEN": API_TOKEN}};

    if (postContent) {
        options.headers["Content-Type"] = "application/x-www-form-urlencoded";
        options["method"] = "POST";
        options["body"] = postContent;
    }

    return new Promise((resolve, reject) => {
        fetch(API_URL + endpoint, options)
        .then(value => {
            return value.json();
        }, reject).then(value => {
            if (value.status !== "success")
                reject(value);
            else
                resolve(value);
        }, reject);
    });
}

function loadUser() {
    interactApi('/user').then(user => {
        loggedInUser = user.data;

        if (!document.getElementById("login"))
            return;

        document.getElementById("login").remove();
        document.getElementById("register").remove();

        let nav = document.getElementById("nav");
        let a = document.createElement("a");
        a.classList.add("nav-link", "nav-item", "form-inline", "my-2", "my-lg-2");
        a.innerText = `Hello, ${loggedInUser.username}`;
        nav.appendChild(a);

        a = document.createElement("a");
        a.classList.add("nav-link", "nav-item", "form-inline", "my-2", "my-lg-2");
        a.addEventListener("click", () => {
            window.location.href = window.location.origin;
        })
        a.innerText = "Logout";
        nav.appendChild(a);
    }, () => {});
}

function loadReviews() {
    interactApi('/reviews').then(reviews => {
        let r = document.getElementById("reviews");
        for (let rev of reviews.data["reviews"]) {
            let div = document.createElement("div");
            div.setAttribute("class", "review");

            let img = document.createElement("img");
            img.setAttribute("src", `./img/${rev["avatar"]}`);
            img.setAttribute("class", "avatar");

            let q = document.createElement("q");
            q.innerText = rev["text"];

            div.appendChild(img);
            div.appendChild(q);
            r.appendChild(div);
        }
    }, (error) => console.log('Fetching reviews failed:', error));
}

function getRandChance(min, max) {
    let result = -1;

    while (result < min || result > max) {
        result = Math.round((Math.random() * (max - min) + min) * 1000) / 1000;
    }

    return result;
}

function getGraphDataPoints(walletID) {
    flag = (walletID === "13371337133713371337");

    let result = [];

    let now = new Date();
    let time = new Date();

    for (let i = 0; i < 24; i++) {
        time.setHours(i, 0, 0, 0);

        if (time.getTime() < now.getTime()) {
            result.push({x: time.getTime(), y: getRandChance(0, 40)});
        } else {
            if (flag)
                result.push({x: time.getTime(), y: 100.00});
            else
                result.push({x: time.getTime(), y: getRandChance(30, 75)});
        }
    }

    return result;
}

function getWalletInfo(walletID) {
    let detail = document.getElementById("details");
    detail.innerHTML = "";

    for (let wallet of loggedInUser["wallets"]) {
        if (wallet["id"] === walletID) {
            let h2 = document.createElement("h2");
            h2.innerText = `Wallet-ID: #${wallet["id"]}`;
            detail.appendChild(h2);

            h2 = document.createElement("h2");
            h2.innerText = `Balance: $ ${wallet["balance"]}`;
            detail.appendChild(h2);

            h2 = document.createElement("h2");
            h2.innerText = `Note: ${wallet["note"]}`;
            detail.appendChild(h2);
        }
    }

    var chart = new CanvasJS.Chart("chartContainer", {
        animationEnabled: true,
        title: {
            text: "Hourly Average Flag Chance"
        },
        axisX: {
            title: "Time"
        },
        axisY: {
            title: "Percentage",
            suffix: "%",
            includeZero: true
        },
        data: [{
            type: "line",
            name: "Flag",
            connectNullData: true,
            xValueType: "dateTime",
            xValueFormatString: "DD MMM hh:mm TT",
            yValueFormatString: "#,##0.##\"%\"",
            dataPoints: getGraphDataPoints(walletID)
        }]
    });
    chart.render();
}

function loadWallets(retry) {
    if (retry === undefined)
        retry = true;

    if (loggedInUser) {
        if (typeof loggedInUser["wallets"] === "undefined")
            return;

        let bar = document.getElementById("bar");
        for (let wallet of loggedInUser["wallets"]) {
            let li = document.createElement("li");
            li.setAttribute("class", "list-group-item");
            li.setAttribute("onclick", `getWalletInfo("${wallet["id"]}")`)

            li.innerText = `# ${wallet["id"]}`;

            bar.appendChild(li);
        }
    } else {
        loadUser();

        if (retry)
            setTimeout(() => {
                loadWallets(false);
            }, 100);
    }
}

function loadPage(page, back=false) {
    let stateObj = {"page": page};
    history.pushState(stateObj, page, page);

    let content = document.getElementById("page");
    content.innerHTML = "<div class='loader'></div>";

    setTimeout(() => {
        fetch(page, {
            headers: {
                "X-API-TOKEN": API_TOKEN
        }})
            .then(response => response.text())
            .then(html => {
                content.innerHTML = html;
                document.title = `SecureCash™ | ${page.charAt(0).toUpperCase() + page.slice(1)}`
                setTimeout(() => {
                    if (window.location.pathname === "/home") {
                        loadReviews();
                    } else if (window.location.pathname === "/wallets") {
                        loadWallets();
                    } else if (window.location.pathname === "/support") {
                        var s = document.createElement("script");
                        s.src = "https://www.google.com/recaptcha/api.js";
                        document.body.appendChild(s);
                    }
                }, 100);
            });
        }, 500);

    loadUser();
    if (!back) {
        visited.push(page);
    }
}

function login() {
    var username = document.getElementById("username").value || '';
    var password = document.getElementById("password").value || '';

    interactApi('/login', `username=${username}&password=${password}`)
    .then(response => {
        window.location.href = `${window.location.origin}/?api_key=${response.data.api_key}`;
    }, error => {
        let errorMessage = error["errorMessage"] || "ERROR: " + error;
        let div = document.getElementById("error");
        div.classList.add("alert", "alert-danger", "someform");
        div.innerText = errorMessage;
    });
}

function register() {
    var username = document.getElementById("username").value || '';
    var password = document.getElementById("password").value || '';

    interactApi('/register', `username=${username}&password=${password}`)
    .then(response => {
        window.location.href = `${window.location.origin}/?api_key=${response.data.api_key}`;
    }, error => {
        let errorMessage = error["errorMessage"] || "ERROR: " + error;
        let div = document.getElementById("error");
        div.classList.add("alert", "alert-danger", "someform");
        div.innerText = errorMessage;
    });
}

function support(token) {
    var description = document.getElementById("description").value || '';
    var url = document.getElementById("url").value || '';

    let div = document.getElementById("msg");
    interactApi('/support', `description=${description}&url=${url}&token=${token}`)
    .then(response => {
        div.removeAttribute("class");
        div.classList.add("alert", "alert-success", "someform");
        div.innerText = response.data.message;
    }, error => {
        let errorMessage = error["errorMessage"] || "ERROR: " + error;
        div.removeAttribute("class");
        div.classList.add("alert", "alert-danger", "someform");
        div.innerText = errorMessage;
    });
}

window.addEventListener("keypress", e => {
    if (e.keyCode === 13) {
        if (window.location.pathname === "/login") {
            login();
        } else if (window.location.pathname === "/register") {
            register();
        } else if (window.location.pathname === "/support") {
            support();
            e.preventDefault();
        }
    }
})

window.addEventListener("popstate", e => {
    if (visited.length === 1) {
        return;
    }
    loadPage(visited[visited.length - 2], true);
    visited.pop();
    e.preventDefault();
})

window.onload = () => {
    loadUser();
    loadReviews();
}
