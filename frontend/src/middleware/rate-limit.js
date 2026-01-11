/**
 * Rate Limiting Middleware
 * Protects against abuse and DoS attacks
 * @module middleware/rate-limit
 */

import rateLimit from 'express-rate-limit';
import { config } from '../../config.js';

/**
 * Create rate limiter with custom configuration
 * @returns {Function} Express rate limiter middleware
 */
export function createRateLimiter() {
  if (!config.rateLimit.enabled) {
    // Return no-op middleware if rate limiting is disabled
    return (req, res, next) => next();
  }
  
  const limiter = rateLimit({
    windowMs: config.rateLimit.windowMs,
    max: config.rateLimit.maxRequests,
    message: config.rateLimit.message,
    standardHeaders: true,
    legacyHeaders: false,
    skipSuccessfulRequests: config.rateLimit.skipSuccessfulRequests,
    skipFailedRequests: config.rateLimit.skipFailedRequests,
    
    handler: (req, res) => {
      if (config.debug.enabled) {
        console.warn(`[RATE LIMIT] IP ${req.ip} exceeded limit`);
      }
      
      res.status(429).json({
        error: 'Too Many Requests',
        message: config.rateLimit.message,
        retryAfter: Math.ceil(config.rateLimit.windowMs / 1000)
      });
    }
  });
  
  if (config.debug.enabled) {
    console.log(`[RATE LIMIT] Enabled: ${config.rateLimit.maxRequests} requests per ${config.rateLimit.windowMs / 1000}s`);
  }
  
  return limiter;
}