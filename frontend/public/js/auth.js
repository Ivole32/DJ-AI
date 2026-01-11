// Authentication Service
class AuthService {
    constructor() {
        this.API_URL = AppConfig.getApiUrl('');
        this.USER_KEY = AppConfig.storage.userKey;
    }

    // Helper to format error messages from API responses
    formatErrorMessage(error) {
        return formatApiError(error);
    }

    // Helper method to make API calls with credentials
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            credentials: 'include', // Include cookies
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        let response = await fetch(`${this.API_URL}${endpoint}`, {
            ...defaultOptions,
            ...options
        });

        // If unauthorized and not already a refresh/login request, try to refresh token
        if (response.status === 401 && !endpoint.includes('/auth/refresh') && !endpoint.includes('/auth/login')) {
            console.log('Access token expired, attempting refresh...');
            
            const refreshSuccess = await this.refreshAccessToken();
            if (refreshSuccess) {
                // Retry original request with new access token
                console.log('Token refreshed, retrying original request...');
                response = await fetch(`${this.API_URL}${endpoint}`, {
                    ...defaultOptions,
                    ...options
                });
            } else {
                // Refresh failed, redirect to login
                console.log('Token refresh failed, redirecting to login...');
                localStorage.removeItem(this.USER_KEY);
                window.location.href = AppConfig.app.loginRoute;
                throw new Error('Session expired. Please log in again.');
            }
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(this.formatErrorMessage(error));
        }

        return response.json();
    }

    // Refresh access token using refresh token
    async refreshAccessToken() {
        // Check if refresh_token cookie exists
        if (!document.cookie.split('; ').find(row => row.startsWith('refresh_token='))) {
            console.warn('No refresh_token cookie present, skipping refresh request');
            return false;
        }
        try {
            const response = await fetch(`${this.API_URL}/auth/refresh`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                console.log('Access token refreshed successfully');
                return true;
            } else {
                console.warn('Failed to refresh access token');
                return false;
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    }

    // Login with username/password
    async login(username, password) {
        try {
            const response = await this.apiCall('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            console.log('Login successful, fetching user data...');
            
            // Get user data
            const userData = await this.getCurrentUserFromAPI();
            if (userData) {
                localStorage.setItem(this.USER_KEY, JSON.stringify(userData));
                console.log('User data saved to localStorage:', userData);
                return { success: true, user: userData };
            } else {
                console.error('Failed to get user data after login');
                return { success: false, error: 'Failed to retrieve user data' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    }

    // Register new user
    async register(username, email, password) {
        try {
            await this.apiCall('/user/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });

            // Auto-login after registration
            return await this.login(username, password);
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: error.message };
        }
    }

    // Logout
    async logout() {
        try {
            // Send logout request to API
            const response = await fetch(`${this.API_URL}/auth/logout`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                console.log('Logout successful');
            } else {
                console.warn('Logout request failed, but clearing local session anyway');
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Always clear local storage and redirect
            localStorage.removeItem(this.USER_KEY);
            window.location.href = AppConfig.app.loginRoute;
        }
    }

    // Check if user is authenticated
    async isAuthenticatedAsync() {
        // Check if user data exists in localStorage
        if (localStorage.getItem(this.USER_KEY)) {
            return true;
        }
        
        // Try to refresh token if no user data in localStorage
        const refreshSuccess = await this.refreshAccessToken();
        if (refreshSuccess) {
            // Get user data after successful refresh
            const userData = await this.getCurrentUserFromAPI();
            if (userData) {
                localStorage.setItem(this.USER_KEY, JSON.stringify(userData));
                return true;
            }
        }
        return false;
    }
    
    // Synchronous version for compatibility
    isAuthenticated() {
        // Check if user data exists in localStorage
        return !!localStorage.getItem(this.USER_KEY);
    }

    // Get current user from API
    async getCurrentUserFromAPI() {
        try {
            return await this.apiCall('/user/me', { method: 'GET' });
        } catch (error) {
            console.error('Get user error:', error);
            return null;
        }
    }

    // Get current user from localStorage
    getCurrentUser() {
        const userStr = localStorage.getItem(this.USER_KEY);
        return userStr ? JSON.parse(userStr) : null;
    }

    // Refresh user data
    async refreshUserData() {
        const userData = await this.getCurrentUserFromAPI();
        if (userData) {
            localStorage.setItem(this.USER_KEY, JSON.stringify(userData));
        }
        return userData;
    }

    // Social login
    async socialLogin(provider) {
        // Redirect to OAuth provider
        const authUrl = `${this.API_URL}/auth/${provider.toLowerCase()}`;
        window.location.href = authUrl;
    }

    // Password reset (placeholder - needs backend implementation)
    async resetPassword(email) {
        console.log('Password reset for:', email);
        // TODO: Implement when backend endpoint is ready
        return { success: true, message: 'Password reset feature is still being implemented' };
    }
}

// Initialize auth service - lazy initialization to ensure AppConfig is loaded
let authService;
function getAuthService() {
    if (!authService) {
        authService = new AuthService();
    }
    return authService;
}

// Initialize social login buttons based on config
function initializeSocialButtons() {
    const socialLoginDiv = document.querySelector('.social-login');
    if (!socialLoginDiv) return;

    // Check if any provider is enabled
    if (!AppConfig.hasSocialLogin()) {
        socialLoginDiv.style.display = 'none';
        return;
    }

    // Get button container
    const buttonContainer = socialLoginDiv.querySelector('.social-buttons') || socialLoginDiv;
    
    // Show/hide buttons based on config
    const googleBtn = buttonContainer.querySelector('.btn-google');
    const spotifyBtn = buttonContainer.querySelector('.btn-spotify');
    const githubBtn = buttonContainer.querySelector('.btn-github');

    if (googleBtn) {
        googleBtn.style.display = AppConfig.authProviders.google ? 'block' : 'none';
    }
    if (spotifyBtn) {
        spotifyBtn.style.display = AppConfig.authProviders.spotify ? 'block' : 'none';
    }
    if (githubBtn) {
        githubBtn.style.display = AppConfig.authProviders.github ? 'block' : 'none';
    }
}

// Login form handler
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username')?.value || document.getElementById('email')?.value;
        const password = document.getElementById('password').value;
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Signing in...';
        
        const result = await getAuthService().login(username, password);
        
        if (result.success) {
            window.location.href = AppConfig.app.defaultRoute;
        } else {
            toast.error('Login failed: ' + formatApiError(result.error));
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // Forgot password handler
    document.getElementById('forgotPassword')?.addEventListener('click', async (e) => {
        e.preventDefault();
        const email = prompt('Please enter your email address:');
        if (email) {
            const result = await getAuthService().resetPassword(email);
            toast.info(result.message || 'A reset link has been sent to your email.');
        }
    });

    // Social login handlers
    document.querySelector('.btn-google')?.addEventListener('click', () => {
        getAuthService().socialLogin('Google');
    });

    document.querySelector('.btn-spotify')?.addEventListener('click', () => {
        getAuthService().socialLogin('Spotify');
    });

    document.querySelector('.btn-github')?.addEventListener('click', () => {
        getAuthService().socialLogin('GitHub');
    });

    // Initialize social buttons visibility
    initializeSocialButtons();
}

// Register form handler
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        // Ensure config is loaded
        if (!ConfigAPI.values.password_min_length) await ConfigAPI.load();
        const cfg = ConfigAPI.values;
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (password !== confirmPassword) {
            toast.error('Passwords do not match!');
            return;
        }
        if (password.length < cfg.password_min_length || password.length > cfg.password_max_length) {
            toast.error(`Password must be ${cfg.password_min_length}-${cfg.password_max_length} characters long.`);
            return;
        }
        if (username.length < cfg.username_min_length || username.length > cfg.username_max_length) {
            toast.error(`Username must be ${cfg.username_min_length}-${cfg.username_max_length} characters long.`);
            return;
        }
        // Add more dynamic checks as needed (bio, genres, etc.)

        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering...';

        const result = await getAuthService().register(username, email, password);

        if (result.success) {
            window.location.href = AppConfig.app.defaultRoute;
        } else {
            toast.error('Registration failed: ' + formatApiError(result.error));
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // Initialize social buttons visibility
    initializeSocialButtons();
}

// Logout handler (global) - Initialize when DOM is ready
function initLogoutHandler() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await getAuthService().logout();
        });
    }
}

// Initialize logout handler when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLogoutHandler);
} else {
    initLogoutHandler();
}

// Protect pages that require authentication
async function requireAuth() {
    const authService = getAuthService();
    const path = window.location.pathname;
    const isLoginOrPublicPage =
        path === '/' ||
        path === '/index.html' ||
        path.includes('login') ||
        path.includes('register') ||
        path.includes('landing') ||
        path.includes('index');

    if (isLoginOrPublicPage) {
        return; // Skip auth check on public pages
    }
    
    // Try to authenticate (will attempt refresh if needed)
    const isAuthenticated = await authService.isAuthenticatedAsync();
    
    if (!isAuthenticated) {
        console.log('Authentication failed, redirecting to login');
        window.location.href = 'login.html';
    }
}

// Check auth on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', requireAuth);
} else {
    requireAuth();
}