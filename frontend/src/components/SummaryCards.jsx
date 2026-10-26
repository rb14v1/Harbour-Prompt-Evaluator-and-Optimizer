import React from 'react';
import { Target, TrendingUp, Sparkles, Database, CheckCircle2, ShieldCheck, Zap } from 'lucide-react';

export default function SummaryCards({ result }) {
  if (!result) return null;

  const origScore = result.overall_original_score ?? 0;
  const impScore = result.overall_improved_score ?? 0;
  const diffScore = result.score_difference ?? (impScore - origScore);
  const dsSize = result.synthetic_dataset?.dataset_size ?? 0;
  const edgeCount = result.dataset_summary?.edge_cases_count ?? 0;

  const getScoreColor = (score) => {
    if (score >= 8) return '#10b981';
    if (score >= 5) return '#f59e0b';
    return '#f43f5e';
  };

  return (
    <div className="kpi-grid">
      {/* Original Score */}
      <div className="kpi-card">
        <div className="kpi-info">
          <h4>Original Prompt Score</h4>
          <div className="kpi-value" style={{ color: getScoreColor(origScore) }}>
            {origScore.toFixed(1)} <span style={{ fontSize: '1.05rem', color: 'var(--text-dim)', fontWeight: 600 }}>/ 10</span>
          </div>
          <p className="kpi-subtext">Baseline across 15 dimensions</p>
        </div>
        <div className="kpi-icon-badge" style={{ background: 'rgba(255,255,255,0.05)' }}>
          <Target size={28} color="var(--text-secondary)" />
        </div>
      </div>

      {/* Improved Score */}
      <div className="kpi-card" style={{ borderColor: 'rgba(16, 185, 129, 0.45)', background: 'rgba(6, 78, 59, 0.15)' }}>
        <div className="kpi-info">
          <h4>Optimized Prompt Score</h4>
          <div className="kpi-value" style={{ color: '#34d399' }}>
            {impScore.toFixed(1)} <span style={{ fontSize: '1.05rem', color: 'rgba(52, 211, 153, 0.6)', fontWeight: 600 }}>/ 10</span>
          </div>
          <p className="kpi-subtext" style={{ color: '#34d399' }}>Re-evaluated post-optimization</p>
        </div>
        <div className="kpi-icon-badge" style={{ background: 'rgba(16, 185, 129, 0.2)' }}>
          <Sparkles size={28} color="#34d399" />
        </div>
      </div>

      {/* Score Net Gain */}
      <div className="kpi-card" style={{ borderColor: 'rgba(99, 102, 241, 0.45)', background: 'rgba(99, 102, 241, 0.1)' }}>
        <div className="kpi-info">
          <h4>Quality Net Elevation</h4>
          <div className="kpi-value" style={{ color: '#818cf8' }}>
            {diffScore >= 0 ? `+${diffScore.toFixed(1)}` : diffScore.toFixed(1)}
            <span style={{ fontSize: '1.05rem', color: 'rgba(129, 140, 248, 0.6)', fontWeight: 600 }}> pts</span>
          </div>
          <p className="kpi-subtext">Net gain in clarity & constraints</p>
        </div>
        <div className="kpi-icon-badge" style={{ background: 'rgba(99, 102, 241, 0.2)' }}>
          <TrendingUp size={28} color="#818cf8" />
        </div>
      </div>

      {/* Synthetic Dataset */}
      <div className="kpi-card">
        <div className="kpi-info">
          <h4>Synthetic Test Dataset</h4>
          <div className="kpi-value" style={{ color: '#c084fc' }}>
            {dsSize} <span style={{ fontSize: '1.05rem', color: 'var(--text-dim)', fontWeight: 600 }}>cases</span>
          </div>
          <p className="kpi-subtext">Includes {edgeCount} boundary edge cases</p>
        </div>
        <div className="kpi-icon-badge" style={{ background: 'rgba(168, 85, 247, 0.18)' }}>
          <Database size={28} color="#c084fc" />
        </div>
      </div>
    </div>
  );
}
