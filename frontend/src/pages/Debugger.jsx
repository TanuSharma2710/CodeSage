import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ThemeToggle, { ThemeProvider } from '../components/ThemeToggle';
import DiffViewer from '../components/DiffViewer';
import { debuggerAPI, debugCodeAnonymous } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Debugger.css';

const DebuggerContent = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user } = useAuth();
    const [code, setCode] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [language, setLanguage] = useState('python');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [languageWarning, setLanguageWarning] = useState('');
    const [isPrefilled, setIsPrefilled] = useState(false);
    const [expectedOutput, setExpectedOutput] = useState('');
    const [showExpectedOutput, setShowExpectedOutput] = useState(false);

    // Handle prefill data from Analysis page
    useEffect(() => {
        if (location.state?.prefillData) {
            const data = location.state.prefillData;
            setCode(data.code || '');
            setErrorMessage(data.error_message || '');
            setLanguage(data.language || 'python');
            setIsPrefilled(true);

            // If there's previous solution data, show it
            if (data.diagnosis || data.fixed_code) {
                // Parse wrong_lines and corrected_lines if they exist (stored as JSON strings)
                let mistakes = [];
                if (data.wrong_lines) {
                    try {
                        const wrongLines = JSON.parse(data.wrong_lines);
                        mistakes = wrongLines.map(line => `Line was: ${line}`);
                    } catch (e) {
                        mistakes = [data.diagnosis || 'Error identified and fixed'];
                    }
                } else {
                    mistakes = [data.diagnosis || 'Error identified and fixed'];
                }

                setResult({
                    diagnosis: data.diagnosis,
                    fixed_code: data.fixed_code,
                    study_topics: data.study_topics ? JSON.parse(data.study_topics) : [],
                    mistakes: mistakes,
                    changed_lines: []
                });
            }
        }
    }, [location.state]);

    // Detect language from code patterns
    const detectLanguage = (codeText) => {
        const patterns = {
            java: [/public\s+class\s+/, /public\s+static\s+void\s+main/, /System\.out\.print/],
            python: [/def\s+\w+\s*\(/, /print\s*\(/, /import\s+\w+/, /__name__\s*==\s*['"]__main__['"]/],
            javascript: [/const\s+\w+\s*=/, /let\s+\w+\s*=/, /function\s+\w+\s*\(/, /console\.log/, /=>\s*{/],
            cpp: [/#include\s*</, /int\s+main\s*\(/, /std::/, /cout\s*<</],
            csharp: [/using\s+System/, /namespace\s+/, /static\s+void\s+Main/, /Console\.Write/]
        };

        for (const [lang, regexes] of Object.entries(patterns)) {
            if (regexes.some(regex => regex.test(codeText))) {
                return lang;
            }
        }
        return null;
    };

    // Check if code matches selected language
    const checkLanguageMatch = (codeText, selectedLang) => {
        const detectedLang = detectLanguage(codeText);
        if (detectedLang && detectedLang !== selectedLang) {
            return `⚠️ This looks like ${detectedLang.toUpperCase()} code, but you selected ${selectedLang.toUpperCase()}. Please select the correct language.`;
        }
        return '';
    };

    // Handle code change and check language
    const handleCodeChange = (e) => {
        const newCode = e.target.value;
        setCode(newCode);
        if (newCode.trim().length > 20) {
            setLanguageWarning(checkLanguageMatch(newCode, language));
        } else {
            setLanguageWarning('');
        }
    };

    // Handle language change
    const handleLanguageChange = (e) => {
        const newLang = e.target.value;
        setLanguage(newLang);
        if (code.trim().length > 20) {
            setLanguageWarning(checkLanguageMatch(code, newLang));
        }
    };

    const handleAnalyze = async () => {
        if (!code.trim() || !errorMessage.trim()) {
            setError('Please enter both code and error message');
            return;
        }

        // Warn about language mismatch but allow proceeding
        if (languageWarning) {
            setError(languageWarning);
            return;
        }

        setIsLoading(true);
        setError('');
        setResult(null);

        try {
            const debugRequest = {
                code,
                error_message: errorMessage,
                language,
                ...(expectedOutput.trim() && { expected_output: expectedOutput })
            };

            // Use authenticated endpoint if logged in (saves to database)
            // Otherwise use anonymous endpoint
            const response = user
                ? await debuggerAPI.analyzeCode(debugRequest)
                : await debugCodeAnonymous(debugRequest);

            setResult(response);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to analyze code. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleAnalyze();
        }
    };

    const handleExploreStudy = () => {
        if (result?.study_topics) {
            navigate('/study', { state: { topics: result.study_topics } });
        }
    };

    return (
        <div className="debugger-page">
            <Header />

            <div className="debugger-header">
                <div className="container">
                    <div className="debugger-title-row">
                        <div>
                            <h1>🔍 AI Debugger</h1>
                            <p>Paste your code and error, let AI diagnose the problem</p>
                        </div>
                        <ThemeToggle />
                    </div>
                </div>
            </div>

            <main className="debugger-main">
                <div className="debugger-container">
                    {/* Left Panel - Code Input */}
                    <div className="panel input-panel">
                        <div className="panel-header">
                            <h3>📝 Your Code</h3>
                            <select
                                value={language}
                                onChange={handleLanguageChange}
                                className="language-select"
                            >
                                <option value="python">Python</option>
                                <option value="javascript">JavaScript</option>
                                <option value="java">Java</option>
                                <option value="cpp">C++</option>
                                <option value="csharp">C#</option>
                            </select>
                        </div>
                        <div className="input-group">
                            <label>Code with error:</label>
                            <textarea
                                className="code-textarea"
                                placeholder="Paste your code here..."
                                value={code}
                                onChange={handleCodeChange}
                                onKeyDown={handleKeyDown}
                                spellCheck="false"
                            />
                            {languageWarning && (
                                <div className="language-warning">{languageWarning}</div>
                            )}
                        </div>
                        <div className="input-group">
                            <label>Terminal / Error message:</label>
                            <textarea
                                className="error-textarea"
                                placeholder="Paste the error message from terminal..."
                                value={errorMessage}
                                onChange={(e) => setErrorMessage(e.target.value)}
                                onKeyDown={handleKeyDown}
                                spellCheck="false"
                            />
                        </div>

                        {/* Optional Expected Output Section */}
                        <div className="expected-output-section">
                            <button
                                type="button"
                                className={`expected-output-toggle ${showExpectedOutput ? 'active' : ''}`}
                                onClick={() => setShowExpectedOutput(!showExpectedOutput)}
                            >
                                <span className="toggle-icon">{showExpectedOutput ? '▼' : '▶'}</span>
                                <span>Expected Output (Optional)</span>
                                <span className="optional-badge">For Logical Errors</span>
                            </button>
                            {showExpectedOutput && (
                                <div className="expected-output-content">
                                    <textarea
                                        className="expected-output-textarea"
                                        placeholder="Expected: [1, 2, 3]&#10;Got: [3, 2, 1]"
                                        value={expectedOutput}
                                        onChange={(e) => setExpectedOutput(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        spellCheck="false"
                                    />
                                </div>
                            )}
                        </div>
                        <button
                            className="analyze-btn"
                            onClick={handleAnalyze}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <span className="loading-spinner"></span>
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    🔍 Analyze Code
                                    <span className="shortcut">Ctrl + Enter</span>
                                </>
                            )}
                        </button>
                        {error && <div className="error-message">{error}</div>}
                    </div>

                    {/* Middle Panel - Diagnostics */}
                    <div className="panel diagnostics-panel">
                        <div className="panel-header">
                            <h3>🎯 AI Diagnosis</h3>
                        </div>
                        <div className="panel-content">
                            {!result && !isLoading && (
                                <div className="empty-state">
                                    <div className="empty-icon">🤖</div>
                                    <p>Paste your code and error message, then click "Analyze" to get AI diagnosis</p>
                                </div>
                            )}

                            {isLoading && (
                                <div className="loading-state">
                                    <div className="loading-animation">
                                        <div className="loading-bar"></div>
                                        <div className="loading-bar"></div>
                                        <div className="loading-bar"></div>
                                    </div>
                                    <p>Analyzing your code...</p>
                                </div>
                            )}

                            {result && (
                                <div className="diagnosis-content">
                                    <div className="diagnosis-section">
                                        <h4>📋 Diagnosis</h4>
                                        <p className="diagnosis-text">{result.diagnosis}</p>
                                    </div>

                                    <div className="diagnosis-section">
                                        <h4>❌ Mistakes Found</h4>
                                        <ul className="mistakes-list">
                                            {result.mistakes.map((mistake, index) => (
                                                <li key={index} className="mistake-item">
                                                    <span className="mistake-marker">•</span>
                                                    {mistake}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className="diagnosis-section">
                                        <h4>✅ Fixed Code</h4>
                                        <DiffViewer
                                            originalCode={code}
                                            fixedCode={result.fixed_code}
                                            changedLines={result.changed_lines || []}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Panel - Study Topics */}
                    <div className="panel study-panel">
                        <div className="panel-header">
                            <h3>📚 Study Topics</h3>
                        </div>
                        <div className="panel-content">
                            {!result && (
                                <div className="empty-state">
                                    <div className="empty-icon">📖</div>
                                    <p>Study recommendations will appear after analysis</p>
                                </div>
                            )}

                            {result && result.study_topics && (
                                <div className="study-content">
                                    <p className="study-intro">
                                        Based on your error, we recommend studying these topics:
                                    </p>
                                    <ul className="topics-list">
                                        {result.study_topics.map((topic, index) => (
                                            <li key={index} className="topic-item">
                                                <span className="topic-icon">📌</span>
                                                <span className="topic-name">{topic}</span>
                                            </li>
                                        ))}
                                    </ul>

                                    <div className="study-cta">
                                        <p>Want to improve in these areas?</p>
                                        <button
                                            className="study-btn"
                                            onClick={handleExploreStudy}
                                        >
                                            🎓 Explore Study Session
                                            <span className="btn-arrow">→</span>
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </main>

            <Footer />
        </div>
    );
};

const Debugger = () => {
    return (
        <ThemeProvider>
            <DebuggerContent />
        </ThemeProvider>
    );
};

export default Debugger;
