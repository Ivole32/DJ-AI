/**
 * API Client Utility
 * Centralized HTTP client for making authenticated API requests
 * @module utils/api-client
 */

/**
 * HTTP Methods
 * @typedef {'GET'|'POST'|'PUT'|'DELETE'|'PATCH'} HttpMethod
 */

/**
 * API Client for making authenticated HTTP requests
 * Handles token refresh automatically on 401 errors
 */
class ApiClient {
    /**
     * Create a new API Client
     * @param {string} baseUrl - Base URL for API requests
     */
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    /**
     * Make an HTTP request with automatic token refresh
     * @param {string} endpoint - API endpoint (e.g., '/playlist/create')
     * @param {Object} options - Fetch options
     * @param {HttpMethod} options.method - HTTP method
     * @param {Object} [options.body] - Request body (will be JSON stringified)
     * @param {Object} [options.headers] - Additional headers
     * @param {boolean} [options.skipAuth=false] - Skip authentication headers
     * @returns {Promise<Response>} Fetch response
     * @throws {Error} If request fails after token refresh attempt
     */
    async request(endpoint, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        const requestOptions = {
            method: options.method || 'GET',
            headers: defaultHeaders,
            credentials: 'include', // Include cookies for auth
            ...options
        };

        // Stringify body if it's an object
        if (options.body && typeof options.body === 'object') {
            requestOptions.body = JSON.stringify(options.body);
        }

        const url = `${this.baseUrl}${endpoint}`;
        let response = await fetch(url, requestOptions);

        // Handle 401 - Attempt token refresh
        if (response.status === 401 && !this.isAuthEndpoint(endpoint)) {
            console.log('Access token expired, attempting refresh...');
            
            const refreshSuccess = await this.refreshToken();
            if (refreshSuccess) {
                console.log('Token refreshed successfully, retrying original request...');
                // Retry original request with new token
                response = await fetch(url, requestOptions);
            } else {
                console.warn('Token refresh failed, redirecting to login...');
                this.redirectToLogin();
                throw new Error('Session expired. Please log in again.');
            }
        }

        return response;
    }

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} [options] - Additional fetch options
     * @returns {Promise<Object>} Parsed JSON response
     */
    async get(endpoint, options = {}) {
        const response = await this.request(endpoint, {
            ...options,
            method: 'GET'
        });
        
        if (!response.ok) {
            throw await this.handleError(response);
        }
        
        return response.json();
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} body - Request body
     * @param {Object} [options] - Additional fetch options
     * @returns {Promise<Object>} Parsed JSON response
     */
    async post(endpoint, body, options = {}) {
        const response = await this.request(endpoint, {
            ...options,
            method: 'POST',
            body
        });
        
        if (!response.ok) {
            throw await this.handleError(response);
        }
        
        return response.json();
    }

    /**
     * Make a PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} body - Request body
     * @param {Object} [options] - Additional fetch options
     * @returns {Promise<Object>} Parsed JSON response
     */
    async put(endpoint, body, options = {}) {
        const response = await this.request(endpoint, {
            ...options,
            method: 'PUT',
            body
        });
        
        if (!response.ok) {
            throw await this.handleError(response);
        }
        
        return response.json();
    }

    /**
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} [options] - Additional fetch options
     * @returns {Promise<Object>} Parsed JSON response
     */
    async delete(endpoint, options = {}) {
        const response = await this.request(endpoint, {
            ...options,
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw await this.handleError(response);
        }
        
        return response.json();
    }

    /**
     * Refresh the access token using the refresh token
     * @returns {Promise<boolean>} True if refresh was successful
     * @private
     */
    async refreshToken() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            return response.ok;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    }

    /**
     * Handle API error responses
     * @param {Response} response - Fetch response
     * @returns {Promise<Error>} Error with formatted message
     * @private
     */
    async handleError(response) {
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = { detail: `Request failed with status ${response.status}` };
        }

        const message = this.formatErrorMessage(errorData);
        const error = new Error(message);
        error.status = response.status;
        error.data = errorData;
        
        return error;
    }

    /**
     * Format API error messages
     * @param {Object|string} error - Error object or string
     * @returns {string} Formatted error message
     * @private
     */
    formatErrorMessage(error) {
        // Handle 422 validation errors with detail array
        if (error.detail && Array.isArray(error.detail)) {
            const messages = error.detail.map(err => err.msg || JSON.stringify(err));
            return messages.join(', ');
        }
        // Handle simple string detail
        if (error.detail && typeof error.detail === 'string') {
            return error.detail;
        }
        // Handle string error
        if (typeof error === 'string') {
            return error;
        }
        // Handle Error object
        if (error.message) {
            return error.message;
        }
        // Fallback
        return 'An error occurred';
    }

    /**
     * Check if endpoint is an auth endpoint (to avoid refresh loops)
     * @param {string} endpoint - API endpoint
     * @returns {boolean} True if endpoint is auth-related
     * @private
     */
    isAuthEndpoint(endpoint) {
        return endpoint.includes('/auth/login') || 
               endpoint.includes('/auth/refresh') || 
               endpoint.includes('/auth/logout') ||
               endpoint.includes('/auth/register');
    }

    /**
     * Redirect user to login page
     * @private
     */
    redirectToLogin() {
        localStorage.removeItem(AppConfig.storage.userKey);
        // Never redirect to login from the landing page
        const path = window.location.pathname;
        if (
            !path.includes('login.html') &&
            path !== '/' &&
            path !== '/index.html'
        ) {
            const redirect = encodeURIComponent(path);
            window.location.href = `${AppConfig.app.loginRoute}?redirect=${redirect}`;
        }
    }
}

// Create and export a singleton instance
const apiClient = new ApiClient(AppConfig.getApiUrl(''));