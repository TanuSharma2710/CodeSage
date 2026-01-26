import { useState, createContext, useContext } from 'react';
import './ThemeToggle.css';

// Theme context
const ThemeContext = createContext();

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
    const [isDark, setIsDark] = useState(true);

    const toggleTheme = () => {
        setIsDark(!isDark);
        document.body.classList.toggle('light-mode', !isDark);
    };

    return (
        <ThemeContext.Provider value={{ isDark, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

const ThemeToggle = () => {
    const { isDark, toggleTheme } = useTheme();

    return (
        <button
            className={`theme-toggle ${isDark ? 'dark' : 'light'}`}
            onClick={toggleTheme}
            aria-label="Toggle theme"
        >
            <span className="toggle-icon">
                {isDark ? '🌙' : '☀️'}
            </span>
            <span className="toggle-text">
                {isDark ? 'Dark' : 'Light'}
            </span>
        </button>
    );
};

export default ThemeToggle;
