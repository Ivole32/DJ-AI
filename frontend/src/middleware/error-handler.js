/**
 * Error Handling Middleware
 * Centralized error handling for the application
 * @module middleware/error-handler
 */

import { config, isDevelopment } from '../../config.js';

/**
 * 404 Not Found handler
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 */
export function notFoundHandler(req, res) {
  if (config.debug.enabled) {
    console.warn(`[404] Route not found: ${req.method} ${req.url}`);
  }
  
  // Serve custom 404 page for HTML requests
  if (req.accepts('html')) {
    return res.status(404).sendFile('404.html', { 
      root: './public' 
    });
  }
  
  // JSON response for API requests
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.url} not found`
  });
}

/**
 * Global error handler
 * @param {Error} err - Error object
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export function errorHandler(err, req, res, next) {
  if (config.debug.logErrors) {
    console.error(`[ERROR] ${err.message}`);
    if (isDevelopment()) {
      console.error(err.stack);
    }
  }
  
  const statusCode = err.status || err.statusCode || 500;
  
  res.status(statusCode).json({
    error: isDevelopment() ? err.message : 'Internal Server Error',
    ...(isDevelopment() && { 
      stack: err.stack,
      details: err.details 
    })
  });
}