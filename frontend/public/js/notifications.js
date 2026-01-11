/**
 * Toast Notification System
 * Shows elegant notifications in the top right corner
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Type of toast: 'success', 'error', 'info', 'warning'
     * @param {number} duration - Duration in milliseconds (default: 4000)
     */
    show(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        // Icon based on type
        const icons = {
            success: '✓',
            error: '✕',
            info: 'i',
            warning: '!'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">${message}</div>
            <button class="toast-close" aria-label="Close">&times;</button>
        `;

        // Close button functionality
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.removeToast(toast);
        });

        // Add to container
        this.container.appendChild(toast);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeToast(toast);
            }, duration);
        }

        return toast;
    }

    removeToast(toast) {
        toast.classList.add('toast-removing');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300); // Match animation duration
    }

    // Convenience methods
    success(message, duration = 4000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    info(message, duration = 4000) {
        return this.show(message, 'info', duration);
    }

    warning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    }
}

// Create global instance
const toast = new ToastNotification();

// Alternative function to replace alert()
function showNotification(message, type = 'info') {
    toast.show(message, type);
}

/**
 * Format API error messages, especially for 422 validation errors
 * @param {Object|string} error - Error object from API response
 * @returns {string} Formatted error message
 */
function formatApiError(error) {
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