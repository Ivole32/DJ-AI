// Profile Management
class ProfileService {
    constructor() {
        this.API_URL = AppConfig.getApiUrl('');
        // Use API base URL for static files (without /api/v1 prefix)
        this.BASE_URL = `${AppConfig.api.baseUrl}`;
        this.authService = getAuthService();
    }

    // Get user profile from backend
    async getProfile() {
        try {
            console.log('Fetching profile from backend...');
            
            // First get username from /user/me endpoint
            const meResponse = await fetchWithTokenRefresh(`${this.API_URL}/user/me`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!meResponse.ok) {
                const errorData = await meResponse.json();
                throw new Error(formatApiError(errorData));
            }
            
            const meData = await meResponse.json();
            const username = meData.username;
            
            // Then get full profile data from /profile/<username>
            const profileResponse = await fetchWithTokenRefresh(`${this.API_URL}/profile/${username}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!profileResponse.ok) {
                const errorData = await profileResponse.json();
                throw new Error(formatApiError(errorData));
            }
            
            const profileData = await profileResponse.json();
            
            // Extract BPM range if it exists
            let minBpm = 120;
            let maxBpm = 140;
            if (profileData.prefered_bpm_range && Array.isArray(profileData.prefered_bpm_range)) {
                minBpm = profileData.prefered_bpm_range[0] || 120;
                maxBpm = profileData.prefered_bpm_range[1] || 140;
            }
            
            // Return profile data with backend info
            return {
                success: true,
                profile: {
                    user_id: meData.user_id,
                    username: profileData.username,
                    // email: profileData.email,
                    role_id: meData.role_id,
                    avatar: profileData.avatar_url
                        ? (profileData.avatar_url.startsWith('http')
                            ? profileData.avatar_url
                            : `${this.BASE_URL}${profileData.avatar_url}`)
                        : `https://api.dicebear.com/7.x/initials/png?seed=${profileData.username}`,
                    bio: profileData.bio || '',
                    favoriteGenres: profileData.prefered_genres || [],
                    minBpm: minBpm,
                    maxBpm: maxBpm,
                    stats: {
                        playlistCount: 0,
                        trackCount: 0,
                        searchCount: 0,
                        memberSince: 'Jan 2026'
                    }
                }
            };
        } catch (error) {
            console.error('Error fetching profile:', error);
            return { success: false, error: error.message };
        }
    }

    // Update profile
    async updateProfile(profileData) {
        try {
            console.log('Updating profile:', profileData);
            
            const response = await fetchWithTokenRefresh(`${this.API_URL}/profile/update-profile`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(formatApiError(data));
            }
            
            return { success: true, message: data.message || 'Profile updated successfully' };
        } catch (error) {
            console.error('Error updating profile:', error);
            return { success: false, error: error.message };
        }
    }

    // Update password
    async updatePassword(currentPassword, newPassword) {
        try {
            const response = await fetchWithTokenRefresh(`${this.API_URL}/user/change-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(formatApiError(data));
            }
            
            return { success: true, message: data.detail || 'Password changed successfully' };
        } catch (error) {
            console.error('Error updating password:', error);
            return { success: false, error: error.message };
        }
    }

    // Upload avatar
    async uploadAvatar(file) {
        try {
            console.log('Uploading avatar:', file.name, 'Size:', file.size, 'Type:', file.type);
            
            // Validate file size (5MB max)
            const maxSize = 5 * 1024 * 1024;
            if (file.size > maxSize) {
                return { success: false, error: 'File size must be less than 5MB' };
            }
            
            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                return { success: false, error: 'Only JPEG, PNG, and WEBP images are allowed' };
            }
            
            // Create FormData to upload the file
            const formData = new FormData();
            formData.append('file', file);
            
            console.log('Sending upload request to:', `${this.API_URL}/profile/profile-picture`);
            
            const response = await fetchWithTokenRefresh(`${this.API_URL}/profile/profile-picture`, {
                method: 'POST',
                body: formData
                // Don't set Content-Type header - browser will set it automatically with boundary
            });
            
            console.log('Upload response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Avatar uploaded successfully:', data);
                
                // Use the URL from the server response
                const avatarUrl = data.avatar_url
                    ? (data.avatar_url.startsWith('http')
                        ? data.avatar_url
                        : `${this.BASE_URL}${data.avatar_url}`)
                    : URL.createObjectURL(file);
                
                return { success: true, avatarUrl: avatarUrl };
            } else {
                const error = await response.json();
                console.error('Upload failed:', error);
                return { success: false, error: error.detail || 'Failed to upload avatar' };
            }
        } catch (error) {
            console.error('Error uploading avatar:', error);
            return { success: false, error: error.message };
        }
    }

    // Delete/Reset avatar to default
    async deleteAvatar() {
        try {
            console.log('Resetting avatar to default...');
            
            const response = await fetchWithTokenRefresh(`${this.API_URL}/profile/profile-picture`, {
                method: 'DELETE'
            });
            
            console.log('Reset response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Avatar reset successfully:', data);
                return { success: true, message: data.message };
            } else {
                const error = await response.json();
                console.error('Reset failed:', error);
                return { success: false, error: error.detail || 'Failed to reset avatar' };
            }
        } catch (error) {
            console.error('Error resetting avatar:', error);
            return { success: false, error: error.message };
        }
    }

    // Delete account
    async deleteAccount() {
        try {
            const response = await fetchWithTokenRefresh(`${this.API_URL}/user/delete-account`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Account deleted successfully');
                // Logout after successful deletion (tokens are already cleared by backend)
                localStorage.removeItem(this.authService.USER_KEY);
                window.location.href = '/login';
                return { success: true, message: data.message };
            } else {
                const error = await response.json();
                return { success: false, error: error.detail || 'Failed to delete account' };
            }
        } catch (error) {
            console.error('Error deleting account:', error);
            return { success: false, error: error.message };
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize profile service
const profileService = new ProfileService();

// Feedback helper function
function showFeedback(element, message, type = 'info') {
    if (!element) return;
    
    element.textContent = message;
    element.className = `feedback-message ${type}`;
    element.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

// Load profile data
async function loadProfile() {
    const result = await profileService.getProfile();
    
    if (result.success) {
        const profile = result.profile;
        
        // Update form fields with backend data
        document.getElementById('username').value = profile.username || 'N/A';
        document.getElementById('userId').value = profile.user_id || 'N/A';
        document.getElementById('roleId').value = getRoleName(profile.role_id);
        
        // Update optional fields if they exist
        const bioField = document.getElementById('bio');
        const genresField = document.getElementById('favoriteGenres');
        const minBpmField = document.getElementById('minBpm');
        const maxBpmField = document.getElementById('maxBpm');
        
        if (bioField) bioField.value = profile.bio || '';
        if (genresField) genresField.value = Array.isArray(profile.favoriteGenres) ? profile.favoriteGenres.join(', ') : '';
        if (minBpmField) minBpmField.value = profile.minBpm || 120;
        if (maxBpmField) maxBpmField.value = profile.maxBpm || 140;
        
        // Update avatar with initials based on username
        document.getElementById('avatarImage').src = profile.avatar;
        
        // Update stats if elements exist
        const playlistCount = document.getElementById('playlistCount');
        const trackCount = document.getElementById('trackCount');
        const searchCount = document.getElementById('searchCount');
        const memberSince = document.getElementById('memberSince');
        
        if (playlistCount) playlistCount.textContent = profile.stats.playlistCount;
        if (trackCount) trackCount.textContent = profile.stats.trackCount;
        if (searchCount) searchCount.textContent = profile.stats.searchCount.toLocaleString();
        if (memberSince) memberSince.textContent = profile.stats.memberSince;
        
        console.log('Profile loaded successfully:', profile);
    } else {
        console.error('Failed to load profile:', result.error);
        // Redirect to login if not authenticated
        window.location.href = AppConfig.app.loginRoute;
    }
}

// Helper function to get role name from role_id
function getRoleName(roleId) {
    const roles = {
        1: 'User',
        2: 'Premium User',
        3: 'Moderator',
        4: 'Admin'
    };
    return roles[roleId] || `Role ${roleId}`;
}

// Profile form submit
document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get only the fields that can be updated
    const profileData = {};
    
    const bioField = document.getElementById('bio');
    const genresField = document.getElementById('favoriteGenres');
    const minBpmField = document.getElementById('minBpm');
    const maxBpmField = document.getElementById('maxBpm');
    
    // Bio (string, max 500 characters)
    if (bioField) {
        profileData.bio = bioField.value.trim();
    }
    
    // Favorite genres (convert comma-separated string to array)
    if (genresField) {
        const genresString = genresField.value.trim();
        profileData.prefered_genres = genresString 
            ? genresString.split(',').map(g => g.trim()).filter(g => g.length > 0).slice(0, 10)
            : [];
    }
    
    // BPM range (tuple of [min, max])
    const minBpm = minBpmField ? parseInt(minBpmField.value) : 120;
    const maxBpm = maxBpmField ? parseInt(maxBpmField.value) : 140;
    
    // Validate BPM range
    if (minBpm >= maxBpm) {
        const feedbackEl = document.getElementById('profileFeedback');
        showFeedback(feedbackEl, 'Minimum BPM must be less than maximum BPM!', 'error');
        return;
    }
    
    profileData.prefered_bpm_range = [minBpm, maxBpm];
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';
    
    const result = await profileService.updateProfile(profileData);
    
    const feedbackEl = document.getElementById('profileFeedback');
    if (result.success) {
        showFeedback(feedbackEl, result.message, 'success');
    } else {
        showFeedback(feedbackEl, 'Error updating profile: ' + formatApiError(result.error), 'error');
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
});

// Password form submit
document.getElementById('passwordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const feedbackEl = document.getElementById('passwordFeedback');
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    
    // Validation
    if (newPassword.length < 8) {
        showFeedback(feedbackEl, 'New password must be at least 8 characters long!', 'error');
        return;
    }
    
    if (newPassword !== confirmNewPassword) {
        showFeedback(feedbackEl, 'New passwords do not match!', 'error');
        return;
    }
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Changing...';
    
    const result = await profileService.updatePassword(currentPassword, newPassword);
    
    if (result.success) {
        showFeedback(feedbackEl, result.message, 'success');
        e.target.reset();
    } else {
        showFeedback(feedbackEl, formatApiError(result.error), 'error');
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
});

// Avatar change handler
document.getElementById('changeAvatarBtn').addEventListener('click', () => {
    document.getElementById('avatarInput').click();
});

// Avatar reset handler
document.getElementById('resetAvatarBtn').addEventListener('click', async () => {
    const confirmed = await customConfirm(
        'Do you want to reset your profile picture to the default?',
        'Reset Profile Picture'
    );
    
    if (!confirmed) {
        return;
    }
    
    const feedbackEl = document.getElementById('profileFeedback');
    showFeedback(feedbackEl, 'Resetting profile picture...', 'info');
    
    const result = await profileService.deleteAvatar();
    
    if (result.success) {
        showFeedback(feedbackEl, 'Profile picture reset to default!', 'success');
        // Reload profile to get default avatar
        setTimeout(() => loadProfile(), 500);
    } else {
        showFeedback(feedbackEl, 'Error resetting picture: ' + formatApiError(result.error), 'error');
    }
});

document.getElementById('avatarInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const feedbackEl = document.getElementById('profileFeedback');
        showFeedback(feedbackEl, 'Uploading profile picture...', 'info');
        
        const result = await profileService.uploadAvatar(file);
        
        if (result.success) {
            document.getElementById('avatarImage').src = result.avatarUrl;
            showFeedback(feedbackEl, 'Profile picture uploaded successfully!', 'success');
            
            // Reload profile to get updated data from backend
            setTimeout(() => loadProfile(), 1000);
        } else {
            showFeedback(feedbackEl, 'Error uploading picture: ' + formatApiError(result.error), 'error');
        }
        
        // Reset file input
        e.target.value = '';
    }
});

// Delete account handler
document.getElementById('deleteAccountBtn').addEventListener('click', async () => {
    const confirmed = await customConfirm(
        'Do you really want to delete your account? This action cannot be undone and all your data (playlists, profiles, settings) will be permanently deleted.',
        'Delete Account'
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        const result = await profileService.deleteAccount();
        
        if (result.success) {
            toast.success('Account deleted successfully');
            // Redirect is handled in deleteAccount method
        } else {
            toast.error('Error deleting account: ' + formatApiError(result.error));
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        toast.error('Failed to delete account');
    }
});

// Make sure that loadPlaylists is called in the Public Profile tab.
if (window.location.pathname.endsWith('user-profile.html')) {
    document.addEventListener('DOMContentLoaded', async () => {
        // Nach dem Laden des Profils:
        const profile = await loadProfile();
        if (profile) {
            loadPlaylists(profile);
        }
    });
}

// Load profile on page load
loadProfile();
