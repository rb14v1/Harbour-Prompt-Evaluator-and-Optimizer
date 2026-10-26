import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle, Lightbulb, CheckCircle2, SlidersHorizontal } from 'lucide-react';

export default function DimensionsTable({ result }) {
  if (!result) return null;

  const origDims = result.evaluation?.dimensions || {};
  const impDims = result.re_evaluation?.dimensions || {};
  const compDims = result.comparison?.dimensions_comparison || {};

  const [expandedKey, setExpandedKey] = useState(null);
  const [filterScore, setFilterScore] = useState('ALL');

  const toggleExpand = (key) => {
    setExpandedKey(expandedKey === key ? null : key);
  };

  const getBadgeClass = (score) => {
    if (score >= 8) return 'score-green';
    if (score >= 5) return 'score-amber';
    return 'score-red';
  };

  const getBarFillColor = (score) => {
    if (score >= 8) return '#10b981';
    if (score >= 5) return '#f59e0b';
    return '#f43f5e';
  };

  const dimKeys = Object.keys(origDims);

  const filteredKeys = dimKeys.filter((key) => {
    const s = origDims[key]?.score ?? 5;
    if (filterScore === 'WEAK') return s < 6;
    if (filterScore === 'STRONG') return s >= 8;
    return true;
  });

  return (
    <div className="section-panel">
      <div className="panel-title">
        <div>
          <span>15-Dimension Prompt Quality Matrix</span>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', fontWeight: 500, marginTop: '2px' }}>
            Comprehensive architectural evaluation across all 15 industry dimensions (0–10 standard scale)
          </p>
        </div>

        {/* Filter Score Buttons */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {[
            { id: 'ALL', label: `All (${dimKeys.length})` },
            { id: 'WEAK', label: `Needs Improvement (<6)` },
            { id: 'STRONG', label: `Optimized (≥8)` },
          ].map((flt) => (
            <button
              key={flt.id}
              type="button"
              className={`diff-btn ${filterScore === flt.id ? 'active' : ''}`}
              onClick={() => setFilterScore(flt.id)}
            >
              {flt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="dimensions-grid">
        {filteredKeys.map((key) => {
          const item = origDims[key];
          const impItem = impDims[key] || {};
          const compItem = compDims[key] || {};
          const isExpanded = expandedKey === key;
          const origScore = item.score ?? 5;
          const impScore = impItem.score ?? origScore;
          const delta = compItem.difference ?? (impScore - origScore);

          return (
            <div key={key} className="dimension-card" onClick={() => toggleExpand(key)} style={{ cursor: 'pointer' }}>
              <div className="dim-header">
                <span className="dim-title">{item.name || key.replace(/_/g, ' ')}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className={`score-badge ${getBadgeClass(origScore)}`}>
                    {origScore} / 10
                  </span>
                  {delta > 0 && (
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10b981', background: 'rgba(16,185,129,0.16)', padding: '3px 8px', borderRadius: '4px' }}>
                      +{delta}
                    </span>
                  )}
                  {isExpanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="dim-progress-track">
                <div
                  className="dim-progress-fill"
                  style={{
                    width: `${origScore * 10}%`,
                    background: getBarFillColor(origScore),
                  }}
                />
              </div>

              <p className="dim-reasoning">{item.reasoning}</p>

              {item.identified_issue && item.identified_issue !== "No critical issue detected." && (
                <div className="dim-issue">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 700, marginBottom: '2px' }}>
                    <AlertCircle size={13} />
                    <span>Identified Issue:</span>
                  </div>
                  {item.identified_issue}
                </div>
              )}

              {item.recommendation && (
                <div className="dim-rec">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 700, marginBottom: '2px' }}>
                    <Lightbulb size={13} />
                    <span>Recommendation:</span>
                  </div>
                  {item.recommendation}
                </div>
              )}

              {isExpanded && impItem && (
                <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#34d399', display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <CheckCircle2 size={14} />
                      Optimized Re-evaluation Score:
                    </span>
                    <span className="score-badge score-green">
                      {impScore} / 10
                    </span>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    {impItem.reasoning || "Elevated following structured optimization and explicit schema/constraints injection."}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
