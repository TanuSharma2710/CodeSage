import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ThemeToggle, { ThemeProvider } from '../components/ThemeToggle';
import { getStudyRecommendationsAnonymous } from '../services/api';
import './Study.css';

const StudyContent = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [recommendations, setRecommendations] = useState(null);
    const [error, setError] = useState('');
    const [topics, setTopics] = useState(location.state?.topics || []);

    useEffect(() => {
        if (topics.length > 0) {
            fetchRecommendations();
        }
    }, []);

    const fetchRecommendations = async () => {
        setIsLoading(true);
        setError('');

        try {
            const response = await getStudyRecommendationsAnonymous({
                topics: topics,
                language: 'python'
            });
            setRecommendations(response);
        } catch (err) {
            setError('Failed to load recommendations. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleBackToDebugger = () => {
        navigate('/debugger');
    };

    return (
        <div className="study-page">
            <Header />

            <div className="study-header">
                <div className="container">
                    <div className="study-title-row">
                        <div>
                            <h1>📚 Study Session</h1>
                            <p>Curated resources to help you master the topics</p>
                        </div>
                        <div className="header-actions">
                            <ThemeToggle />
                            <button className="back-btn" onClick={handleBackToDebugger}>
                                ← Back to Debugger
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <main className="study-main">
                <div className="container">
                    {/* Topics Summary */}
                    {topics.length > 0 && (
                        <div className="topics-banner">
                            <span className="banner-label">Learning Topics:</span>
                            <div className="topics-tags">
                                {topics.map((topic, index) => (
                                    <span key={index} className="topic-tag">{topic}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {topics.length === 0 && (
                        <div className="no-topics">
                            <div className="no-topics-icon">🔍</div>
                            <h2>No Topics Selected</h2>
                            <p>Go to the debugger to analyze code and get study recommendations.</p>
                            <button className="primary-btn" onClick={handleBackToDebugger}>
                                Go to Debugger
                            </button>
                        </div>
                    )}

                    {isLoading && (
                        <div className="loading-container">
                            <div className="loader"></div>
                            <p>Loading study resources...</p>
                        </div>
                    )}

                    {error && (
                        <div className="error-banner">{error}</div>
                    )}

                    {recommendations && (
                        <div className="study-grid">
                            {/* Resources Section */}
                            <section className="study-section resources-section">
                                <div className="section-header">
                                    <h2>📖 Top Learning Resources</h2>
                                    <span className="count-badge">{recommendations.resources.length}</span>
                                </div>
                                <div className="resources-list">
                                    {recommendations.resources.map((resource, index) => (
                                        <a
                                            key={index}
                                            href={resource.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="resource-card"
                                        >
                                            <div className="resource-type">{resource.type}</div>
                                            <h3>{resource.title}</h3>
                                            <p>{resource.description}</p>
                                            <span className="resource-link">
                                                Visit Resource →
                                            </span>
                                        </a>
                                    ))}
                                </div>
                            </section>

                            {/* YouTube Videos Section */}
                            <section className="study-section videos-section">
                                <div className="section-header">
                                    <h2>🎬 Recommended Videos</h2>
                                    <span className="count-badge">{recommendations.youtube_videos.length}</span>
                                </div>
                                <div className="videos-list">
                                    {recommendations.youtube_videos.map((video, index) => (
                                        <a
                                            key={index}
                                            href={video.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="video-card"
                                        >
                                            <div className="video-thumbnail">
                                                <div className="play-icon">▶</div>
                                                {video.duration && (
                                                    <span className="video-duration">{video.duration}</span>
                                                )}
                                            </div>
                                            <div className="video-info">
                                                <h3>{video.title}</h3>
                                                <span className="video-channel">{video.channel}</span>
                                            </div>
                                        </a>
                                    ))}
                                </div>
                            </section>

                            {/* Video Summary Section */}
                            {recommendations.best_video_summary && (
                                <section className="study-section summary-section">
                                    <div className="section-header">
                                        <h2>🤖 AI Video Summary</h2>
                                        <span className="ai-badge">AI Generated</span>
                                    </div>
                                    <div className="summary-content">
                                        <div className="summary-card">
                                            <h3>{recommendations.best_video_summary.title}</h3>

                                            <div className="summary-topics">
                                                <h4>Topics Covered:</h4>
                                                <div className="summary-topic-tags">
                                                    {recommendations.best_video_summary.topics.map((topic, index) => (
                                                        <span key={index} className="summary-tag">{topic}</span>
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="summary-text">
                                                <h4>Summary:</h4>
                                                <p>{recommendations.best_video_summary.summary}</p>
                                            </div>

                                            <div className="key-points">
                                                <h4>Key Points:</h4>
                                                <ul>
                                                    {recommendations.best_video_summary.key_points.map((point, index) => (
                                                        <li key={index}>
                                                            <span className="point-icon">✓</span>
                                                            {point}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </section>
                            )}
                        </div>
                    )}
                </div>
            </main>

            <Footer />
        </div>
    );
};

const Study = () => {
    return (
        <ThemeProvider>
            <StudyContent />
        </ThemeProvider>
    );
};

export default Study;
