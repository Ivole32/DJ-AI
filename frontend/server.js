/**
 * DJ-AI Frontend Server
 * Express server for serving the DJ-AI frontend application
 * @module server
 */

import express from 'express';
import { config } from './config.js';
import { setupMiddleware, setupRoutes, setupErrorHandlers, printBanner } from './src/utils/setup.js';

// Create Express application
const app = express();

// ====================================
// Setup Application
// ====================================

// Configure middleware (logging, rate limiting, parsing, etc.)
setupMiddleware(app);

// Configure routes (API, protected pages, static files)
setupRoutes(app);

// Configure error handling (404, 500, etc.)
setupErrorHandlers(app);

// ====================================
// Start Server
// ====================================

app.listen(config.server.port, config.server.host, () => {
  printBanner(config.server.port, config.server.host);
});

// ====================================
// Graceful Shutdown
// ====================================

process.on('SIGTERM', () => {
  console.log('\n[SHUTDOWN] SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\n[SHUTDOWN] SIGINT received, shutting down gracefully...');
  process.exit(0);
});
