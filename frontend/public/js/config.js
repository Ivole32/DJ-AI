/**
 * Frontend Client Configuration
 * Configuration for authentication and API settings
 */

const AppConfig = {
    // Backend API Configuration
    api: {
        baseUrl: 'http://localhost:8080',
        prefix: '/api/v1',
        timeout: 30000
    },

    // Authentication Providers Configuration
    // Set to true to enable the login button for each provider
    authProviders: {
        google: false,      // Google OAuth Login
        spotify: false,     // Spotify OAuth Login
        github: false       // GitHub OAuth Login
    },

    // Cookie Settings
    cookies: {
        tokenKey: 'access_token',
        refreshKey: 'refresh_token'
    },

    // Storage Keys
    storage: {
        userKey: 'dj_ai_user',
        themeKey: 'dj_ai_theme'
    },

    // App Settings
    app: {
        name: 'DJ-AI',
        version: '1.0.0',
        defaultRoute: 'app.html',
        loginRoute: 'login.html'
    }
};

// Helper function to get full API URL
AppConfig.getApiUrl = function(endpoint) {
    return `${this.api.baseUrl}${this.api.prefix}${endpoint}`;
};

// Helper function to check if any social login is enabled
AppConfig.hasSocialLogin = function() {
    return Object.values(this.authProviders).some(enabled => enabled);
};

/**
 * Fetch wrapper with automatic token refresh on 401 errors
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} - The fetch response
 */
async function fetchWithTokenRefresh(url, options = {}) {
    // Ensure credentials are included
    const defaultOptions = {
        credentials: 'include',
        ...options
    };
    
    // Don't set Content-Type header if body is FormData (browser will set it with boundary)
    if (options.body instanceof FormData && defaultOptions.headers) {
        delete defaultOptions.headers['Content-Type'];
    }

    let response = await fetch(url, defaultOptions);

    // If unauthorized and not already a refresh/login request, try to refresh token
    if (response.status === 401 && !url.includes('/auth/refresh') && !url.includes('/auth/login') && !url.includes('/auth/logout')) {
        console.log('Access token expired, attempting automatic refresh...');
        
        const refreshResponse = await fetch(`${AppConfig.api.baseUrl}${AppConfig.api.prefix}/auth/refresh`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (refreshResponse.ok) {
            console.log('Token refreshed successfully, retrying original request...');
            // Retry original request with new access token
            response = await fetch(url, defaultOptions);
        } else {
            console.warn('Token refresh failed, user needs to log in again');
            // Clear local storage and redirect to login
            localStorage.removeItem(AppConfig.storage.userKey);
            if (!window.location.pathname.includes('login.html')) {
                window.location.href = AppConfig.app.loginRoute + '?redirect=' + encodeURIComponent(window.location.pathname);
            }
        }
    }

    return response;
}

// Helper function to get enabled providers
AppConfig.getEnabledProviders = function() {
    return Object.entries(this.authProviders)
        .filter(([_, enabled]) => enabled)
        .map(([provider, _]) => provider);
};

// Log configuration in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('[CONFIG] App configuration loaded:', AppConfig);
}