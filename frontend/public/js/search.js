// Global AbortController for ML-Suggestions
let suggestionsAbortController = null;
// Backend URL configuration; adjust per environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8080'  // local development
  : '';  // production (same origin)

let searchTimeout;
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const loadingIndicator = document.getElementById('loadingIndicator');
const playlistDiv = document.getElementById('playlist');
const playlistCountSpan = document.getElementById('playlistCount');
const clearPlaylistBtn = document.getElementById('clearPlaylist');
const suggestionsStatus = document.getElementById('suggestionsStatus');
const suggestionsList = document.getElementById('suggestionsList');
let dragImageEl = null;
let currentDropIndex = null;

// Playlist state
let playlist = []; // Only for the right playlist UI (current working playlist)
let currentPlaylist = []; // Holds the actual playlist tracks (right side)
let currentPlaylistId = null; // Track currently loaded playlist
let currentPlaylistName = null; // Name of the loaded playlist

const playlistStatusBar = document.getElementById('playlistStatusBar');

function updatePlaylistStatusBar() {
  if (currentPlaylistId && currentPlaylistName) {
    playlistStatusBar.innerHTML = `<div class="bg-green-50 border border-green-200 text-green-800 rounded px-3 py-2 text-sm flex items-center gap-2">
      <svg class='w-4 h-4 text-green-500' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-width='2' d='M5 13l4 4L19 7'></path></svg>
      Editing playlist: <span class='font-semibold'>${escapeHtml(currentPlaylistName)}</span>
    </div>`;
  } else {
    playlistStatusBar.innerHTML = `<div class="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded px-3 py-2 text-sm flex items-center gap-2">
      <svg class='w-4 h-4 text-yellow-500' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-width='2' d='M13 16h-1v-4h-1m1-4h.01'></path></svg>
      <span class='font-semibold'>No playlist loaded.</span> Changes will NOT be saved!
    </div>`;
  }
}

// Initialize
// Clear All Button entfernt
document.addEventListener('dragend', cleanupDragImage);

// Check if playlist parameter is provided in URL
window.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const playlistId = urlParams.get('playlist');
  
  if (playlistId) {
    loadPlaylistFromId(playlistId);
  } else {
    updatePlaylistStatusBar();
  }
});

// Load playlist from backend by ID
async function loadPlaylistFromId(playlistId) {
  try {
    // Fetch playlist details
    const playlistResponse = await fetchWithTokenRefresh(`${API_BASE_URL}/api/v1/playlist/get/${playlistId}`);
    if (!playlistResponse.ok) {
      throw new Error('Failed to load playlist');
    }
    const playlistData = await playlistResponse.json();
    currentPlaylistName = playlistData.playlist.name || null;
    // Fetch playlist tracks
    const tracksResponse = await fetchWithTokenRefresh(`${API_BASE_URL}/api/v1/playlist/get-tracks/${playlistId}`);
    if (!tracksResponse.ok) {
      throw new Error('Failed to load playlist tracks');
    }
    const tracksData = await tracksResponse.json();
    
    // Set current playlist ID
    currentPlaylistId = playlistId;
    
    // Load tracks into currentPlaylist (right playlist UI)
    currentPlaylist = tracksData.tracks.map(track => ({
      id: track.youtube_track_id,
      playlist_track_id: track.playlist_track_id,
      sort_key: track.sort_key,
      title: track.title || 'Unknown Title',
      artist: track.artist || 'Unknown Artist',
      bpm: track.bpm || null,
      key: track.key || null,
      camelot: track.camelot || null,
      energy: track.energy || null
    }));
    playlist = currentPlaylist;
    updatePlaylistDisplay(false);
    updatePlaylistStatusBar();
    updateSuggestions();
    toast.success(`Loaded playlist: ${playlistData.playlist.name}`);
  } catch (error) {
    console.error('Error loading playlist:', error);
    toast.error('Failed to load playlist');
  }
}


// Enable drop on playlist area
playlistDiv.addEventListener('dragover', (e) => {
  e.preventDefault();
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
  playlistDiv.classList.add('playlist-drop-active');
  const idx = computeDropIndex(e);
  if (idx !== currentDropIndex) {
    currentDropIndex = idx;
    updatePlaylistDisplay(true);
  }
});
playlistDiv.addEventListener('dragenter', (e) => {
  e.preventDefault();
  playlistDiv.classList.add('playlist-drop-active');
});
playlistDiv.addEventListener('drop', (e) => {
  e.preventDefault();
  if (!e.dataTransfer) return;
  const data = e.dataTransfer.getData('application/json') || e.dataTransfer.getData('text/plain');
  if (!data) return;
  try {
    const payload = JSON.parse(data);
    const track = normalizeTrack(payload);
    const dropIndex = currentDropIndex ?? playlist.length;
    addToPlaylistAt(track, dropIndex);
  } catch (_) {
    /* ignore bad payload */
  }
  playlistDiv.classList.remove('playlist-drop-active');
  updatePlaylistDisplay(false);
  currentDropIndex = null;
});
playlistDiv.addEventListener('dragleave', () => {
  playlistDiv.classList.remove('playlist-drop-active');
  currentDropIndex = null;
  updatePlaylistDisplay(false);
});

searchInput.addEventListener('input', (e) => {
  const query = e.target.value.trim();
  
  // Clear previous debounce
  clearTimeout(searchTimeout);
  
  // Clear results if input is empty
  if (!query) {
    resultsDiv.innerHTML = '';
    return;
  }

  // Only search if query has at least 3 characters
  if (query.length < 3) {
    resultsDiv.innerHTML = `
      <div class="p-4 bg-gray-50 text-gray-600 rounded-lg text-center text-sm border border-gray-200">
        Please enter at least 3 characters
      </div>
    `;
    return;
  }

  // Show loading indicator
  loadingIndicator.classList.remove('hidden');
  
  // Debounce: wait 300ms after typing stops
  searchTimeout = setTimeout(async () => {
    try {
      const response = await fetchWithTokenRefresh(`${API_BASE_URL}/api/v1/search/track?query=${encodeURIComponent(query)}&top=10`);
      
      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      const data = await response.json();
      displayResults(data.results);
    } catch (error) {
      resultsDiv.innerHTML = `
        <div class="p-4 bg-gray-50 text-gray-700 rounded-lg border border-gray-300">
          Error: ${error.message}
        </div>
      `;
    } finally {
      loadingIndicator.classList.add('hidden');
    }
  }, 300);
});

function displayResults(results) {
  if (!results || results.length === 0) {
    resultsDiv.innerHTML = `
      <div class="p-4 bg-gray-50 text-gray-600 rounded-lg text-center text-sm sm:text-base border border-gray-200">
        No results found
      </div>
    `;
    return;
  }

  resultsDiv.innerHTML = results.map(track => {
    const safeTrack = normalizeTrack(track);
    const payload = encodeURIComponent(JSON.stringify(safeTrack));
    // YouTube link button (arrow icon)
    // Try both youtube_id and id fields for YouTube video ID
    const ytId = safeTrack.youtube_id || safeTrack.id;
    const ytUrl = ytId ? `https://www.youtube.com/watch?v=${ytId}` : null;
    const ytButton = ytUrl ? `
      <a href="${ytUrl}" target="_blank" rel="noopener noreferrer" title="Open on YouTube" class="ml-2 inline-flex items-center justify-center w-8 h-8 rounded hover:bg-gray-200 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 text-gray-500">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
      </a>
    ` : '';
    return `
      <div class="bg-white p-4 sm:p-5 border border-gray-200 rounded-md hover:border-gray-300 transition-colors cursor-pointer"
           onclick='addToPlaylist(JSON.parse(decodeURIComponent("${payload}")))'
           draggable="true"
           ondragstart='onDragStart(event, decodeURIComponent("${payload}"))'>
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-base sm:text-lg text-gray-900 truncate flex items-center">
              ${escapeHtml(safeTrack.title)}
              ${ytButton}
            </h3>
            <p class="text-sm sm:text-base text-gray-600 truncate">${escapeHtml(safeTrack.artist)}</p>
            <div class="flex flex-wrap gap-2 mt-2">
              ${safeTrack.bpm ? `<span class="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded">${Math.round(safeTrack.bpm)} BPM</span>` : ''}
              ${safeTrack.key ? `<span class="text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded">${escapeHtml(safeTrack.key)}</span>` : ''}
              <span class="text-xs px-2 py-1 bg-green-50 text-green-700 rounded">${escapeHtml(safeTrack.camelot)}</span>
              ${safeTrack.energy ? `<span class="text-xs px-2 py-1 bg-orange-50 text-orange-700 rounded">Energy: ${(safeTrack.energy * 100).toFixed(0)}%</span>` : ''}
            </div>
            <p class="text-xs sm:text-sm text-gray-500 mt-1">ID: ${escapeHtml(safeTrack.id)}</p>
          </div>
          <div class="flex-shrink-0 self-start">
            <span class="inline-block px-3 py-1.5 sm:px-4 sm:py-2 bg-gray-100 text-gray-800 rounded-md text-sm sm:text-base font-medium">
              ${(safeTrack.score).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function addToPlaylist(track) {
  addToPlaylistAt(track, playlist.length);
}

/**
 * Add a track to the playlist at a specific index position.
 * Handles duplicate detection and repositioning logic.
 * 
 * @param {Object} track - Track object to add (will be normalized)
 * @param {number} index - Target position (0-based) in playlist
 * 
 * Behavior:
 * - If track already exists at target index: no-op
 * - If track exists elsewhere: removes from old position, inserts at new
 * - If track is new: inserts at specified index
 * - Syncs with backend if a playlist is currently loaded
 */
function addToPlaylistAt(track, index) {
  // Check if track is already in playlist
  const normalized = normalizeTrack(track);
  // Only operate on currentPlaylist (not search/ML results)
  let arr = currentPlaylist;
  const existingIndex = arr.findIndex(t => t.id === normalized.id);
  if (existingIndex !== -1) {
    if (existingIndex === index) return;
    // Track existiert, verschiebe: Lösche und füge neu ein
    const trackToMove = arr[existingIndex];
    arr.splice(existingIndex, 1);
    const safeIndex = Math.max(0, Math.min(index ?? arr.length, arr.length));
    arr.splice(safeIndex, 0, normalized);
    playlist = arr;
    updatePlaylistDisplay(false);
    updateSuggestions();
    showToast('Track moved in playlist');
    if (currentPlaylistId && trackToMove.playlist_track_id) {
      // Backend: Track löschen und neu einfügen
      syncRemoveTrack(trackToMove.playlist_track_id).then(() => {
        syncAddTrack(normalized.id, safeIndex);
      });
    }
    return;
  }
  // Track ist neu, wie gehabt hinzufügen
  const safeIndex = Math.max(0, Math.min(index ?? arr.length, arr.length));
  arr.splice(safeIndex, 0, normalized);
  playlist = arr;
  updatePlaylistDisplay(false);
  updateSuggestions();
  showToast('Track added to playlist');
  if (currentPlaylistId) {
    syncAddTrack(normalized.id, safeIndex);
  }
}

/**
 * Synchronize track addition to backend using fractional indexing.
 * Calculates the correct insertion position and calls the backend API.
 * 
 * @param {string} youtubeId - YouTube video ID of the track to add
 * @param {number} index - Position in the playlist where track should be inserted
 * 
 * Position Types:
 * - 'start': index === 0 (prepend to playlist)
 * - 'end': index >= playlist.length - 1 (append to playlist)
 * - 'between': insert between two tracks (requires prev_sort and next_sort)
 * 
 * The backend uses fractional indexing to maintain order without renumbering.
 * After successful insertion, reloads the playlist to get updated sort_keys.
 */
async function syncAddTrack(youtubeId, index) {
  try {
    let position, prev_sort, next_sort;
    
    // Determine position type
    if (index === 0) {
      // Add to start
      position = 'start';
    } else if (index >= playlist.length - 1) {
      // Add to end
      position = 'end';
    } else {
      // Add between two tracks
      position = 'between';
      prev_sort = playlist[index - 1].sort_key;
      next_sort = playlist[index + 1].sort_key;
    }
    
    const requestBody = { position };
    if (position === 'between') {
      requestBody.prev_sort = prev_sort;
      requestBody.next_sort = next_sort;
    }
    
    const response = await fetchWithTokenRefresh(
      `${API_BASE_URL}/api/v1/playlist/add-track/${currentPlaylistId}/${youtubeId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to sync track addition');
    }
    
    // Reload playlist to get updated sort_keys and metadata from backend
    await reloadPlaylistTracks();
  } catch (error) {
    console.error('Error syncing track addition:', error);
    toast.error('Failed to save track to playlist');
  }
}

// Reload playlist tracks from backend
/**
 * Reload all tracks from backend after modification.
 * Ensures frontend playlist state matches backend database.
 * Updates sort_keys and playlist_track_ids from server.
 * 
 * Called after:
 * - Adding a track (to get new sort_key and playlist_track_id)
 * - Reordering tracks (to get updated sort_keys after rebalancing)
 * 
 * @returns {Promise<void>}
 */
async function reloadPlaylistTracks() {
  if (!currentPlaylistId) return;
  
  try {
    const tracksResponse = await fetchWithTokenRefresh(`${API_BASE_URL}/api/v1/playlist/get-tracks/${currentPlaylistId}`);
    if (!tracksResponse.ok) {
      throw new Error('Failed to reload playlist tracks');
    }
    const tracksData = await tracksResponse.json();
    
    // Update playlist with new sort_keys and playlist_track_ids
    playlist = tracksData.tracks.map(track => ({
      id: track.youtube_track_id,
      playlist_track_id: track.playlist_track_id,
      sort_key: track.sort_key,
      title: track.title || 'Unknown Title',
      artist: track.artist || 'Unknown Artist',
      bpm: track.bpm || 0,
      key: track.key || 'Unknown',
      camelot: track.camelot || null,
      energy: track.energy || 0
    }));
    
    updatePlaylistDisplay(false);
  } catch (error) {
    console.error('Error reloading playlist tracks:', error);
  }
}

function removeFromPlaylist(trackId) {
  const trackToRemove = currentPlaylist.find(t => t.id === trackId);
  currentPlaylist = currentPlaylist.filter(t => t.id !== trackId);
  playlist = currentPlaylist;
  updatePlaylistDisplay();
  updateSuggestions();
  if (currentPlaylistId && trackToRemove && trackToRemove.playlist_track_id) {
    syncRemoveTrack(trackToRemove.playlist_track_id);
  }
}

// Sync track removal with backend
async function syncRemoveTrack(playlistTrackId) {
  try {
    const response = await fetchWithTokenRefresh(
      `${API_BASE_URL}/api/v1/playlist/remove-track/${currentPlaylistId}/${playlistTrackId}`,
      { method: 'DELETE' }
    );
    
    if (!response.ok) {
      throw new Error('Failed to sync track removal');
    }
  } catch (error) {
    console.error('Error syncing track removal:', error);
    toast.error('Failed to remove track from playlist');
  }
}

function clearPlaylist() {
  if (currentPlaylist.length === 0) return;
  if (confirm('Clear the playlist?')) {
    currentPlaylist = [];
    playlist = [];
    currentPlaylistId = null;
    currentPlaylistName = null;
    updatePlaylistDisplay();
    updatePlaylistStatusBar();
    updateSuggestions();
  }
}

function updatePlaylistDisplay(showPlaceholder = false) {
  playlistCountSpan.textContent = playlist.length;
  
  if (playlist.length === 0) {
    playlistDiv.innerHTML = `
      <div class="text-center text-gray-400 py-8 text-sm">
        Click tracks to add them to the playlist
      </div>
    `;
    return;
  }
  
  const parts = [];

  const placeholder = `
    <div class="drop-slot"></div>
  `;

  playlist.forEach((track, index) => {
    if (showPlaceholder && currentDropIndex === index) {
      parts.push(placeholder);
    }
    const payload = encodeURIComponent(JSON.stringify({ ...track, source: 'playlist', index }));
    parts.push(`
    <div class="bg-white p-3 rounded-md border border-gray-200 flex items-start justify-between gap-2 hover:bg-gray-50 transition-colors"
         draggable="true"
         data-index="${index}"
         ondragstart='onDragStart(event, decodeURIComponent("${payload}"), ${index})'>
      <div class="flex items-start gap-3 flex-1 min-w-0">
        <span class="drag-handle text-gray-400 hover:text-gray-600" title="Drag to reorder">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-width="2" d="M10 6h8M10 12h8M10 18h8"></path>
          </svg>
        </span>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs font-medium text-gray-500">${index + 1}.</span>
            <h4 class="font-medium text-sm text-gray-900 truncate">${escapeHtml(track.title)}</h4>
            <a href="https://www.youtube.com/watch?v=${track.id}" target="_blank" rel="noopener noreferrer" title="Open on YouTube" class="ml-2 inline-flex items-center justify-center w-8 h-8 rounded hover:bg-gray-200 focus:outline-none">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 text-gray-500">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </a>
          </div>
          <p class="text-xs text-gray-600 truncate">${escapeHtml(track.artist)}</p>
          <div class="flex flex-wrap gap-1 mt-1">
            ${track.bpm ? `<span class="text-xs px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded">${Math.round(track.bpm)} BPM</span>` : ''}
            ${track.key ? `<span class="text-xs px-1.5 py-0.5 bg-purple-50 text-purple-700 rounded">${escapeHtml(track.key)}</span>` : ''}
            <span class="text-xs px-1.5 py-0.5 bg-green-50 text-green-700 rounded">${escapeHtml(track.camelot)}</span>
            ${track.energy ? `<span class="text-xs px-1.5 py-0.5 bg-orange-50 text-orange-700 rounded">${(track.energy * 100).toFixed(0)}%</span>` : ''}
          </div>
        </div>
      </div>
      <button 
        onclick="removeFromPlaylist('${escapeHtml(track.id)}')"
        class="flex-shrink-0 text-gray-400 hover:text-red-600 transition p-1"
        title="Remove"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>
    `);
  });

  if (showPlaceholder && currentDropIndex === playlist.length) {
    parts.push(placeholder);
  }

  playlistDiv.innerHTML = parts.join('');
}

async function updateSuggestions() {
  if (!suggestionsStatus || !suggestionsList) return;

  if (playlist.length === 0) {
    suggestionsStatus.textContent = 'Add tracks to the playlist first.';
    suggestionsList.innerHTML = '';
    return;
  }

  const lastTrackId = playlist[playlist.length - 1].id;
  suggestionsStatus.textContent = 'Loading suggestions...';
  suggestionsList.innerHTML = '';

  // Cancel the previous suggestion request.
  if (suggestionsAbortController) {
    suggestionsAbortController.abort();
  }
  suggestionsAbortController = new AbortController();
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/prediction/next_track?track_id=${encodeURIComponent(lastTrackId)}&top_k=5`, {
      signal: suggestionsAbortController.signal
    });
    if (!res.ok) throw new Error('Could not load suggestions');

    const data = await res.json();
    const results = Array.isArray(data.results) ? data.results : [];

    if (results.length === 0) {
      suggestionsStatus.textContent = 'No suggestions found.';
      return;
    }

    suggestionsStatus.textContent = 'Recommendations (Top 5)';
    suggestionsList.innerHTML = results.map(track => {
      const trackObj = normalizeTrack({
        id: track.id,
        title: track.title || track.id,
        artist: track.artist || 'Unknown Artist',
        bpm: track.bpm,
        key: track.key,
        camelot: track.camelot,
        energy: track.energy,
        score: track.score * 100
      });
      const payload = encodeURIComponent(JSON.stringify(trackObj));
      return `
        <div class="flex flex-col bg-white border border-gray-200 rounded-md p-3 hover:bg-gray-50 transition cursor-pointer"
             onclick='addToPlaylist(JSON.parse(decodeURIComponent("${payload}")))'
             draggable="true"
             ondragstart='onDragStart(event, decodeURIComponent("${payload}"))'>
          <div class="flex items-center justify-between mb-2">
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-900 truncate" title="${escapeHtml(trackObj.title)}">${escapeHtml(trackObj.title)}</div>
              <div class="text-xs text-gray-600 truncate">${escapeHtml(trackObj.artist)}</div>
            </div>
            <div class="text-xs text-gray-600 ml-3 flex-shrink-0">${(track.score * 100).toFixed(1)}%</div>
          </div>
          <div class="flex flex-wrap gap-1">
            ${trackObj.bpm ? `<span class="text-xs px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded">${Math.round(trackObj.bpm)} BPM</span>` : ''}
            ${trackObj.key ? `<span class="text-xs px-1.5 py-0.5 bg-purple-50 text-purple-700 rounded">${escapeHtml(trackObj.key)}</span>` : ''}
            ${trackObj.camelot ? `<span class="text-xs px-1.5 py-0.5 bg-green-50 text-green-700 rounded">${escapeHtml(trackObj.camelot)}</span>` : ''}
            ${trackObj.energy ? `<span class="text-xs px-1.5 py-0.5 bg-orange-50 text-orange-700 rounded">${(trackObj.energy * 100).toFixed(0)}%</span>` : ''}
          </div>
        </div>
      `;
    }).join('');
  } catch (error) {
    if (error.name === 'AbortError') return;
    suggestionsStatus.textContent = error.message || 'Error loading suggestions';
    suggestionsList.innerHTML = '';
  }
}

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 transform bg-gray-800 text-white px-4 py-2 rounded text-sm z-50 animate-fade-in border border-gray-700 shadow-sm';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 2000);
}

/**
 * Normalize track objects to ensure required fields exist.
 * Handles inconsistent field names from different API sources.
 * 
 * @param {Object} track - Raw track data (may have missing fields)
 * @returns {Object} Normalized track with guaranteed fields (id, title, artist, score)
 */
function normalizeTrack(track) {
  return {
    id: track.id || '',
    title: track.title || track.id || 'Unknown track',
    artist: track.artist || 'Unknown',
    score: typeof track.score === 'number' ? track.score : 0,
    bpm: track.bpm || null,
    key: track.key || null,
    camelot: (typeof track.camelot === 'string' && track.camelot.trim() !== '' ? track.camelot : 'n/a'),
    energy: track.energy || null,
  };
}

// Safe parse helper for payload strings
function safeParseTrack(payload) {
  try {
    return normalizeTrack(JSON.parse(payload));
  } catch (_) {
    return normalizeTrack({ id: '', title: 'Unknown', artist: 'Unknown', score: 0 });
  }
}

// Handle drag start for adding tracks via drop
function onDragStart(event, payloadStr, sourceIndex) {
  if (!event?.dataTransfer) return;
  const track = safeParseTrack(payloadStr);
  if (typeof sourceIndex === 'number') {
    track._sourceIndex = sourceIndex;
  }
  event.dataTransfer.effectAllowed = 'copy';
  const serialized = JSON.stringify(track);
  event.dataTransfer.setData('application/json', serialized);
  event.dataTransfer.setData('text/plain', serialized);

  // Create and attach a custom drag preview
  const dragEl = createDragImage(track);
  dragImageEl = dragEl;
  event.dataTransfer.setDragImage(dragEl, 12, 12);
}

// Build a small drag image element that follows the cursor
function createDragImage(track) {
  const el = document.createElement('div');
  el.className = 'drag-ghost shadow-sm border border-gray-200 bg-white rounded-md px-3 py-2 text-xs text-gray-800 flex items-center gap-2';
  el.innerHTML = `
    <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-semibold">★</span>
    <div class="flex flex-col min-w-0">
      <span class="font-semibold truncate max-w-[160px]">${escapeHtml(track.title)}</span>
      <span class="text-gray-500 truncate max-w-[140px]">${escapeHtml(track.artist)}</span>
    </div>
  `;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add('drag-ghost-active'));
  return el;
}

// Remove drag image after drag ends
function cleanupDragImage() {
  if (dragImageEl && dragImageEl.parentNode) {
    dragImageEl.parentNode.removeChild(dragImageEl);
  }
  dragImageEl = null;
  playlistDiv.classList.remove('playlist-drop-active');
  currentDropIndex = null;
  updatePlaylistDisplay(false);
}

// Determine drop index based on mouse position relative to playlist items
/**
 * Calculate the index where a dragged item should be dropped in the playlist.
 * Determines the insertion position based on the mouse Y coordinate relative to existing playlist cards.
 * 
 * @param {DragEvent} event - The drag event containing clientY position
 * @returns {number} The index position (0-based) where the track should be inserted
 * 
 * Logic:
 * - Returns 0 if playlist is empty
 * - Compares mouse Y position against the midpoint of each card
 * - If mouse is above a card's midpoint, inserts before that card
 * - Otherwise inserts at the end
 */
function computeDropIndex(event) {
  const items = Array.from(playlistDiv.querySelectorAll('[data-index]'));
  if (items.length === 0) return 0;

  const y = event.clientY;
  for (const el of items) {
    const rect = el.getBoundingClientRect();
    const mid = rect.top + rect.height / 2;
    const idx = Number(el.dataset.index || '0');
    if (y < mid) {
      return idx;
    }
  }
  return items.length; // drop at end
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Initialize suggestions state on load
updateSuggestions();