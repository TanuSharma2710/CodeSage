import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './Home.css';

const Home = () => {
    return (
        <div className="home-page">
            <Header />

            {/* Hero Section */}
            <section className="hero" id="home">
                <div className="hero-background">
                    <div className="hero-glow"></div>
                    <div className="hero-grid"></div>
                </div>
                <div className="container hero-content">
                    <div className="hero-badge fade-in-up">
                        <span className="badge-icon">✨</span>
                        <span>AI-Powered Debugging Platform</span>
                    </div>
                    <h1 className="hero-title fade-in-up">
                        Empowering the Next Generation of
                        <span className="text-gradient"> Smart Developers</span>
                    </h1>
                    <p className="hero-subtitle fade-in-up">
                        Turning Bugs into Breakthroughs. Debug Smarter. Learn Faster. Build Better.
                    </p>
                    <div className="hero-cta fade-in-up">
                        <Link to="/signup" className="btn btn-primary btn-large">
                            <span>🚀</span>
                            Get Started
                        </Link>
                        <a href="#features" className="btn btn-secondary btn-large">
                            Learn More
                        </a>
                    </div>
                    <div className="hero-stats fade-in-up">
                        <div className="stat-item">
                            <span className="stat-number">10K+</span>
                            <span className="stat-label">Bugs Fixed</span>
                        </div>
                        <div className="stat-divider"></div>
                        <div className="stat-item">
                            <span className="stat-number">5K+</span>
                            <span className="stat-label">Developers</span>
                        </div>
                        <div className="stat-divider"></div>
                        <div className="stat-item">
                            <span className="stat-number">95%</span>
                            <span className="stat-label">Success Rate</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* What We Offer Section */}
            <section className="section features-section" id="features">
                <div className="container">
                    <span className="section-badge">🧠 What We Offer</span>
                    <h2 className="section-title">Powerful Features for Modern Developers</h2>
                    <p className="section-subtitle">
                        Everything you need to debug, learn, and grow as a developer
                    </p>

                    <div className="features-grid">
                        <div className="feature-card glass-card">
                            <div className="feature-icon">🤖</div>
                            <h3 className="feature-title">AI-Powered Debugging Assistant</h3>
                            <p className="feature-description">
                                Fix code instantly with intelligent explanations and suggestions.
                                Our AI helps you find and solve errors quickly and efficiently.
                            </p>
                        </div>

                        <div className="feature-card glass-card">
                            <div className="feature-icon">📝</div>
                            <h3 className="feature-title">Step-by-Step Solutions & Explanations</h3>
                            <p className="feature-description">
                                Understand why the bug happened, not just what it is.
                                Get detailed breakdowns of every issue with clear solutions.
                            </p>
                        </div>

                        <div className="feature-card glass-card">
                            <div className="feature-icon">🌐</div>
                            <h3 className="feature-title">Frontend + Backend Debugging Support</h3>
                            <p className="feature-description">
                                Get tailored help for JavaScript, Python, Java, C#, and more.
                                Full-stack debugging at your fingertips.
                            </p>
                        </div>

                        <div className="feature-card glass-card">
                            <div className="feature-icon">📚</div>
                            <h3 className="feature-title">Learn While You Debug</h3>
                            <p className="feature-description">
                                Every error becomes a lesson — with helpful tips, examples,
                                and best practices from industry standards.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Learning Hub Section */}
            <section className="section learning-section">
                <div className="container">
                    <span className="section-badge">📚 Learning Hub Features</span>
                    <h2 className="section-title">Grow Your Skills Every Day</h2>
                    <p className="section-subtitle">
                        Resources designed to make you a better developer
                    </p>

                    <div className="learning-grid">
                        <div className="learning-card">
                            <div className="learning-icon">📝</div>
                            <div className="learning-content">
                                <h3>Coding Tutorials & Articles</h3>
                                <p>Access detailed tutorials on data structures, algorithms, and real code problems.</p>
                            </div>
                        </div>

                        <div className="learning-card">
                            <div className="learning-icon">🧩</div>
                            <div className="learning-content">
                                <h3>Example-Based Explanations</h3>
                                <p>Real problem breakdowns with solutions — ideal for interview prep and skill building.</p>
                            </div>
                        </div>

                        <div className="learning-card">
                            <div className="learning-icon">🚀</div>
                            <div className="learning-content">
                                <h3>Skills Growth Path</h3>
                                <p>Track your progress and build coding confidence with every bug you solve.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Preview Section */}
            <section className="section preview-section">
                <div className="container">
                    <span className="section-badge">👀 Platform Preview</span>
                    <h2 className="section-title">See CodeSage in Action</h2>
                    <p className="section-subtitle">
                        A glimpse of our powerful debugging and analysis tools
                    </p>

                    <div className="preview-grid">
                        <div className="preview-card glass-card">
                            <div className="preview-header">
                                <span className="preview-badge">Debugger</span>
                                <div className="preview-dots">
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                            <div className="preview-image">
                                <img
                                    src="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=400&fit=crop"
                                    alt="Debugger Page Preview"
                                />
                                <div className="preview-overlay">
                                    <p>Paste your code, get instant AI diagnosis, and see highlighted fixes</p>
                                </div>
                            </div>
                        </div>

                        <div className="preview-card glass-card">
                            <div className="preview-header">
                                <span className="preview-badge">Analysis</span>
                                <div className="preview-dots">
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                            <div className="preview-image">
                                <img
                                    src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop"
                                    alt="Analysis Page Preview"
                                />
                                <div className="preview-overlay">
                                    <p>Track your progress, see common mistakes, and improve over time</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Why Choose Us Section */}
            <section className="section why-section">
                <div className="container">
                    <span className="section-badge">🤖 Why Choose Us</span>
                    <h2 className="section-title">Built for Serious Developers</h2>
                    <p className="section-subtitle">
                        More than just a debugger — a complete learning ecosystem
                    </p>

                    <div className="why-grid">
                        <div className="why-card">
                            <div className="why-check">✔</div>
                            <div className="why-content">
                                <h4>AI Insights, Not Just Spellchecks</h4>
                                <p>The system explains logic, not just syntax errors</p>
                            </div>
                        </div>

                        <div className="why-card">
                            <div className="why-check">✔</div>
                            <div className="why-content">
                                <h4>Interactive Debugging</h4>
                                <p>For frontend (browser/JS) and backend challenges</p>
                            </div>
                        </div>

                        <div className="why-card">
                            <div className="why-check">✔</div>
                            <div className="why-content">
                                <h4>Real-World Problem Solving</h4>
                                <p>So you code like a professional from day one</p>
                            </div>
                        </div>

                        <div className="why-card">
                            <div className="why-check">✔</div>
                            <div className="why-content">
                                <h4>Trusted Learning Resource</h4>
                                <p>Inspired by platforms that help learners grow from basics to advanced</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="section cta-section">
                <div className="container">
                    <div className="cta-card glass-card">
                        <div className="cta-content">
                            <h2 className="cta-title">Start Debugging Smarter Now</h2>
                            <p className="cta-description">
                                Get instant help from AI & grow your coding skills!
                                Join thousands of developers who are already learning smarter.
                            </p>
                            <div className="cta-buttons">
                                <Link to="/signup" className="btn btn-primary btn-large">
                                    <span>➤</span>
                                    Get Started Free
                                </Link>
                                <Link to="/login" className="btn btn-secondary btn-large">
                                    Already have an account?
                                </Link>
                            </div>
                        </div>
                        <div className="cta-decoration">
                            <div className="decoration-circle"></div>
                            <div className="decoration-circle"></div>
                            <div className="decoration-circle"></div>
                        </div>
                    </div>
                </div>
            </section>

            <Footer />
        </div>
    );
};

export default Home;
