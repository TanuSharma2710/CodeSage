import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './Header.css';

const Header = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout, isAuthenticated } = useAuth();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const isActive = (path) => location.pathname === path;

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <header className={`header ${isScrolled ? 'header-scrolled' : ''}`}>
            <div className="header-container">
                <Link to="/" className="logo" onClick={scrollToTop}>
                    <span className="logo-icon">🧠</span>
                    <span className="logo-text">CodeSage</span>
                </Link>

                <nav className="nav">
                    <Link
                        to="/"
                        className={`nav-link ${isActive('/') ? 'active' : ''}`}
                        onClick={scrollToTop}
                    >
                        Home
                    </Link>
                    <Link
                        to="/debugger"
                        className={`nav-link ${isActive('/debugger') ? 'active' : ''}`}
                    >
                        Debugger
                    </Link>
                    <Link
                        to="/study"
                        className={`nav-link ${isActive('/study') ? 'active' : ''}`}
                    >
                        Study
                    </Link>
                    <Link
                        to="/analysis"
                        className={`nav-link ${isActive('/analysis') ? 'active' : ''}`}
                    >
                        Analysis
                    </Link>
                </nav>

                <div className="header-actions">
                    {isAuthenticated ? (
                        <>
                            <span className="user-greeting">
                                👋 Hey, <strong>{user?.name?.split(' ')[0]}</strong>
                            </span>
                            <button onClick={handleLogout} className="btn btn-ghost">
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="btn btn-ghost">
                                Login
                            </Link>
                            <Link to="/signup" className="btn btn-primary">
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;
