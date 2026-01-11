/**
 * Request Logger Middleware
 * Logs incoming HTTP requests in development mode
 * @module middleware/logger
 */

import { config } from '../../config.js';

/**
 * Log incoming HTTP requests
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export function requestLogger(req, res, next) {
  if (config.debug.logRequests) {
    const timestamp = new Date().toISOString();
    const method = req.method.padEnd(6);
    const url = req.url;
    const ip = req.ip || req.connection.remoteAddress;
    
    console.log(`[${timestamp}] ${method} ${url} - IP: ${ip}`);
  }
  
  next();
}

/**
 * Log response time
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export function responseTimeLogger(req, res, next) {
  if (config.debug.logRequests) {
    const startTime = Date.now();
    
    res.on('finish', () => {
      const duration = Date.now() - startTime;
      const status = res.statusCode;
      const statusColor = status >= 500 ? '\x1b[31m' : status >= 400 ? '\x1b[33m' : '\x1b[32m';
      const resetColor = '\x1b[0m';
      
      console.log(`  → ${statusColor}${status}${resetColor} in ${duration}ms`);
    });
  }
  
  next();
}