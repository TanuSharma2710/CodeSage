import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();
    const location = useLocation();

    // Show loading while checking auth state
    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loading-spinner-large"></div>
                <p>Loading...</p>
            </div>
        );
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
        // Save the attempted URL so we can redirect back after login
        return <Navigate to="/login" state={{ from: location.pathname }} replace />;
    }

    return children;
};

export default ProtectedRoute;
