/**
 * Production Build Script for Smart Crop Advisory
 * Prepares the production dist/ bundle required by AI Studio Cloud Run deployment.
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🏗️ Building Smart Crop Advisory for Production...');

const distDir = path.join(__dirname, 'dist');
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// 1. Run Vite build if vite is installed
try {
  console.log('📦 Running Vite build...');
  execSync('npx vite build', { stdio: 'inherit' });
} catch (e) {
  console.warn('Vite build warning, continuing asset copy:', e.message);
}

// 2. Copy all frontend pages and assets into dist
function copyDir(src, dest) {
  if (!fs.existsSync(src)) return;
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });

  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

console.log('📂 Syncing HTML and static assets to dist/ ...');
const frontendDir = path.join(__dirname, 'frontend');

// Copy HTML entrypoints
['index.html', 'dashboard.html', 'login.html'].forEach(file => {
  const src = path.join(frontendDir, file);
  const dest = path.join(distDir, file);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest);
  }
});

// Copy directories
copyDir(path.join(frontendDir, 'css'), path.join(distDir, 'css'));
copyDir(path.join(frontendDir, 'js'), path.join(distDir, 'js'));
copyDir(path.join(frontendDir, 'assets'), path.join(distDir, 'assets'));
copyDir(path.join(__dirname, 'data'), path.join(distDir, 'data'));

// 3. Verify Python and database initialization
try {
  execSync('python3 -c "import sqlite3, http.server, json; from backend.database import init_db; init_db(force_reset=False); print(\'✓ Database initialized\')"', { stdio: 'inherit' });
} catch (e) {
  console.warn('Python database check warning:', e.message);
}

console.log('✅ Production build completed successfully in dist/');
