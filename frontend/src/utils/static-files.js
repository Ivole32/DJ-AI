/**
 * Static File Utilities
 * Handles serving HTML files without extensions
 * @module utils/static-files
 */

import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Get path to public directory
 * @param {string} filename - Filename to append
 * @returns {string} Full path to file
 */
export function getPublicPath(filename = '') {
  return join(__dirname, '../../public', filename);
}

/**
 * Middleware to redirect .html requests to extensionless routes
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export function redirectHtmlExtension(req, res, next) {
  if (req.path.endsWith('.html')) {
    const routeWithoutExtension = req.path.replace(/\.html$/, '');
    return res.redirect(routeWithoutExtension);
  }
  next();
}

/**
 * Middleware to serve HTML files without extension
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export function serveHtmlWithoutExtension(req, res, next) {
  // Skip if already has extension or is an API route
  if (req.path.includes('.') || req.path.startsWith('/api/')) {
    return next();
  }
  
  // Try to serve HTML file without extension
  const htmlPath = getPublicPath(`${req.path}.html`);
  
  if (existsSync(htmlPath)) {
    return res.sendFile(htmlPath);
  }
  
  next();
}