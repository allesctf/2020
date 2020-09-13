const express = require('express');
const fs = require('fs');
const path = require('path');

const BIND_ADDR = process.env.BIND_ADDR || '0.0.0.0';
const PORT = process.env.PORT || '1337';

const app = express();
app.set('view engine', 'hbs');
app.set('views', './static');

function getToken(req) {
    if (!req.query.api_key || typeof req.query.api_key !== "string") {
        return 'I-AM-GUEST-TOKEN';
    }
    return req.query.api_key.replace(/;|\n|\r/g, "");
}

function handleStatic(req, res) {
    var file = path.join(__dirname + '/static' + path.normalize(req.path));
    if (fs.existsSync(file)) {
        res.sendFile(file);
    } else {
        res.status(404).send(`<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Error</title></head><body><pre>Cannot GET ${req.path}</pre></body></html>`);
    }
}

app.get('/', function(req, res) {
    res.render('index', {
        token: getToken(req)
    });
});

app.get('/home', function(req, res) {
    if (req.header("X-API-TOKEN")) {
        res.sendFile(path.join(__dirname) + '/static/home.html');
    } else {
        res.redirect('/');
    }
});

app.get('/wallets', function(req, res) {
    if (req.header("X-API-TOKEN")) {
        res.sendFile(path.join(__dirname) + '/static/wallets.html');
    } else {
        res.redirect('/');
    }
});

app.get('/notes', function(req, res) {
    if (req.header("X-API-TOKEN")) {
        res.sendFile(path.join(__dirname) + '/static/notes.html');
    } else {
        res.redirect('/');
    }
});

app.get('/support', function(req, res) {
    if (req.header("X-API-TOKEN")) {
        res.sendFile(path.join(__dirname) + '/static/support.html');
    } else {
        res.redirect('/');
    }
});

app.get('/login', function(req, res) {
    if (req.header("X-API-TOKEN")) {
        res.sendFile(path.join(__dirname) + '/static/login.html');
    } else {
        res.redirect('/');
    }
});

app.get('/register', function(req, res) {
    if (req.header("X-API-TOKEN")) {
        res.sendFile(path.join(__dirname) + '/static/register.html');
    } else {
        res.redirect('/');
    }
});

app.get('/js/*', handleStatic);
app.get('/css/*', handleStatic);
app.get('/img/*', handleStatic);

app.listen(PORT, BIND_ADDR, () => {
    console.log(`Running on ${BIND_ADDR}:${PORT}...`);
});
