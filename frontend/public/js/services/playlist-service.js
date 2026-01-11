/**
 * Playlist Service
 * Handles all playlist-related API operations
 * @module services/playlist-service
 */

/**
 * @typedef {Object} Playlist
 * @property {string|number} id - Playlist ID
 * @property {string} name - Playlist name
 * @property {string} description - Playlist description
 * @property {string[]} tags - Playlist tags
 * @property {boolean} isPublic - Whether the playlist is public
 * @property {number} trackCount - Number of tracks in playlist
 * @property {string} createdAt - Creation date (ISO format)
 * @property {string} updatedAt - Last update date (ISO format)
 * @property {string} coverImage - Cover image URL
 * @property {Track[]} [tracks] - Array of tracks in playlist
 */

/**
 * @typedef {Object} Track
 * @property {string|number} id - Track ID
 * @property {string} title - Track title
 * @property {string} artist - Track artist
 * @property {number} bpm - Beats per minute
 * @property {string} key - Musical key
 * @property {string} genre - Music genre
 * @property {number} energy - Energy level (0-1)
 */

/**
 * @typedef {Object} PlaylistCreateData
 * @property {string} name - Playlist name
 * @property {string} [description] - Playlist description
 * @property {string} [tags] - Comma-separated tags
 * @property {boolean} [isPublic] - Whether the playlist should be public
 */

/**
 * Playlist Service Class
 * Manages all playlist-related operations including CRUD operations
 */
class PlaylistService {
    /**
     * Create a new Playlist Service
     */
    constructor() {
        this.apiClient = apiClient;
    }

    /**
     * Get all playlists for the current user
     * @returns {Promise<{success: boolean, playlists?: Playlist[], error?: string}>}
     */
    async getPlaylists() {
        try {
            console.log('Fetching playlists...');
            // Call backend API to get user's playlists
            const result = await this.apiClient.get('/playlist/list');
            // Transform backend data to frontend format
            const playlists = result.playlists.map(p => ({
                id: p.playlist_id,
                name: p.name,
                description: p.description || '',
                tags: p.tags || [],
                isPublic: p.public || false,
                trackCount: p.tracks_count || 0,
                createdAt: p.created_at,
                updatedAt: p.created_at,
                coverImage: `https://picsum.photos/seed/${p.playlist_id}/300/300`
            }));
            return { success: true, playlists };
        } catch (error) {
            console.error('Error fetching playlists:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get a specific playlist by ID
     * @param {string|number} playlistId - The playlist ID
     * @returns {Promise<{success: boolean, playlist?: Playlist, error?: string}>}
     */
    async getPlaylist(playlistId) {
        try {
            console.log('Fetching playlist:', playlistId);
            // Fetch playlist base data
            const playlistResult = await this.apiClient.get(`/playlist/get/${playlistId}`);
            if (!playlistResult.playlist) {
                return { success: false, error: 'Playlist not found' };
            }
            const playlist = {
                id: playlistResult.playlist.playlist_id,
                name: playlistResult.playlist.name,
                description: playlistResult.playlist.description || '',
                tags: playlistResult.playlist.tags || [],
                isPublic: playlistResult.playlist.public || false,
                trackCount: playlistResult.playlist.tracks_count || 0,
                createdAt: playlistResult.playlist.created_at,
                updatedAt: playlistResult.playlist.created_at,
                coverImage: `https://picsum.photos/seed/${playlistResult.playlist.playlist_id}/300/300`,
                tracks: []
            };
            // Fetch tracks for the playlist
            const tracksResult = await this.apiClient.get(`/playlist/get-tracks/${playlistId}`);
            playlist.tracks = Array.isArray(tracksResult.tracks) ? tracksResult.tracks : [];
            return { success: true, playlist };
        } catch (error) {
            console.error('Error fetching playlist:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Create a new playlist
     * @param {PlaylistCreateData} playlistData - The playlist data
     * @returns {Promise<{success: boolean, playlist?: Playlist, message?: string, error?: string}>}
     */
    async createPlaylist(playlistData) {
        try {
            console.log('Creating playlist:', playlistData);
            
            // Parse tags if they're a comma-separated string
            const tags = typeof playlistData.tags === 'string' 
                ? playlistData.tags.split(',').map(t => t.trim()).filter(t => t.length > 0)
                : (playlistData.tags || []);
            
            // Call backend API
            const result = await this.apiClient.post('/playlist/create', {
                name: playlistData.name,
                description: playlistData.description || '',
                tags: tags.length > 0 ? tags : null,
                is_public: playlistData.isPublic || false
            });
            
            console.log('Playlist created:', result);
            
            // Create local representation of the new playlist
            const newPlaylist = {
                id: result.playlist_id,
                name: playlistData.name,
                description: playlistData.description || '',
                tags: tags,
                isPublic: playlistData.isPublic || false,
                trackCount: 0,
                createdAt: new Date().toISOString().split('T')[0],
                updatedAt: new Date().toISOString().split('T')[0],
                coverImage: `https://picsum.photos/seed/${result.playlist_id}/300/300`,
                tracks: []
            };
            
            return { 
                success: true, 
                playlist: newPlaylist, 
                message: result.message 
            };
        } catch (error) {
            console.error('Error creating playlist:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Update an existing playlist
     * @param {string|number} playlistId - The playlist ID
     * @param {Partial<PlaylistCreateData>} playlistData - Updated playlist data
     * @returns {Promise<{success: boolean, playlist?: Playlist, error?: string}>}
     */
    async updatePlaylist(playlistId, playlistData) {
        try {
            console.log('Updating playlist:', playlistId, playlistData);
            
            // Parse tags if they're a comma-separated string
            const tags = typeof playlistData.tags === 'string' 
                ? playlistData.tags.split(',').map(t => t.trim()).filter(t => t.length > 0)
                : (playlistData.tags || null);
            
            // Call backend API
            const result = await this.apiClient.put(`/playlist/update/${playlistId}`, {
                name: playlistData.name,
                description: playlistData.description,
                tags: tags,
                is_public: playlistData.isPublic
            });
            
            return { 
                success: true, 
                playlist: { id: playlistId, ...playlistData } 
            };
        } catch (error) {
            console.error('Error updating playlist:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Delete a playlist
     * @param {string|number} playlistId - The playlist ID
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    async deletePlaylist(playlistId) {
        try {
            console.log('Deleting playlist:', playlistId);
            
            // Call backend API to delete playlist
            await this.apiClient.delete(`/playlist/delete/${playlistId}`);
            
            return { success: true };
        } catch (error) {
            console.error('Error deleting playlist:', error);
            return { success: false, error: error.message };
        }
    }


    /**
     * Export a playlist to a file
     * @param {string|number} playlistId - The playlist ID
     * @param {string} [format='json'] - Export format (currently only 'json')
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    async exportPlaylist(playlistId, format = 'json') {
        try {
            console.log('Exporting playlist:', playlistId, format);
            
            const result = await this.getPlaylist(playlistId);
            if (!result.success) {
                return { success: false, error: 'Playlist not found' };
            }
            
            // Create downloadable file
            const dataStr = JSON.stringify(result.playlist, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
            const exportFileName = `playlist_${playlistId}_${Date.now()}.json`;
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileName);
            linkElement.click();
            
            return { success: true };
        } catch (error) {
            console.error('Error exporting playlist:', error);
            return { success: false, error: error.message };
        }
    }
}

// Create and export singleton instance
const playlistService = new PlaylistService();