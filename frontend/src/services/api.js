import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth API
export const authAPI = {
    signup: async (userData) => {
        const response = await api.post('/auth/signup', userData);
        return response.data;
    },

    login: async (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await api.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await api.get('/users/me');
        return response.data;
    },
};

// User API
export const userAPI = {
    getProfile: async () => {
        const response = await api.get('/users/me');
        return response.data;
    },
};

// Debugger API
export const debuggerAPI = {
    analyzeCode: async (debugRequest) => {
        const response = await api.post('/debug/', debugRequest);
        return response.data;
    },

    analyzeCodeAnonymous: async (debugRequest) => {
        const response = await api.post('/debug/anonymous', debugRequest);
        return response.data;
    },

    getHistory: async (limit = 10, offset = 0) => {
        const response = await api.get(`/debug/history?limit=${limit}&offset=${offset}`);
        return response.data;
    },
};

// Study API
export const studyAPI = {
    getRecommendations: async (studyRequest) => {
        const response = await api.post('/study/recommendations', studyRequest);
        return response.data;
    },

    getRecommendationsAnonymous: async (studyRequest) => {
        const response = await api.post('/study/recommendations/anonymous', studyRequest);
        return response.data;
    },
};

// Helper functions for direct imports
export const debugCodeAnonymous = debuggerAPI.analyzeCodeAnonymous;
export const getStudyRecommendationsAnonymous = studyAPI.getRecommendationsAnonymous;

export default api;

