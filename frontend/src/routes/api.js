/**
 * API Routes
 * Internal API endpoints for the frontend
 * @module routes/api
 */

import express from 'express';
import { config } from '../../config.js';

const router = express.Router();

/**
 * Health check endpoint
 * GET /ping
 */
router.get('/ping', (req, res) => {
  res.json({
    result: 'Pong!',
    timestamp: new Date().toISOString(),
    environment: config.server.env
  });
});

/**
 * Auth providers configuration
 * GET /api/config/auth-providers
 * Returns which authentication providers are enabled
 */
router.get('/config/auth-providers', (req, res) => {
  res.json({
    google: false,   // Set to true to enable Google login
    spotify: false,  // Set to true to enable Spotify login
    github: false    // Set to true to enable GitHub login
  });
});

/**
 * Server status endpoint (debug mode only)
 * GET /debug/status
 */
if (config.debug.enabled) {
  router.get('/debug/status', (req, res) => {
    res.json({
      server: {
        uptime: process.uptime(),
        environment: config.server.env,
        nodeVersion: process.version,
        platform: process.platform,
        pid: process.pid
      },
      config: {
        rateLimit: {
          enabled: config.rateLimit.enabled,
          maxRequests: config.rateLimit.maxRequests,
          windowMs: config.rateLimit.windowMs
        },
        debug: config.debug
      },
      memory: process.memoryUsage(),
      timestamp: new Date().toISOString()
    });
  });
}

export default router;