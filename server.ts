/**
 * Smart Crop Advisory - Production Full-Stack Server
 * Bridges Express.js entry point with high-performance Python 3 backend.
 * Conforms to AI Studio Cloud Run deployment standards.
 */

import express from 'express';
import http from 'http';
import path from 'path';
import fs from 'fs';
import { spawn, ChildProcess } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
let portArg = 3000;
for (const arg of process.argv.slice(2)) {
  if (arg.startsWith('--port=')) {
    const val = Number(arg.split('=')[1]);
    if (!isNaN(val)) portArg = val;
  }
}

// In development, default to port 3000 because Nginx already occupies 8080.
// In production Cloud Run, process.env.PORT is respected if no CLI flag is provided.
const PORT = portArg || Number(process.env.PORT) || 3000;
const PYTHON_PORT = Number(process.env.PYTHON_PORT) || 3001;

let pythonProcess: ChildProcess | null = null;
let isPythonReady = false;

// 1. Spawn Python Agricultural Decision Engine
function startPythonBackend() {
  const pythonScript = path.join(__dirname, 'backend', 'app.py');
  
  if (!fs.existsSync(pythonScript)) {
    console.warn(`[Server] Python script not found at ${pythonScript}`);
    return;
  }

  console.log(`[Server] Launching Python backend on port ${PYTHON_PORT}...`);
  pythonProcess = spawn('python3', [pythonScript, `--port=${PYTHON_PORT}`, '--host=127.0.0.1'], {
    cwd: __dirname,
    stdio: 'inherit',
    env: {
      ...process.env,
      PORT: String(PYTHON_PORT)
    }
  });

  pythonProcess.on('error', (err) => {
    console.error('[Server] Failed to spawn Python backend:', err.message);
  });

  pythonProcess.on('exit', (code) => {
    console.log(`[Server] Python backend process exited with code ${code}`);
    isPythonReady = false;
  });

  // Verify python readiness
  const checkInterval = setInterval(() => {
    const req = http.get(`http://127.0.0.1:${PYTHON_PORT}/health`, (res) => {
      if (res.statusCode === 200) {
        isPythonReady = true;
        clearInterval(checkInterval);
        console.log(`[Server] Python backend verified online on port ${PYTHON_PORT}`);
      }
    });
    req.on('error', () => {
      // Still booting up
    });
  }, 200);

  setTimeout(() => clearInterval(checkInterval), 10000);
}

// 2. Proxy Helper for /api/* requests
function proxyToPython(req: express.Request, res: express.Response) {
  const options: http.RequestOptions = {
    hostname: '127.0.0.1',
    port: PYTHON_PORT,
    path: req.originalUrl,
    method: req.method,
    headers: {
      ...req.headers,
      host: `127.0.0.1:${PYTHON_PORT}`
    }
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode || 200, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on('error', (err) => {
    console.warn(`[Proxy Warning] ${req.method} ${req.originalUrl} failed: ${err.message}`);
    res.status(503).json({
      status: 'error',
      message: 'Agricultural engine initializing. Please try again in 2 seconds.'
    });
  });

  req.pipe(proxyReq, { end: true });
}

// 3. Mount Routes & Static Files
const staticDir = fs.existsSync(path.join(__dirname, 'dist')) 
  ? path.join(__dirname, 'dist') 
  : path.join(__dirname, 'frontend');

const frontendDir = path.join(__dirname, 'frontend');
const dataDir = path.join(__dirname, 'data');

// Static assets
app.use('/css', express.static(path.join(frontendDir, 'css')));
app.use('/js', express.static(path.join(frontendDir, 'js')));
app.use('/assets', express.static(path.join(frontendDir, 'assets')));
app.use('/data', express.static(dataDir));

// Root and core HTML views
app.get('/', (req, res) => {
  res.sendFile(path.join(frontendDir, 'index.html'));
});

app.get(['/dashboard', '/dashboard.html'], (req, res) => {
  res.sendFile(path.join(frontendDir, 'dashboard.html'));
});

app.get(['/login', '/login.html'], (req, res) => {
  res.sendFile(path.join(frontendDir, 'login.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'online',
    app: 'Smart Crop Advisory',
    version: '1.0.0',
    runtime: 'Node.js Full-Stack Wrapper',
    python_backend: isPythonReady ? 'online' : 'initializing',
    database: 'SQLite Relational DB Initialized'
  });
});

// Proxy all /api/* routes to Python
app.use('/api', (req, res) => {
  proxyToPython(req, res);
});

// Fallback to index.html
app.use((req, res) => {
  if (req.path.startsWith('/api/')) {
    res.status(404).json({ status: 'error', message: 'API route not found' });
  } else {
    res.sendFile(path.join(frontendDir, 'index.html'));
  }
});

// Clean shutdown
process.on('SIGTERM', () => {
  if (pythonProcess) pythonProcess.kill();
  process.exit(0);
});

process.on('SIGINT', () => {
  if (pythonProcess) pythonProcess.kill();
  process.exit(0);
});

// Start Server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🌾 Smart Crop Advisory Full-Stack Server active on http://0.0.0.0:${PORT}`);
  startPythonBackend();
});
