// Fetches config values from the backend API and exposes them for validation
// Usage: await ConfigAPI.load(); then use ConfigAPI.values.password_min_length etc.

const ConfigAPI = {
    values: {},
    async load() {
        try {
            const res = await fetch(AppConfig.getApiUrl('/config/get'));
            if (!res.ok) throw new Error('Failed to load config');
            this.values = await res.json();
        } catch (e) {
            console.error('Could not fetch config from API:', e);
            // Fallback: set defaults if needed
            this.values = {
                username_min_length: 4,
                username_max_length: 16,
                password_min_length: 8,
                password_max_length: 64,
                bio_max_length: 500,
                prefered_genres_max_length: 10,
                prefered_max_length_per_genre: 15,
                prefered_bpm_min: 50,
                prefered_bpm_max: 250,
                min_playlist_name_length: 3,
                max_playlist_name_length: 25,
                playlist_description_max_length: 200
            };
        }
    }
};