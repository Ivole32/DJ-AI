/**
 * Frontend Server Configuration
 * Centralized configuration for the Express server
 * @module config
 */

export const config = {
  // Server Settings
  server: {
    port: process.env.PORT || 3000,
    host: process.env.HOST || '0.0.0.0',
    env: process.env.NODE_ENV || 'development'
  },

  // Debug Mode
  debug: {
    enabled: process.env.DEBUG === 'true' || false,
    logRequests: process.env.LOG_REQUESTS === 'true' || false,
    logErrors: true
  },

  // Rate Limiting
  rateLimit: {
    enabled: process.env.RATE_LIMIT_ENABLED !== 'false', // Enabled by default
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 1000, // Max 1000 requests per window
    message: 'Too many requests from this IP, please try again later.',
    skipSuccessfulRequests: false,
    skipFailedRequests: false
  },

  // CORS Settings
  cors: {
    enabled: process.env.CORS_ENABLED !== 'false',
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true
  },

  // Security Headers
  security: {
    enableHelmet: true,
    contentSecurityPolicy: process.env.NODE_ENV === 'production'
  },

  // Static Files
  static: {
    directory: 'public',
    options: {
      maxAge: process.env.NODE_ENV === 'production' ? '1d' : 0,
      etag: true
    }
  },

  // Logging
  logging: {
    enabled: true,
    format: process.env.NODE_ENV === 'production' ? 'combined' : 'dev',
    logFile: process.env.LOG_FILE || null
  }
};

// Helper function to check if in development mode
export const isDevelopment = () => config.server.env === 'development';

// Helper function to check if in production mode
export const isProduction = () => config.server.env === 'production';

// Log configuration on startup (only in debug mode)
if (config.debug.enabled) {
  console.log('[CONFIG] Server configuration loaded:', JSON.stringify(config, null, 2));
}
