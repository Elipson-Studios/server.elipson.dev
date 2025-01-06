console.log("Powered by AWS");
const http = require('http');
const url = require('url');
const path = require('path');
const fs = require('fs');

const PORT = 1551;
const REQUESTS_FOLDER = path.join(__dirname, 'requests');

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const query = parsedUrl.query;
    const requestFile = query.request;

    if (!requestFile) {
        res.writeHead(400, { 'Content-Type': 'text/plain' });
        res.end('Bad Request: Missing request file parameter');
        return;
    }

    const filePath = path.join(REQUESTS_FOLDER, requestFile);

    if (!fs.existsSync(filePath)) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found: Request file does not exist');
        return;
    }

    const params = Object.keys(query).reduce((acc, key) => {
        if (key !== 'request') {
            acc[key] = query[key];
        }
        return acc;
    }, {});

    try {
        const requestHandler = require(filePath);
        requestHandler(params, res);
    } catch (error) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Internal Server Error: Unable to process request file');
    }
});

server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});