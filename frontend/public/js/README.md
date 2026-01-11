# Frontend JS Code Structure

## Overview

The frontend JavaScript code is organized for maintainability and scalability, with clear separation of concerns.

## Directory Structure

```
frontend/public/js/
├── config.js              # App configuration
├── notifications.js       # Toast notifications
├── playlist-ui.js         # Playlist UI controller
├── profile.js             # Profile management
├── search.js              # Track search
├── services/              # Business logic
│   └── playlist-service.js
└── utils/                 # Utility functions
     └── api-client.js      # HTTP client with auth
```

## Architecture

- **UI Layer**: Handles DOM and user events (e.g., playlist-ui.js)
- **Services Layer**: Business logic and API (e.g., services/playlist-service.js)
- **Utils Layer**: Utility functions and HTTP client (e.g., utils/api-client.js)

## File Descriptions

- `playlist-ui.js`: Controls playlist UI and user interactions
- `services/playlist-service.js`: Handles playlist API logic
- `utils/api-client.js`: Centralized HTTP client with token refresh and error handling
- `notifications.js`: Displays toast notifications
- `profile.js`: Manages user profile
- `search.js`: Track search logic
- `config.js`: App configuration

---
For more details, see the main frontend README.
- Cookie-based authentication
- Retry logic

**Usage:**
```javascript
// GET request
const data = await apiClient.get('/playlist/get/123');

// POST request
const result = await apiClient.post('/playlist/create', {
    name: 'My Playlist',
    is_public: false
});

// DELETE request
await apiClient.delete('/playlist/delete/123');
```

**Key Methods:**
- `get(endpoint, options)` - GET request
- `post(endpoint, body, options)` - POST request
- `put(endpoint, body, options)` - PUT request
- `delete(endpoint, options)` - DELETE request
- `request(endpoint, options)` - Generic request with auto-refresh

### Services

#### `services/playlist-service.js`
Handles all playlist-related business logic.

**Features:**
- CRUD operations for playlists
- Track management
- Playlist export
- Data transformation

**Usage:**
```javascript
// Get all playlists
const result = await playlistService.getPlaylists();

// Create a new playlist
const result = await playlistService.createPlaylist({
    name: 'Summer Mix',
    description: 'Best tracks for summer',
    tags: 'house, party',
    isPublic: true
});

// Delete a playlist
await playlistService.deletePlaylist(playlistId);
```

**Key Methods:**
- `getPlaylists()` - Fetch all playlists
- `getPlaylist(id)` - Fetch single playlist with tracks
- `createPlaylist(data)` - Create new playlist
- `updatePlaylist(id, data)` - Update existing playlist
- `deletePlaylist(id)` - Delete playlist
- `addTrack(playlistId, track)` - Add track to playlist
- `removeTrack(playlistId, trackId)` - Remove track from playlist
- `exportPlaylist(playlistId, format)` - Export playlist to file

### UI Controllers

#### `playlist-ui.js`
Manages all UI interactions for the playlist page.

**Features:**
- Modal management
- Form handling
- Event delegation
- XSS protection
- User feedback with toasts

**Key Methods:**
- `init()` - Initialize controller and event listeners
- `loadPlaylists()` - Fetch and display playlists
- `displayPlaylists(playlists)` - Render playlist grid
- `openPlaylistDetail(id)` - Show playlist detail modal
- `handleCreatePlaylist(event)` - Handle playlist creation
- `handleDeletePlaylist()` - Handle playlist deletion
- `handleRemoveTrack(trackId)` - Handle track removal

## Code Style

### Documentation

All functions include JSDoc comments with:
- Description
- Parameter types
- Return types
- Usage examples (where helpful)

Example:
```javascript
/**
 * Create a new playlist
 * @param {PlaylistCreateData} playlistData - The playlist data
 * @returns {Promise<{success: boolean, playlist?: Playlist, message?: string, error?: string}>}
 */
async createPlaylist(playlistData) {
    // Implementation
}
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `PlaylistService`)
- **Methods/Functions**: camelCase (e.g., `getPlaylists`)
- **Private Methods**: Prefixed with underscore (e.g., `_cacheElements`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_URL`)
- **DOM Elements**: Descriptive names (e.g., `createPlaylistBtn`)

### Error Handling

All async operations use try-catch blocks and return consistent error objects:

```javascript
try {
    const result = await service.doSomething();
    if (result.success) {
        // Handle success
    } else {
        // Handle error
        toast.error(result.error);
    }
} catch (error) {
    console.error('Operation failed:', error);
    toast.error('Operation failed');
}
```

## Migration Guide

### Old Code (Deprecated)
```javascript
// playlist.js - Old monolithic approach
const playlistService = new PlaylistService();

async function createPlaylist() {
    // Mixed concerns: API calls + DOM manipulation
}
```

### New Code
```javascript
// Services handle data
// services/playlist-service.js
class PlaylistService {
    async createPlaylist(data) {
        return await this.apiClient.post('/playlist/create', data);
    }
}

// UI controllers handle DOM
// playlist-ui.js
class PlaylistUIController {
    async handleCreatePlaylist(event) {
        const result = await this.service.createPlaylist(data);
        if (result.success) {
            this.displaySuccess();
        }
    }
}
```

## Testing Considerations

The new structure makes testing easier:

1. **Unit Testing Services**: Test business logic without DOM
2. **Integration Testing**: Test API client independently
3. **UI Testing**: Mock services for UI controller tests

## Future Improvements

- [ ] Add TypeScript for type safety
- [ ] Implement service worker for offline support
- [ ] Add state management (Redux/MobX)
- [ ] Create reusable UI components
- [ ] Add unit tests
- [ ] Bundle and minify for production

## Best Practices

1. **Keep layers separate**: Don't mix service logic with UI logic
2. **Use the API client**: Don't use fetch() directly
3. **Handle errors**: Always catch and display user-friendly messages
4. **Escape user input**: Use `_escapeHtml()` for XSS prevention
5. **Document your code**: Add JSDoc comments for all public methods
6. **Use toast notifications**: Provide feedback for all user actions

## Contributing

When adding new features:

1. Add API calls to the appropriate service
2. Create/update UI controller for DOM interactions
3. Add JSDoc documentation
4. Follow naming conventions
5. Handle errors consistently
6. Test in browser before committing

## Support

For questions or issues, please refer to the main project README or contact the development team.
