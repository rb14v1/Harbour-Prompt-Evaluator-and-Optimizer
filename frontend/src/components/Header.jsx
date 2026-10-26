import React from 'react';
import { Sparkles, FileSpreadsheet, Sun, Moon, History } from 'lucide-react';

export default function Header({ onExportExcel, hasResult, isExporting, theme, onToggleTheme, onOpenHistory }) {
  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="nav-logo-icon">
          <Sparkles size={24} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 className="nav-title">Prompt Engine AI</h1>
            <span className="nav-badge-status">
              <span className="status-dot"></span>
              Backend is active
            </span>
          </div>
          <p className="nav-subtitle">
            Enterprise Prompt Evaluation • Synthetic Dataset Generation • Automated Optimization
          </p>
        </div>
      </div>

      <div className="nav-actions">
        {/* Day / Dark Mode Toggle */}
        <button
          type="button"
          className="theme-toggle-btn"
          onClick={onToggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Day (Light)' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? (
            <>
              <Sun size={15} color="#fbbf24" />
              <span>Day Mode</span>
            </>
          ) : (
            <>
              <Moon size={15} color="#818cf8" />
              <span>Dark Mode</span>
            </>
          )}
        </button>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={onOpenHistory}
          title="View evaluation history"
        >
          <History size={16} />
          <span>Evaluation History</span>
        </button>

        {hasResult && (
          <button
            className="btn btn-success"
            onClick={onExportExcel}
            disabled={isExporting}
            title="Download full Excel Workbook with all sheets"
          >
            <FileSpreadsheet size={16} />
            <span>{isExporting ? 'Generating Report...' : 'Download Excel Report'}</span>
          </button>
        )}
      </div>
    </header>
  );
}
