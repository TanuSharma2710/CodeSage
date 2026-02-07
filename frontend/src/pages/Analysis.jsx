import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import API_BASE_URL from '../config/apiBaseUrl';
import './Analysis.css';

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const Analysis = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const [errorHistory, setErrorHistory] = useState([]);
    const [dailyErrors, setDailyErrors] = useState([]);
    const [selectedError, setSelectedError] = useState(null);
    const [sessionErrorCounts, setSessionErrorCounts] = useState(null);
    const [loading, setLoading] = useState(true);
    const [loadingCounts, setLoadingCounts] = useState(false);
    const [error, setError] = useState('');
    const [days, setDays] = useState(30);

    // Dynamic thresholds from API
    const [thresholds, setThresholds] = useState({
        mean: 0,
        greenMax: 1,
        yellowMax: 2,
        orangeMax: 3,
        totalErrors: 0
    });

    // Fetch error history (latest to oldest)
    useEffect(() => {
        const fetchErrorHistory = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`${API_BASE_URL}/analysis/error-history?limit=10`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    setErrorHistory(data.errors);
                }
            } catch (err) {
                console.error('Failed to fetch error history:', err);
            }
        };

        fetchErrorHistory();
    }, []);

    // Fetch daily errors for graph
    useEffect(() => {
        const fetchDailyErrors = async () => {
            setLoading(true);
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`${API_BASE_URL}/analysis/daily-errors?days=${days}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    setDailyErrors(data.daily_counts);

                    // Set dynamic thresholds from API response
                    setThresholds({
                        mean: data.mean,
                        greenMax: data.green_max,
                        yellowMax: data.yellow_max,
                        orangeMax: data.orange_max,
                        totalErrors: data.total_errors
                    });
                }
            } catch (err) {
                console.error('Failed to fetch daily errors:', err);
                setError('Failed to load error data');
            } finally {
                setLoading(false);
            }
        };

        fetchDailyErrors();
    }, [days]);

    // Fetch session error counts when an error is selected
    useEffect(() => {
        const fetchSessionErrorCounts = async () => {
            if (!selectedError) {
                setSessionErrorCounts(null);
                return;
            }

            setLoadingCounts(true);
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`${API_BASE_URL}/analysis/session-error-counts/${selectedError.id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    setSessionErrorCounts(data);
                }
            } catch (err) {
                console.error('Failed to fetch session error counts:', err);
            } finally {
                setLoadingCounts(false);
            }
        };

        fetchSessionErrorCounts();
    }, [selectedError]);

    // Navigate to debugger with session data
    const handleStudyNow = async (debugSessionId) => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/analysis/debug-session/${debugSessionId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const sessionData = await response.json();
                // Navigate to debugger with state
                navigate('/debugger', { state: { prefillData: sessionData } });
            }
        } catch (err) {
            console.error('Failed to fetch session data:', err);
        }
    };

    // Get color for error count using dynamic thresholds
    const getCountColor = (count) => {
        if (count <= thresholds.greenMax) return '#22c55e'; // green
        if (count <= thresholds.yellowMax) return '#eab308'; // yellow
        if (count <= thresholds.orangeMax) return '#f97316'; // orange
        return '#ef4444'; // red
    };

    // Map color name to hex for chart
    const colorNameToHex = {
        'green': '#22c55e',
        'yellow': '#eab308',
        'orange': '#f97316',
        'red': '#ef4444'
    };

    // Prepare chart data for error frequency - use colors from API response
    const chartData = {
        labels: dailyErrors.map(d => {
            const date = new Date(d.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }),
        datasets: [{
            label: 'Errors per Day',
            data: dailyErrors.map(d => d.count),
            backgroundColor: dailyErrors.map(d => colorNameToHex[d.color] || '#22c55e'),
            borderColor: '#3b82f6',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 6
        }]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                padding: 12,
                displayColors: false,
                callbacks: {
                    label: (context) => `${context.raw} errors`
                }
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: '#9ca3af',
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: '#9ca3af',
                    stepSize: 1
                }
            }
        }
    };

    // Prepare error type bar chart data for the selected session
    // Show all error types including Logical and Other
    const errorTypes = ['Syntax', 'Runtime', 'Import', 'Type', 'Logical', 'Other'];
    const errorTypeColors = ['#ef4444', '#f59e0b', '#10b981', '#06b6d4', '#8b5cf6', '#6b7280'];

    // Use actual counts from sessionErrorCounts
    const errorTypeChartData = (selectedError && sessionErrorCounts) ? {
        labels: errorTypes,
        datasets: [{
            label: 'Error Count',
            data: [
                sessionErrorCounts.syntax_error_count,
                sessionErrorCounts.runtime_error_count,
                sessionErrorCounts.import_error_count,
                sessionErrorCounts.type_error_count,
                sessionErrorCounts.logical_error_count,
                sessionErrorCounts.other_error_count
            ],
            backgroundColor: errorTypeColors,
            borderRadius: 8,
            barThickness: 28
        }]
    } : null;

    // Calculate max for y-axis dynamically
    const maxCount = sessionErrorCounts ? Math.max(
        sessionErrorCounts.syntax_error_count,
        sessionErrorCounts.runtime_error_count,
        sessionErrorCounts.import_error_count,
        sessionErrorCounts.type_error_count,
        sessionErrorCounts.logical_error_count || 0,
        sessionErrorCounts.other_error_count || 0,
        1  // minimum of 1 to avoid empty chart
    ) : 2;

    const errorTypeChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { color: '#fff', font: { size: 9 }, maxRotation: 45, minRotation: 45 }
            },
            y: {
                beginAtZero: true,
                max: maxCount + 1,
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                ticks: { color: '#9ca3af', stepSize: 1 }
            }
        }
    };

    return (
        <div className="analysis-page">
            <div className="analysis-header">
                <h1>📊 My Coding Performance</h1>
                <p>Track your debugging patterns and improve your coding skills</p>
            </div>

            <div className="analysis-grid">
                {/* Left Panel - Error History */}
                <div className="analysis-panel recurring-errors">
                    <h2>📜 Error History</h2>
                    <p className="panel-subtitle">Latest to Oldest</p>

                    {errorHistory.length === 0 ? (
                        <div className="no-data">
                            <span>🎉</span>
                            <p>No errors recorded yet!</p>
                        </div>
                    ) : (
                        <div className="error-list">
                            {errorHistory.map((err, index) => (
                                <div
                                    key={err.id}
                                    className={`error-item ${selectedError?.id === err.id ? 'selected' : ''}`}
                                    onClick={() => setSelectedError(err)}
                                >
                                    <div className="error-rank">#{index + 1}</div>
                                    <div className="error-info">
                                        <span className="error-name">{err.error_name || err.error_type}</span>
                                        <span className="error-meta">
                                            {err.language} • {new Date(err.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <button
                                        className="btn-study"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleStudyNow(err.id);
                                        }}
                                    >
                                        Debug
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Middle Panel - Error Frequency Graph */}
                <div className="analysis-panel error-graph">
                    <div className="graph-header">
                        <h2>📈 Error Frequency</h2>
                        <div className="period-selector">
                            <button
                                className={days === 7 ? 'active' : ''}
                                onClick={() => setDays(7)}
                            >
                                7D
                            </button>
                            <button
                                className={days === 30 ? 'active' : ''}
                                onClick={() => setDays(30)}
                            >
                                30D
                            </button>
                            <button
                                className={days === 90 ? 'active' : ''}
                                onClick={() => setDays(90)}
                            >
                                90D
                            </button>
                        </div>
                    </div>

                    <div className="color-legend">
                        <span className="legend-item"><span style={{ background: '#22c55e' }}></span> 0-{thresholds.greenMax.toFixed(1)}</span>
                        <span className="legend-item"><span style={{ background: '#eab308' }}></span> {thresholds.greenMax.toFixed(1)}-{thresholds.yellowMax.toFixed(1)}</span>
                        <span className="legend-item"><span style={{ background: '#f97316' }}></span> {thresholds.yellowMax.toFixed(1)}-{thresholds.orangeMax.toFixed(1)}</span>
                        <span className="legend-item"><span style={{ background: '#ef4444' }}></span> {thresholds.orangeMax.toFixed(1)}+</span>
                        <span className="legend-item mean-info">📊 Mean: {thresholds.mean.toFixed(1)}/day</span>
                    </div>

                    <div className="chart-container">
                        {loading ? (
                            <div className="loading">Loading chart...</div>
                        ) : dailyErrors.length > 0 ? (
                            <Line data={chartData} options={chartOptions} />
                        ) : (
                            <div className="no-data">No data available</div>
                        )}
                    </div>
                </div>

                {/* Right Panel - Error Type Breakdown */}
                <div className="analysis-panel language-chart">
                    <h2>📊 Error Type Breakdown</h2>

                    {!selectedError ? (
                        <div className="no-selection">
                            <span>👈</span>
                            <p>Click an error to see its type</p>
                        </div>
                    ) : loadingCounts ? (
                        <div className="loading">Loading error counts...</div>
                    ) : !sessionErrorCounts ? (
                        <div className="no-data">
                            <span>📊</span>
                            <p>No count data available</p>
                        </div>
                    ) : (
                        <>
                            <p className="selected-error-name">{selectedError.error_name || selectedError.error_type}</p>
                            <div className="language-chart-container">
                                <Bar data={errorTypeChartData} options={errorTypeChartOptions} />
                            </div>
                            <button
                                className="btn-study-full"
                                onClick={() => handleStudyNow(selectedError.id)}
                            >
                                📚 Study This Error
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Analysis;
