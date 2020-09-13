const bodyParser = require('body-parser');
const cors = require('cors');
const crypto = require('crypto');
const express = require('express');
const mysql = require('mysql');
const pdf = require('html-pdf'); // I've heard it runs in a sandbox, so this should be safe to use. It is only usable for admins anyway.
const { v4: uuidv4 } = require('uuid');

const connection = mysql.createConnection({
    host: process.env.MYSQL_HOST || '127.0.0.1',
    user: "securecash",
    database: "securecash"
});

function sendError(response, responseCode, errorMessage, errorDetails) {
    errorMessage = errorMessage || "Internal server error";
    responseCode = responseCode || 500;
    errorDetails = errorDetails || {};

    let message = {
        code: responseCode,
        status: "error",
        details: errorDetails,
        errorMessage: errorMessage
    }

    response.status(responseCode);
    response.json(message);
    response.end();
}

function sendSuccess(response, responseData, responseCode) {
    responseCode = responseCode || 200;
    responseData = responseData || {};

    let message = {
        code: responseCode,
        data: responseData,
        status: "success"
    }

    response.status(responseCode);
    response.json(message);
    response.end();
}

const BIND_ADDR = process.env.BIND_ADDR || '0.0.0.0';
const PORT = process.env.PORT || '1337';

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cors());

app.options('/1.0/reviews', cors());
app.get('/1.0/reviews', cors(), function(req, res) {
    sendSuccess(res, {
        'reviews': [
            {
                'avatar': 'avatar_1.png',
                'text': 'Best investment of my life'
            },
            {
                'avatar': 'avatar_2.jpg',
                'text': 'Support and admins suck'
            },
            {
                'avatar': 'avatar_3.jpg',
                'text': 'Your cash well stored'
            },
            {
                'avatar': 'avatar_4.png',
                'text': 'There is nothing better'
            },
        ]
    });
});

app.options('/1.0/login', cors());
app.post('/1.0/login', cors(), function(req, res) {
    var username = req.body['username'] || '';
    var password = req.body['password'] || '';

    if (username.length === 0 || password.length === 0)
        return sendError(res, 400, "Username and/or password are empty!");

    var password = crypto.createHash('sha256').update(password).digest('hex');
    connection.query('SELECT api_key FROM general WHERE username=? AND password=?', [
        username,
        password
    ], (err, data) => {
        if (err) {
            console.log(err);
            return sendError(res);
        }

        var data = data[0];
        if (data)
            return sendSuccess(res, {api_key: data.api_key});
        else
            return sendError(res, 401, "Invalid username or password!");
    });
});

app.options('/1.0/register', cors());
app.post('/1.0/register', cors(), function(req, res) {
    var username = req.body['username'] || '';
    var password = req.body['password'] || '';

    if (username.length === 0 || password.length === 0)
        return sendError(res, 400, "Username and/or password are empty!");

    if (username.length > 50)
        return sendError(res, 400, "Username should not be longer than 50 characters!");

    connection.query('SELECT user_id FROM general WHERE username=?', [
        username
    ], (err, data) => {
        if (err) {
            console.log(err);
            return sendError(res);
        }

        var data = data[0];
        if (data) {
            return sendError(res, 409, "Username is already taken!");
        } else {
            var user_id = uuidv4();
            password = crypto.createHash('sha256').update(password).digest('hex');
            var wallet_id = crypto.randomBytes(20).toString('hex').substring(0,20);
            var api_key = crypto.randomBytes(30).toString('hex').substring(0,30);

            connection.query('INSERT INTO general VALUES (?, ?, ?, ?, ?);', [
                user_id,
                username,
                password,
                api_key,
                false
            ], (err, data) => {
                connection.query('INSERT INTO wallets VALUES (?, ?, ?, ?);', [
                    wallet_id,
                    user_id,
                    0.00,
                    "There could be something important noted here!"
                ], (err, data) => {
                    if (err) {
                        console.log(err);
                        return sendError(res);
                    }

                    return sendSuccess(res, {api_key: api_key}, 201);
                });
            });
        }
    });
});

app.options('/1.0/user', cors());
app.get('/1.0/user', cors(), function(req, res) {
    var api_key = req.header('X-API-TOKEN') || '';

    var response = {};
    response.wallets = [];

    connection.query('SELECT user_id, username FROM general WHERE api_key=?;', [
        api_key
    ], (err, data) => {
        if (err) {
            console.log(err);
            return sendError(res);
        }

        var data = data[0];
        if (data) {
            response.user_id = data.user_id;
            response.api_key = api_key;
            response.username = data.username;
        } else {
            return sendError(res, 401, "API Key is invalid!");
        }

        connection.query('SELECT * FROM wallets WHERE owner_id=?;', [
            response.user_id
        ], (err, data) => {
            if (err) {
                console.log(err);
                return sendError(res);
            }

            let i = 0;
            for (let wallet of data) {
                response.wallets[i] = {};
                response.wallets[i].id = wallet.wallet_id;
                response.wallets[i].balance = wallet.balance;
                response.wallets[i].note = wallet.note;
                i++;
            }

            return sendSuccess(res, response);
        });
    });
});

var config = {
    "format": "A4",
    "orientation": "portrait",
    "border": "0",
    "zoomFactor": "1",
    "paginationOffset": 1,
    "type": "pdf",
    "renderDelay": 1000,
    "timeout": 2000
}

app.options('/1.0/admin/createReport', cors());
app.post('/1.0/admin/createReport', cors(), function(req, res) {
    var api_key = req.header('X-API-TOKEN');
    var html = req.body["html"] || '<p>No HTML provided</p>';

    connection.query('SELECT username FROM general WHERE api_key=? AND admin=?;', [
        api_key,
        true
    ], (err, data) => {
        if (err) {
            console.log(err);
            return sendError(res);
        }

        var data = data[0];
        if (!data) {
            return sendError(res, 403, "Only admins are allowed to use this!");
        } else {
            try {
                pdf.create(html, config).toStream(function(err, stream){
                    if (err)
                        return sendError(res);

                    try {
                        res.status(200);
                        stream.pipe(res);
                    } catch(e) {
                        return sendError(res);
                    }
                });
            } catch (e) {
                console.log("Error creating PDF:", e);
                return sendError(res);
            }
        }
    })
});

// ACCESS ONLY FOR LOCAL IT STAFF
app.options('/internal/createTestWallet', cors());
app.post('/internal/createTestWallet', cors(), function(req, res) {
    var balance = req.body["balance"] || 1337;
    var ip = req.connection.remoteAddress;

    if (ip === "127.0.0.1") {
        // create testing wallet without owner
        var wallet_id = crypto.randomBytes(20).toString('hex').substring(0,20);
        connection.query(`INSERT INTO wallets VALUES ('${wallet_id}', NULL, ${balance}, 'TESTING WALLET 1234');`, (err, data) => {
            if (err)
                return sendError(res);

            if (data)
                return sendSuccess(res, {
                    message: `Here is your test wallet: ${wallet_id}`
                });
            else
                return sendError(res);
        });
    } else {
        return sendError(res, 403, "Only local IT staff is allowed to do this!");
    }
});

app.listen(PORT, BIND_ADDR, () => {
    console.log(`Running on ${BIND_ADDR}:${PORT}...`);
});
