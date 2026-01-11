/**
 * Playlist UI Controller
 * Handles all user interface interactions for the playlist management page
 * @module playlist-ui
 */

/**
 * Playlist UI Controller Class
 * Manages DOM manipulation and event handling for playlists
 */
class PlaylistUIController {
        /**
         * Create a playlist card element
         * @private
         * @param {Playlist} playlist - Playlist data
         * @returns {HTMLElement} Card element
         */
        _createPlaylistCard(playlist) {
            const card = document.createElement('div');
            card.className = 'playlist-card';
            card.innerHTML = `
                <img src="${this._escapeHtml(playlist.coverImage)}" alt="${this._escapeHtml(playlist.name)}">
                <div class="playlist-info">
                    <h3>${this._escapeHtml(playlist.name)}</h3>
                    <p>${this._escapeHtml(playlist.description || '')}</p>
                    <div class="playlist-meta">
                        <span>${playlist.trackCount} Tracks</span>
                        <span>${playlist.isPublic ? '🌐 Public' : '🔒 Private'}</span>
                    </div>
                    <div class="playlist-tags">
                        ${(playlist.tags || []).map(tag => `<span class="tag">${this._escapeHtml(tag)}</span>`).join('')}
                    </div>
                </div>
            `;
            card.addEventListener('click', () => this.openPlaylistDetail(playlist.id));
            return card;
        }
    /**
     * Initialize the Playlist UI Controller
     */
    constructor() {
        this.service = playlistService;
        this.elements = {};
        this.currentPlaylistId = null;
    }

    /**
     * Initialize the controller and set up event listeners
     */
    init() {
        this._cacheElements();
        this._attachEventListeners();
        this.loadPlaylists();
    }

    /**
     * Cache DOM elements for performance
     * @private
     */
    _cacheElements() {
        this.elements = {
            playlistsGrid: document.getElementById('playlistsGrid'),
            createPlaylistBtn: document.getElementById('createPlaylistBtn'),
            createModal: document.getElementById('createPlaylistModal'),
            detailModal: document.getElementById('playlistDetailModal'),
            createPlaylistForm: document.getElementById('createPlaylistForm'),
            
            // Form inputs (create)
            playlistName: document.getElementById('playlistName'),
            playlistDescription: document.getElementById('playlistDescription'),
            playlistTags: document.getElementById('playlistTags'),
            playlistPublic: document.getElementById('playlistPublic'),
            
            // Detail modal elements (view mode)
            playlistTitle: document.getElementById('playlistTitle'),
            playlistDescriptionText: document.getElementById('playlistDescription'),
            playlistTagsDisplay: document.getElementById('playlistTagsDisplay'),
            trackCountInfo: document.getElementById('trackCountInfo'),
            publicStatusInfo: document.getElementById('publicStatusInfo'),
            createdInfo: document.getElementById('createdInfo'),
            
            // Edit mode elements
            playlistViewMode: document.getElementById('playlistViewMode'),
            playlistEditMode: document.getElementById('playlistEditMode'),
            editPlaylistForm: document.getElementById('editPlaylistForm'),
            editPlaylistName: document.getElementById('editPlaylistName'),
            editPlaylistDescription: document.getElementById('editPlaylistDescription'),
            editPlaylistTags: document.getElementById('editPlaylistTags'),
            editPlaylistPublic: document.getElementById('editPlaylistPublic'),
            // Action buttons
            editTracksBtn: document.getElementById('editTracksBtn'),
            // editPlaylistBtn entfernt, da nicht mehr benötigt
            deletePlaylistBtn: document.getElementById('deletePlaylistBtn')
        };
    }

    /**
     * Attach event listeners to UI elements
     * @private
     */
    _attachEventListeners() {
        // Create playlist button
        this.elements.createPlaylistBtn?.addEventListener('click', () => {
            this.showCreateModal();
        });

        // Close modal buttons
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Create playlist form submission
        this.elements.createPlaylistForm?.addEventListener('submit', (e) => {
            this.handleCreatePlaylist(e);
        });
        
        // Edit playlist form submission
        this.elements.editPlaylistForm?.addEventListener('submit', (e) => {
            this.handleUpdatePlaylist(e);
        });

        // Playlist action buttons
        this.elements.editTracksBtn?.addEventListener('click', () => {
            this.handleEditTracks();
        });
        
        // Edit-Button ist entfernt, keine Umschaltung mehr
        
        this.elements.deletePlaylistBtn?.addEventListener('click', () => {
            this.handleDeletePlaylist();
        });
    }

    /**
     * Load and display all playlists
     */
    async loadPlaylists() {
        try {
            const result = await this.service.getPlaylists();
            
            if (result.success) {
                this.displayPlaylists(result.playlists);
            } else {
                console.error('Error loading playlists:', result.error);
                toast.error('Failed to load playlists');
            }
        } catch (error) {
            console.error('Error loading playlists:', error);
            toast.error('Failed to load playlists');
        }
    }

    /**
     * Display playlists in the grid
     * @param {Playlist[]} playlists - Array of playlists to display
     */
    displayPlaylists(playlists) {
        const grid = this.elements.playlistsGrid;
        if (!grid) return;

        grid.innerHTML = '';
        
        if (playlists.length === 0) {
            grid.innerHTML = '<p class="text-center text-gray-500">No playlists yet. Create your first one!</p>';
            return;
        }

        playlists.forEach(playlist => {
            const card = this._createPlaylistCard(playlist);
            grid.appendChild(card);
        });
    }

    /**
     * Create a playlist card element
     * @private
     * @param {Playlist} playlist - Playlist data
     * @returns {HTMLElement} Card element
     */
    async openPlaylistDetail(playlistId) {
        try {
            const result = await this.service.getPlaylist(playlistId);
            if (!result.success) {
                toast.error('Failed to load playlist');
                return;
            }
            const playlist = result.playlist;
            this.currentPlaylistId = playlistId;
            this.currentPlaylist = playlist; // Store for edit mode


            // Setze den Playlist-Titel oben im Modal
            if (this.elements.playlistTitle) {
                this.elements.playlistTitle.textContent = playlist.name;
            }
            this.elements.editPlaylistName.value = playlist.name;
            this.elements.editPlaylistDescription.value = playlist.description || '';
            this.elements.editPlaylistTags.value = playlist.tags ? playlist.tags.join(', ') : '';
            this.elements.editPlaylistPublic.checked = playlist.isPublic || false;

            // Zeige die echte Trackanzahl aus playlist.tracks, falls geladen
            const trackCount = Array.isArray(playlist.tracks) ? playlist.tracks.length : (playlist.trackCount || 0);
            this.elements.trackCountInfo.textContent = `${trackCount} Tracks`;
            this.elements.publicStatusInfo.textContent = playlist.isPublic ? '🌐 Public' : '🔒 Private';
            this.elements.createdInfo.textContent = `Created on ${playlist.createdAt}`;

            // Store playlist ID in modal
            this.elements.detailModal.dataset.playlistId = playlistId;

            // Direkt Edit-Mode aktivieren
            this.elements.playlistViewMode.style.display = 'none';
            this.elements.playlistEditMode.style.display = 'block';

            // Modal anzeigen
            this.showModal(this.elements.detailModal);
        } catch (error) {
            console.error('Error opening playlist detail:', error);
            toast.error('Failed to load playlist details');
        }
    }
    // (doppelter/fehlerhafter tagsDisplay-Block entfernt)

    /**
     * Show create playlist modal
     */
    showCreateModal() {
        this.showModal(this.elements.createModal);
    }

    /**
     * Show a modal
     * @param {HTMLElement} modal - Modal element
     */
    showModal(modal) {
        if (modal) {
            modal.style.display = 'block';
        }
    }

    /**
     * Close a modal
     * @param {HTMLElement} modal - Modal element
     */
    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Handle create playlist form submission
     * @param {Event} event - Form submit event
     */
    async handleCreatePlaylist(event) {
        event.preventDefault();
        
        const playlistData = {
            name: this.elements.playlistName.value.trim(),
            description: this.elements.playlistDescription.value.trim(),
            tags: this.elements.playlistTags.value.trim(),
            isPublic: this.elements.playlistPublic.checked
        };

        // Validate
        if (!playlistData.name) {
            toast.error('Please enter a playlist name');
            return;
        }
        
        try {
            const result = await this.service.createPlaylist(playlistData);
            
            if (result.success) {
                toast.success('Playlist created successfully!');
                this.closeModal(this.elements.createModal);
                this.elements.createPlaylistForm.reset();
                
                // Redirect to /app with the new playlist ID
                window.location.href = `/app?playlist=${result.playlist.id}`;
            } else {
                toast.error('Error creating playlist: ' + result.error);
            }
        } catch (error) {
            console.error('Error creating playlist:', error);
            toast.error('Failed to create playlist');
        }
    }

    /**
     * Toggle between view and edit mode
     * @param {boolean} editMode - True for edit mode, false for view mode
     */
    // toggleEditMode entfällt, da immer Edit-Mode aktiv ist
    
    /**
     * Navigate to /app page for editing tracks
     */
    handleEditTracks() {
        if (this.currentPlaylistId) {
            window.location.href = `/app?playlist=${this.currentPlaylistId}`;
        }
    }
    
    /**
     * Handle update playlist form submission
     * @param {Event} event - Form submit event
     */
    async handleUpdatePlaylist(event) {
        event.preventDefault();
        
        if (!this.currentPlaylistId) return;
        
        const playlistData = {
            name: this.elements.editPlaylistName.value.trim(),
            description: this.elements.editPlaylistDescription.value.trim(),
            tags: this.elements.editPlaylistTags.value.trim(),
            isPublic: this.elements.editPlaylistPublic.checked
        };

        // Validate
        if (!playlistData.name) {
            toast.error('Please enter a playlist name');
            return;
        }
        
        try {
            const result = await this.service.updatePlaylist(this.currentPlaylistId, playlistData);
            
            if (result.success) {
                toast.success('Playlist updated successfully!');
                // Reload playlist detail to show updated data
                await this.openPlaylistDetail(this.currentPlaylistId);
                await this.loadPlaylists(); // Refresh the grid
            } else {
                toast.error('Error updating playlist: ' + result.error);
            }
        } catch (error) {
            console.error('Error updating playlist:', error);
            toast.error('Failed to update playlist');
        }
    }

    /**
     * Handle delete playlist action
     */
    async handleDeletePlaylist() {
        if (!this.currentPlaylistId) return;
        
        // Use custom confirm dialog
        const confirmed = await customConfirm(
            'Do you really want to delete this playlist? This action cannot be undone.',
            'Delete Playlist'
        );
        
        if (!confirmed) {
            return;
        }

        try {
            const result = await this.service.deletePlaylist(this.currentPlaylistId);
            
            if (result.success) {
                toast.success('Playlist deleted successfully');
                this.closeModal(this.elements.detailModal);
                await this.loadPlaylists();
            } else {
                toast.error('Failed to delete playlist: ' + result.error);
            }
        } catch (error) {
            console.error('Error deleting playlist:', error);
            toast.error('Failed to delete playlist');
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @private
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the controller when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const playlistUI = new PlaylistUIController();
    playlistUI.init();
});