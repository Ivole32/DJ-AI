/**
 * Protected Page Routes
 * Routes that require authentication
 * @module routes/protected
 */

import express from 'express';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { requireAuth } from '../middleware/auth.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const router = express.Router();

/**
 * Get path to public directory
 * @returns {string} Path to public directory
 */
function getPublicPath(filename) {
  return join(__dirname, '../../public', filename);
}

/**
 * Redirect /profile/me to /profile
 */
router.get('/profile/me', requireAuth, (req, res) => {
  res.redirect('/profile');
});

/**
 * Public user profile page
 * URL: /profile/:username
 */
router.get('/profile/:username', (req, res) => {
  const username = req.params.username;
  
  // Prevent collision with /profile route
  if (username === 'me') {
    return res.redirect('/profile');
  }
  
  res.sendFile(getPublicPath('user-profile.html'));
});

/**
 * Own profile page (protected)
 * URL: /profile
 */
router.get('/profile', requireAuth, (req, res) => {
  res.sendFile(getPublicPath('profile.html'));
});

/**
 * Main app page (protected)
 * URL: /app
 */
router.get('/app', requireAuth, (req, res) => {
  res.sendFile(getPublicPath('app.html'));
});

/**
 * Playlists page (protected)
 * URL: /playlists
 */
router.get('/playlists', requireAuth, (req, res) => {
  res.sendFile(getPublicPath('playlists.html'));
});

export default router;