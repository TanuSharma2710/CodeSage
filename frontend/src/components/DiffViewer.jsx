import { useState } from 'react';
import './DiffViewer.css';

const DiffViewer = ({ originalCode, fixedCode, changedLines = [] }) => {
    const [copied, setCopied] = useState(false);

    const originalLines = originalCode ? originalCode.split('\n') : [];
    const fixedLines = fixedCode ? fixedCode.split('\n') : [];

    // Convert changed lines to a Set for fast lookup
    const changedLinesSet = new Set(changedLines.map(n => parseInt(n)));

    // Get the corrected lines content for copy
    const getCorrectedLinesText = () => {
        return changedLines
            .map(lineNum => fixedLines[lineNum - 1])
            .filter(line => line !== undefined)
            .join('\n');
    };

    // Copy only corrected lines
    const handleCopyCorrections = async () => {
        const text = getCorrectedLinesText();
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    // Copy full fixed code
    const handleCopyAll = async () => {
        try {
            await navigator.clipboard.writeText(fixedCode);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    return (
        <div className="diff-viewer">
            <div className="diff-header">
                <span className="diff-title">🔧 Fixed Code</span>
                <div className="diff-actions">
                    {changedLinesSet.size > 0 && (
                        <button
                            className="copy-btn copy-corrections"
                            onClick={handleCopyCorrections}
                            title="Copy only corrected lines"
                        >
                            {copied ? '✓ Copied!' : '📋 Copy Fixes'}
                        </button>
                    )}
                    <button
                        className="copy-btn"
                        onClick={handleCopyAll}
                        title="Copy full code"
                    >
                        📄 Copy All
                    </button>
                </div>
            </div>

            <div className="diff-legend-bar">
                <span className="legend-item error">
                    <span className="legend-marker"></span>
                    Error Line
                </span>
                <span className="legend-item fixed">
                    <span className="legend-marker"></span>
                    Corrected Line
                </span>
            </div>

            <div className="diff-content">
                <pre className="code-block">
                    {fixedLines.map((line, index) => {
                        const lineNum = index + 1;
                        const isChanged = changedLinesSet.has(lineNum);
                        const originalLine = originalLines[index] || '';

                        return (
                            <div key={index} className="diff-line-group">
                                {/* Show original error line in red if changed */}
                                {isChanged && originalLine !== line && (
                                    <div className="code-line line-error">
                                        <span className="line-number">{lineNum}</span>
                                        <span className="line-prefix">-</span>
                                        <span className="line-content">{originalLine || ' '}</span>
                                    </div>
                                )}
                                {/* Show fixed line - green if changed */}
                                <div className={`code-line ${isChanged ? 'line-fixed' : ''}`}>
                                    <span className="line-number">{lineNum}</span>
                                    <span className="line-prefix">{isChanged ? '+' : ' '}</span>
                                    <span className="line-content">{line || ' '}</span>
                                    {isChanged && <span className="change-badge">✓ Fixed</span>}
                                </div>
                            </div>
                        );
                    })}
                </pre>
            </div>

            {changedLinesSet.size > 0 && (
                <div className="fixes-summary">
                    <div className="summary-header">
                        <h4>📝 {changedLinesSet.size} line{changedLinesSet.size > 1 ? 's' : ''} corrected</h4>
                        <span className="line-numbers">Lines: {changedLines.join(', ')}</span>
                    </div>
                </div>
            )}

            {changedLinesSet.size === 0 && (
                <div className="no-changes">
                    <p>✅ No changes needed - code looks correct!</p>
                </div>
            )}
        </div>
    );
};

export default DiffViewer;
