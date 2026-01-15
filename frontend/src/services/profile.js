import api from './api';

export default {
  async getProfile() {
    try {
      const response = await api.users.getProfile();
      return response.data;
    } catch (error) {
      console.error('Error fetching profile:', error);
      throw error;
    }
  },
  
  async updateProfile(profileData) {
    try {
      const response = await api.users.updateProfile(profileData);
      // Update stored user info
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const updatedUser = { ...user, ...response.data.user };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return response.data;
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  },
  
  async uploadAvatar(file) {
    try {
      const formData = new FormData();
      formData.append('avatar', file);
      const response = await api.users.updateProfile({ avatar: file });
      return response.data;
    } catch (error) {
      console.error('Error uploading avatar:', error);
      throw error;
    }
  },
  
  async getNotificationPreferences() {
    try {
      const response = await api.users.getNotificationPreferences();
      return response.data;
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
      throw error;
    }
  },
  
  async updateNotificationPreferences(preferences) {
    try {
      const response = await api.users.updateNotificationPreferences(preferences);
      return response.data;
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      throw error;
    }
  },
};
