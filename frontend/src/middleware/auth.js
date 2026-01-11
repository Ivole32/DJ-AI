/**
 * Authentication Middleware
 * Handles JWT token verification and protected route access
 * @module middleware/auth
 */

import { config } from '../../config.js';

/**
 * Refresh access token using refresh token
 * @param {string} refreshToken - JWT refresh token
 * @returns {Promise<{success: boolean, accessToken?: string}>}
 */
async function refreshAccessToken(refreshToken) {
  const apiUrl = process.env.API_URL || 'http://djai-api:8080';
  
  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/refresh`, {
      method: 'GET',
      headers: {
        'Cookie': `refresh_token=${refreshToken}`
      }
    });
    
    if (response.ok) {
      // Extract new access token from response cookies
      const setCookieHeader = response.headers.get('set-cookie');
      if (setCookieHeader) {
        const match = setCookieHeader.match(/access_token=([^;]+)/);
        if (match) {
          return { success: true, accessToken: match[1] };
        }
      }
      return { success: true };
    }
    
    return { success: false };
  } catch (error) {
    if (config.debug.logErrors) {
      console.error(`[AUTH ERROR] Token refresh failed: ${error.message}`);
    }
    return { success: false };
  }
}

/**
 * Verify JWT token with backend API
 * @param {string} accessToken - JWT access token
 * @returns {Promise<{valid: boolean, user?: Object}>}
 */
async function verifyToken(accessToken) {
  const apiUrl = process.env.API_URL || 'http://djai-api:8080';
  
  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/verify`, {
      method: 'GET',
      headers: {
        'Cookie': `access_token=${accessToken}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      return { valid: true, user: data.user };
    }
    
    return { valid: false };
  } catch (error) {
    if (config.debug.logErrors) {
      console.error(`[AUTH ERROR] Token verification failed: ${error.message}`);
    }
    return { valid: false };
  }
}

/**
 * Authentication middleware for protected routes
 * Verifies JWT token and redirects to login if invalid
 * 
 * @example
 * app.get('/protected', requireAuth, (req, res) => {
 *   res.send('Protected content');
 * });
 * 
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export async function requireAuth(req, res, next) {
  // Get token from cookie
  const accessToken = req.cookies.access_token;
  const refreshToken = req.cookies.refresh_token;
  
  if (!accessToken) {
    // No access token, try refresh if available
    if (refreshToken) {
      if (config.debug.enabled) {
        console.log(`[AUTH] No access token, attempting refresh for ${req.path}`);
      }
      
      const refreshResult = await refreshAccessToken(refreshToken);
      if (refreshResult.success && refreshResult.accessToken) {
        // Set new access token in cookie and retry
        res.cookie('access_token', refreshResult.accessToken, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: 30 * 60 * 1000 // 30 minutes
        });
        
        // Verify the new token
        const { valid, user } = await verifyToken(refreshResult.accessToken);
        if (valid) {
          req.user = user;
          if (config.debug.enabled) {
            console.log(`[AUTH] Token refreshed, user authenticated: ${user?.username || 'unknown'}`);
          }
          return next();
        }
      }
    }
    
    if (config.debug.enabled) {
      console.log(`[AUTH] No token found for ${req.path}, redirecting to login`);
    }
    return res.redirect('/login?redirect=' + encodeURIComponent(req.path));
  }
  
  // Verify token with backend
  const { valid, user } = await verifyToken(accessToken);
  
  if (valid) {
    // Token is valid, attach user info to request and proceed
    req.user = user;
    
    if (config.debug.enabled) {
      console.log(`[AUTH] User authenticated: ${user?.username || 'unknown'}`);
    }
    
    return next();
  } else {
    // Token invalid or expired, try refresh
    if (refreshToken) {
      if (config.debug.enabled) {
        console.log(`[AUTH] Token expired, attempting refresh for ${req.path}`);
      }
      
      const refreshResult = await refreshAccessToken(refreshToken);
      if (refreshResult.success) {
        // Refresh succeeded, redirect to same page to retry with new token
        if (config.debug.enabled) {
          console.log(`[AUTH] Token refreshed successfully, redirecting to ${req.path}`);
        }
        return res.redirect(req.originalUrl);
      }
    }
    
    // Token invalid or expired and refresh failed
    if (config.debug.enabled) {
      console.log(`[AUTH] Invalid token for ${req.path}, redirecting to login`);
    }
    return res.redirect('/login?redirect=' + encodeURIComponent(req.path));
  }
}

/**
 * Optional authentication middleware
 * Attaches user info if token is valid, but doesn't require authentication
 * 
 * @param {Request} req - Express request object
 * @param {Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export async function optionalAuth(req, res, next) {
  const accessToken = req.cookies.access_token;
  
  if (accessToken) {
    const { valid, user } = await verifyToken(accessToken);
    if (valid) {
      req.user = user;
    }
  }
  
  next();
}