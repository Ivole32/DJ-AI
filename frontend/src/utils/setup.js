/**
 * Application Setup Utility
 * Configures Express middleware and routes
 * @module utils/setup
 */

import express from 'express';
import cookieParser from 'cookie-parser';
import { config } from '../../config.js';
import { requestLogger, responseTimeLogger } from '../middleware/logger.js';
import { createRateLimiter } from '../middleware/rate-limit.js';
import { notFoundHandler, errorHandler } from '../middleware/error-handler.js';
import { redirectHtmlExtension, serveHtmlWithoutExtension, getPublicPath } from './static-files.js';
import protectedRoutes from '../routes/protected.js';
import apiRoutes from '../routes/api.js';

/**
 * Configure Express middleware
 * @param {Express} app - Express application instance
 */
export function setupMiddleware(app) {
  // Request logging
  app.use(requestLogger);
  app.use(responseTimeLogger);
  
  // Rate limiting
  app.use(createRateLimiter());
  
  // Body parsing
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  
  // Cookie parsing (for JWT)
  app.use(cookieParser());
  
  // Redirect .html requests to extensionless routes
  app.use(redirectHtmlExtension);
  
  // Serve static files
  app.use(express.static(getPublicPath(), config.static.options));
}

/**
 * Configure application routes
 * @param {Express} app - Express application instance
 */
export function setupRoutes(app) {
  // API routes (including /ping)
  app.use('/', apiRoutes);

  // Serve index.html for root (public, no auth)
  app.get('/', (req, res) => {
    res.sendFile(getPublicPath('index.html'));
  });

  // Protected page routes (these will not override /)
  app.use('/', protectedRoutes);

  // Serve HTML files without extension
  app.use(serveHtmlWithoutExtension);
}

/**
 * Configure error handling
 * @param {Express} app - Express application instance
 */
export function setupErrorHandlers(app) {
  // 404 handler
  app.use(notFoundHandler);
  
  // Global error handler
  app.use(errorHandler);
}

/**
 * Print server startup banner
 * @param {number} port - Server port
 * @param {string} host - Server host
 */
export function printBanner(port, host) {
  const url = `http://${host}:${port}`;
  const env = config.server.env.padEnd(43);
  const debugStatus = config.debug.enabled ? 'Enabled ✓' : 'Disabled ✗';
  const rateLimitStatus = config.rateLimit.enabled 
    ? `${config.rateLimit.maxRequests} req/${config.rateLimit.windowMs / 1000}s` 
    : 'Disabled';
  
  console.log(`
╔════════════════════════════════════════════════════════════╗
║                     DJ-AI Frontend Server                  ║
╠════════════════════════════════════════════════════════════╣
║  URL:         ${url.padEnd(43)} ║
║  Environment: ${env} ║
║  Debug Mode:  ${debugStatus.padEnd(43)} ║
║  Rate Limit:  ${rateLimitStatus.padEnd(43)} ║
╚════════════════════════════════════════════════════════════╝
  `);
  
  if (config.debug.enabled) {
    console.log('[DEBUG] Debug endpoints available:');
    console.log(`  - GET /debug/status - Server status and configuration`);
    console.log(`  - GET /ping - Health check`);
    console.log('');
  }
}