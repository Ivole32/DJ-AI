/**
 * Custom Confirm Dialog
 * Provides a modern alternative to browser confirm() dialogs
 */

class ConfirmDialog {
    constructor() {
        this.createModal();
    }

    createModal() {
        // Create modal HTML
        const modal = document.createElement('div');
        modal.id = 'confirmModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content confirm-dialog">
                <h3 id="confirmTitle">Confirm Action</h3>
                <p id="confirmMessage">Are you sure?</p>
                <div class="confirm-actions">
                    <button class="btn btn-secondary" id="confirmCancel">Cancel</button>
                    <button class="btn btn-danger" id="confirmOk">Confirm</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        this.modal = modal;
        this.titleEl = modal.querySelector('#confirmTitle');
        this.messageEl = modal.querySelector('#confirmMessage');
        this.cancelBtn = modal.querySelector('#confirmCancel');
        this.okBtn = modal.querySelector('#confirmOk');
        
        // Close on click outside
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
                if (this.rejectCallback) this.rejectCallback();
            }
        });
    }

    /**
     * Show confirmation dialog
     * @param {Object} options - Dialog options
     * @param {string} options.title - Dialog title
     * @param {string} options.message - Dialog message
     * @param {string} options.confirmText - Confirm button text
     * @param {string} options.cancelText - Cancel button text
     * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
     */
    show({ title = 'Confirm Action', message = 'Are you sure?', confirmText = 'Confirm', cancelText = 'Cancel' } = {}) {
        return new Promise((resolve, reject) => {
            this.titleEl.textContent = title;
            this.messageEl.textContent = message;
            this.okBtn.textContent = confirmText;
            this.cancelBtn.textContent = cancelText;
            
            this.modal.style.display = 'block';
            
            // Store callbacks
            this.rejectCallback = reject;
            
            // Remove old listeners
            const newOkBtn = this.okBtn.cloneNode(true);
            const newCancelBtn = this.cancelBtn.cloneNode(true);
            this.okBtn.parentNode.replaceChild(newOkBtn, this.okBtn);
            this.cancelBtn.parentNode.replaceChild(newCancelBtn, this.cancelBtn);
            this.okBtn = newOkBtn;
            this.cancelBtn = newCancelBtn;
            
            // Add new listeners
            this.okBtn.addEventListener('click', () => {
                this.hide();
                resolve(true);
            });
            
            this.cancelBtn.addEventListener('click', () => {
                this.hide();
                resolve(false);
            });
            
            // Focus cancel button by default
            this.cancelBtn.focus();
        });
    }

    hide() {
        this.modal.style.display = 'none';
    }
}

// Create global instance
const confirmDialog = new ConfirmDialog();

/**
 * Show a confirm dialog (replacement for window.confirm)
 * @param {string} message - Message to display
 * @param {string} title - Optional title
 * @returns {Promise<boolean>}
 */
async function customConfirm(message, title = 'Confirm') {
    return await confirmDialog.show({ 
        title, 
        message, 
        confirmText: 'Yes', 
        cancelText: 'No' 
    });
}