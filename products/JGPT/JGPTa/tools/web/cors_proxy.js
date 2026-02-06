/**
 * cors_proxy.js - A simple Node.js proxy to bypass CORS during development.
 * Usage: node cors_proxy.js [TARGET_URL] [PORT]
 * Example: node cors_proxy.js http://api.external.com 9000
 */

const http = require('http');
const https = require('https');
const url = require('url');

const TARGET = process.argv[2] || 'http://localhost:8000';
const PORT = process.argv[3] || 9090;

console.log(`🌐 CORS Proxy starting on port ${PORT}`);
console.log(`👉 Forwarding to: ${TARGET}`);

http.createServer((req, res) => {
    // 1. Handle Preflight OPTIONS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // 2. Forward Request
    const targetUrl = new url.URL(req.url, TARGET);
    const options = {
        hostname: targetUrl.hostname,
        port: targetUrl.port || (targetUrl.protocol === 'https:' ? 443 : 80),
        path: targetUrl.pathname + targetUrl.search,
        method: req.method,
        headers: {
            ...req.headers,
            host: targetUrl.host // Override host header
        }
    };

    const proxyReq = (targetUrl.protocol === 'https:' ? https : http).request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, {
            ...proxyRes.headers,
            'access-control-allow-origin': '*' // Force CORS on response
        });
        proxyRes.pipe(res, { end: true });
    });

    proxyReq.on('error', (e) => {
        console.error(`❌ Proxy Error: ${e.message}`);
        res.writeHead(500);
        res.end('Proxy Error');
    });

    req.pipe(proxyReq, { end: true });

}).listen(PORT, () => {
    console.log(`✅ Proxy ready: http://localhost:${PORT}`);
});
