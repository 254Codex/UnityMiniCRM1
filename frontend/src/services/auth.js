import api from './api';

export default {
  async login(credentials) {
    try {
      const response = await api.auth.login(credentials);
      const { token, user } = response.data;
      
      // Store token and user info
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set default auth header
      api.setAuthToken(token);
      
      return { success: true, user };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data || 'Login failed' 
      };
    }
  },
  
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    api.setAuthToken(null);
  },
  
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },
  
  async refreshToken() {
    try {
      const response = await api.auth.refreshToken();
      const { token } = response.data;
      localStorage.setItem('token', token);
      api.setAuthToken(token);
      return token;
    } catch (error) {
      this.logout();
      throw error;
    }
  },
};
