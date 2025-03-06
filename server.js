// Custom server for Next.js to handle Render's PORT environment variable
const { createServer } = require('http');
const { parse } = require('url');
const next = require('next');

// Force production mode when running on Render
// This is crucial for avoiding development mode's continuous recompilation
if (process.env.RENDER) {
  process.env.NODE_ENV = 'production';
  console.log('Detected Render environment, forcing production mode');
}

// Determine if we're in development or production
const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();

// Get the port from environment variable or use 3000 as default
const port = process.env.PORT || 3000;

app.prepare().then(() => {
  createServer((req, res) => {
    // Parse the URL
    const parsedUrl = parse(req.url, true);
    
    // Let Next.js handle the request
    handle(req, res, parsedUrl);
  }).listen(port, (err) => {
    if (err) throw err;
    console.log(`> Ready on http://localhost:${port}`);
    // Log information about the environment for debugging
    console.log(`> Environment: ${process.env.NODE_ENV}`);
    console.log(`> Using PORT: ${port}`);
  });
}); 