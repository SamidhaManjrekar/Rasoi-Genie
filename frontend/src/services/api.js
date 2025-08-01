// API Configuration and Service
const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth endpoints
  async register(userData) {
    return this.request('/register', {
      method: 'POST',
      body: userData,
    });
  }

  async login(credentials) {
    return this.request('/login', {
      method: 'POST',
      body: credentials,
    });
  }

  // Protected endpoints
  async getProtectedData(token) {
    return this.request('/protected', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // Future endpoints
  async savePreferences(preferences, token) {
    return this.request('/preferences', {
      method: 'POST',
      body: preferences,
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async getPreferences(token) {
    return this.request('/preferences', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }
}

export const apiService = new ApiService();