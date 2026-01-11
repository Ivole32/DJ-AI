// Playlist Management - Backend Integration
class PlaylistService {
    constructor() {
        this.API_URL = AppConfig.getApiUrl('');
        this.PLAYLISTS_KEY = 'dj_ai_playlists';
    }

    /**
     * Fetch all playlists for the current user from the backend.
     * Calls the real backend API.
     */
    async getPlaylists() {
        try {
            console.log('Fetching playlists...');
            const response = await fetchWithTokenRefresh(`${this.API_URL}/playlist/list`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch playlists' }));
                throw new Error(formatApiError(errorData));
            }
            const result = await response.json();
            return { success: true, playlists: result.playlists };
        } catch (error) {
            console.error('Error fetching playlists:', error);
            return { success: false, error: error.message };
        }
    }

    // Get playlist by ID
    async getPlaylist(playlistId) {
        try {
            console.log('Fetching playlist:', playlistId);
            const response = await fetchWithTokenRefresh(`${this.API_URL}/playlist/get/${playlistId}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch playlist' }));
                throw new Error(formatApiError(errorData));
            }
            const playlist = await response.json();
            return { success: true, playlist };
        } catch (error) {
            console.error('Error fetching playlist:', error);
            return { success: false, error: error.message };
        }
    }

    // Create playlist
    async createPlaylist(playlistData) {
        try {
            console.log('Creating playlist:', playlistData);
            
            // Call backend API
            const response = await fetchWithTokenRefresh(
                `${this.API_URL}/playlist/create`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        name: playlistData.name,
                        is_public: playlistData.isPublic || false
                    })
                }
            );

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to create playlist' }));
                throw new Error(formatApiError(errorData));
            }

            const result = await response.json();
            console.log('Playlist created:', result);
            
            // Create local representation of the new playlist
            const newPlaylist = {
                id: result.playlist_id,
                name: playlistData.name,
                description: playlistData.description || '',
                tags: playlistData.tags ? playlistData.tags.split(',').map(t => t.trim()) : [],
                isPublic: playlistData.isPublic || false,
                trackCount: 0,
                createdAt: new Date().toISOString().split('T')[0],
                updatedAt: new Date().toISOString().split('T')[0],
                coverImage: 'https://via.placeholder.com/300',
                tracks: []
            };
            
            return { success: true, playlist: newPlaylist, message: result.message };
        } catch (error) {
            console.error('Error creating playlist:', error);
            return { success: false, error: error.message };
        }
    }

    // Update playlist
    async updatePlaylist(playlistId, playlistData) {
        try {
            console.log('Updating playlist:', playlistId, playlistData);
            await this.delay(800);
            
            const result = await this.getPlaylists();
            const playlists = result.playlists;
            const index = playlists.findIndex(p => p.id === playlistId);
            
            if (index !== -1) {
                playlists[index] = { ...playlists[index], ...playlistData, updatedAt: new Date().toISOString().split('T')[0] };
                localStorage.setItem(this.PLAYLISTS_KEY, JSON.stringify(playlists));
                return { success: true, playlist: playlists[index] };
            }
            
            return { success: false, error: 'Playlist not found' };
        } catch (error) {
            console.error('Error updating playlist:', error);
            return { success: false, error: error.message };
        }
    }

    // Delete playlist
    async deletePlaylist(playlistId) {
        try {
            console.log('Deleting playlist:', playlistId);
            await this.delay(500);
            
            const result = await this.getPlaylists();
            const playlists = result.playlists.filter(p => p.id !== playlistId);
            localStorage.setItem(this.PLAYLISTS_KEY, JSON.stringify(playlists));
            
            return { success: true };
        } catch (error) {
            console.error('Error deleting playlist:', error);
            return { success: false, error: error.message };
        }
    }

    // Add track to playlist
    async addTrack(playlistId, track) {
        try {
            console.log('Adding track to playlist:', playlistId, track);
            await this.delay(500);
            
            return { success: true, message: 'Track added successfully' };
        } catch (error) {
            console.error('Error adding track:', error);
            return { success: false, error: error.message };
        }
    }

    // Remove track from playlist
    async removeTrack(playlistId, trackId) {
        try {
            console.log('Removing track from playlist:', playlistId, trackId);
            await this.delay(500);
            
            return { success: true };
        } catch (error) {
            console.error('Error removing track:', error);
            return { success: false, error: error.message };
        }
    }

    // Export playlist
    async exportPlaylist(playlistId, format = 'json') {
        try {
            console.log('Exporting playlist:', playlistId, format);
            await this.delay(800);
            
            const result = await this.getPlaylist(playlistId);
            if (result.success) {
                const dataStr = JSON.stringify(result.playlist, null, 2);
                const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
                
                const exportFileDefaultName = `playlist_${playlistId}_${Date.now()}.json`;
                
                const linkElement = document.createElement('a');
                linkElement.setAttribute('href', dataUri);
                linkElement.setAttribute('download', exportFileDefaultName);
                linkElement.click();
                
                return { success: true };
            }
            
            return { success: false, error: 'Playlist not found' };
        } catch (error) {
            console.error('Error exporting playlist:', error);
            return { success: false, error: error.message };
        }
    }
}

// Initialize playlist service
const playlistService = new PlaylistService();

// Load playlists
async function loadPlaylists() {
    const result = await playlistService.getPlaylists();
    
    if (result.success) {
        displayPlaylists(result.playlists);
    } else {
        console.error('Error loading playlists:', result.error);
    }
}

// Display playlists
function displayPlaylists(playlists) {
    const grid = document.getElementById('playlistsGrid');
    grid.innerHTML = '';
    
    playlists.forEach(playlist => {
        const card = document.createElement('div');
        card.className = 'playlist-card';
        card.innerHTML = `
            <img src="${playlist.coverImage}" alt="${playlist.name}">
            <div class="playlist-info">
                <h3>${playlist.name}</h3>
                <p>${playlist.description}</p>
                <div class="playlist-meta">
                    <span>${playlist.trackCount} Tracks</span>
                    <span>${playlist.isPublic ? '🌐 Public' : '🔒 Private'}</span>
                </div>
                <div class="playlist-tags">
                    ${playlist.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => openPlaylistDetail(playlist.id));
        grid.appendChild(card);
    });
}

// Open playlist detail modal
async function openPlaylistDetail(playlistId) {
    const result = await playlistService.getPlaylist(playlistId);
    
    if (result.success) {
        const playlist = result.playlist;
        
        document.getElementById('playlistTitle').textContent = playlist.name;
        document.getElementById('playlistDescription').textContent = playlist.description;
        document.getElementById('trackCountInfo').textContent = `${playlist.trackCount} Tracks`;
        document.getElementById('createdInfo').textContent = `Created on ${playlist.createdAt}`;
        
        // Display tracks (normalize each track for consistent fields)
        const trackList = document.getElementById('trackList');
        trackList.innerHTML = '';
        // Hole normalizeTrack aus globalem Scope (search.js muss vorher geladen sein!)
        playlist.tracks.forEach((track, index) => {
            const norm = typeof normalizeTrack === 'function' ? normalizeTrack(track) : track;
            const trackElement = document.createElement('div');
            trackElement.className = 'track-item';
            trackElement.innerHTML = `
                <span class="track-number">${index + 1}</span>
                <div class="track-info">
                    <div class="track-title">${norm.title}</div>
                    <div class="track-artist">${norm.artist}</div>
                </div>
                <span class="track-bpm">${norm.bpm ? norm.bpm + ' BPM' : ''}</span>
                <span class="track-key">${norm.key || ''}</span>
                <span class="track-camelot">${norm.camelot || ''}</span>
                <button class="btn-icon btn-remove" onclick="removeTrack(${playlist.id}, ${norm.id})">×</button>
            `;
            trackList.appendChild(trackElement);
        });
        
        // Store current playlist ID for actions
        document.getElementById('playlistDetailModal').dataset.playlistId = playlistId;
        
        // Show modal
        document.getElementById('playlistDetailModal').style.display = 'block';
    }
}

// Remove track from playlist
async function removeTrack(playlistId, trackId) {
    if (confirm('Remove track from playlist?')) {
        const result = await playlistService.removeTrack(playlistId, trackId);
        if (result.success) {
            openPlaylistDetail(playlistId); // Reload
        }
    }
}

// Modal handlers
const createModal = document.getElementById('createPlaylistModal');
const detailModal = document.getElementById('playlistDetailModal');

document.getElementById('createPlaylistBtn').addEventListener('click', () => {
    createModal.style.display = 'block';
});

// Close modals
document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.addEventListener('click', function() {
        this.closest('.modal').style.display = 'none';
    });
});

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// Create playlist form
document.getElementById('createPlaylistForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const playlistData = {
        name: document.getElementById('playlistName').value,
        description: document.getElementById('playlistDescription').value,
        tags: document.getElementById('playlistTags').value,
        isPublic: document.getElementById('playlistPublic').checked
    };
    
    const result = await playlistService.createPlaylist(playlistData);
    
    if (result.success) {
        alert('Playlist created successfully!');
        createModal.style.display = 'none';
        e.target.reset();
        loadPlaylists(); // Reload playlists
    } else {
        alert('Error creating playlist: ' + result.error);
    }
});

// Playlist actions
document.getElementById('deletePlaylistBtn')?.addEventListener('click', async () => {
    const playlistId = parseInt(detailModal.dataset.playlistId);
    
    if (confirm('Are you sure you want to delete this playlist?')) {
        const result = await playlistService.deletePlaylist(playlistId);
        if (result.success) {
            detailModal.style.display = 'none';
            loadPlaylists();
        }
    }
});

document.getElementById('sharePlaylistBtn')?.addEventListener('click', () => {
    alert('Share functionality would be implemented here.');
});

document.getElementById('exportPlaylistBtn')?.addEventListener('click', async () => {
    const playlistId = parseInt(detailModal.dataset.playlistId);
    await playlistService.exportPlaylist(playlistId);
});

document.getElementById('playPlaylistBtn')?.addEventListener('click', () => {
    alert('Play functionality would be implemented here.');
});

document.getElementById('shufflePlaylistBtn')?.addEventListener('click', () => {
    alert('Shuffle functionality would be implemented here.');
});

// Load playlists on page load
loadPlaylists();