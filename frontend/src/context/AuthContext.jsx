import { createContext, useState, useContext, useEffect, useCallback } from 'react';
import API_BASE_URL from '../config/apiBaseUrl';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Refresh access token using refresh token
    const refreshAccessToken = useCallback(async () => {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            return null;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh-token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                return data.access_token;
            } else {
                // Refresh token is invalid, clear everything
                clearTokens();
                return null;
            }
        } catch (err) {
            console.error('Failed to refresh token:', err);
            return null;
        }
    }, []);

    // Fetch user data with token
    const fetchUser = useCallback(async (token) => {
        try {
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
                return true;
            } else if (response.status === 401) {
                // Access token expired, try to refresh
                const newToken = await refreshAccessToken();
                if (newToken) {
                    // Retry with new token
                    const retryResponse = await fetch(`${API_BASE_URL}/users/me`, {
                        headers: {
                            'Authorization': `Bearer ${newToken}`
                        }
                    });
                    if (retryResponse.ok) {
                        const userData = await retryResponse.json();
                        setUser(userData);
                        return true;
                    }
                }
                // Couldn't refresh, clear tokens
                clearTokens();
                setUser(null);
                return false;
            } else {
                clearTokens();
                setUser(null);
                return false;
            }
        } catch (err) {
            console.error('Failed to fetch user:', err);
            setUser(null);
            return false;
        }
    }, [refreshAccessToken]);

    // Clear all tokens from storage
    const clearTokens = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token');  // Legacy
        localStorage.removeItem('token_type');  // Legacy
    };

    // Check for existing token and fetch user on mount
    useEffect(() => {
        const initAuth = async () => {
            // Check for both new and legacy token storage
            const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
            if (accessToken) {
                await fetchUser(accessToken);
            }
            setLoading(false);
        };
        initAuth();
    }, [fetchUser]);

    // Login - store both tokens
    const login = async (accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
        await fetchUser(accessToken);
    };

    // Logout - clear tokens and call API to revoke all tokens
    const logout = async () => {
        const accessToken = localStorage.getItem('access_token');
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            });
        } catch (err) {
            console.error('Logout API call failed:', err);
        }
        clearTokens();
        setUser(null);
    };

    // Get current access token (refresh if needed)
    const getAccessToken = async () => {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            return null;
        }
        // For now, just return the token
        // In production, you'd check expiry and refresh if needed
        return accessToken;
    };

    const value = {
        user,
        loading,
        login,
        logout,
        getAccessToken,
        refreshAccessToken,
        isAuthenticated: !!user
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthContext;

