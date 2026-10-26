import React from 'react';
import { Compass, AlertOctagon, CheckSquare, ShieldAlert, Cpu, Layers, Target, AlertTriangle } from 'lucide-react';

export default function PromptAnalysisView({ result }) {
  if (!result) return null;

  const analysis = result.analysis || {};

  return (
    <div className="section-panel">
      <div className="panel-title">
        <div>
          <span>Prompt Semantics & Requirements Intelligence</span>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', fontWeight: 500, marginTop: '2px' }}>
            Multi-factor breakdown of intent, explicit/implicit dependencies, and risk factors
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '18px' }}>
        {/* Intent & Objective */}
        <div className="dimension-card">
          <div className="dim-header">
            <span className="dim-title" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Target size={16} />
              Core Intent & Objective
            </span>
          </div>
          <p style={{ fontSize: '0.9rem', color: '#ffffff', marginBottom: '10px', fontWeight: 600, lineHeight: 1.5 }}>
            {analysis.prompt_intent}
          </p>
          <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.25)', padding: '10px 12px', borderRadius: '6px' }}>
            <strong style={{ color: 'var(--text-main)' }}>Primary Goal:</strong> {analysis.user_objective}
          </div>
        </div>

        {/* Output Format & Audience */}
        <div className="dimension-card">
          <div className="dim-header">
            <span className="dim-title" style={{ color: '#c084fc', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={16} />
              Target Delivery & Parameters
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Output Format: </span>
              <strong style={{ color: '#ffffff' }}>{analysis.output_format}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Target Audience: </span>
              <strong style={{ color: '#ffffff' }}>{analysis.target_audience}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Complexity Level: </span>
              <span className="badge-cat" style={{ color: '#a5b4fc', background: 'rgba(99,102,241,0.2)' }}>
                {analysis.complexity}
              </span>
            </div>
          </div>
        </div>

        {/* Explicit Requirements */}
        <div className="dimension-card">
          <div className="dim-header">
            <span className="dim-title" style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckSquare size={16} />
              Explicit Requirements
            </span>
          </div>
          <ul style={{ paddingLeft: '18px', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
            {(analysis.explicit_requirements || []).map((req, i) => (
              <li key={`exp-${i}`} style={{ marginBottom: '6px' }}>
                {req}
              </li>
            ))}
          </ul>
        </div>

        {/* Implicit Requirements */}
        <div className="dimension-card">
          <div className="dim-header">
            <span className="dim-title" style={{ color: '#818cf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={16} />
              Implicit Requirements
            </span>
          </div>
          <ul style={{ paddingLeft: '18px', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
            {(analysis.implicit_requirements || []).map((req, i) => (
              <li key={`imp-${i}`} style={{ marginBottom: '6px' }}>
                {req}
              </li>
            ))}
          </ul>
        </div>

        {/* Missing Info & Ambiguities */}
        <div className="dimension-card">
          <div className="dim-header">
            <span className="dim-title" style={{ color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle size={16} />
              Missing Information & Ambiguities
            </span>
          </div>
          <ul style={{ paddingLeft: '18px', fontSize: '0.825rem', color: '#fde68a' }}>
            {(analysis.missing_information || []).map((info, i) => (
              <li key={`info-${i}`} style={{ marginBottom: '5px' }}>
                <strong>Missing:</strong> {info}
              </li>
            ))}
            {(analysis.ambiguities || []).map((amb, i) => (
              <li key={`amb-${i}`} style={{ marginBottom: '5px' }}>
                <strong>Ambiguity:</strong> {amb}
              </li>
            ))}
          </ul>
        </div>

        {/* Failure Modes & Risks */}
        <div className="dimension-card">
          <div className="dim-header">
            <span className="dim-title" style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={16} />
              Potential Failure Modes
            </span>
          </div>
          <ul style={{ paddingLeft: '18px', fontSize: '0.825rem', color: '#fca5a5' }}>
            {(analysis.potential_failure_modes || []).map((fm, i) => (
              <li key={`fm-${i}`} style={{ marginBottom: '6px' }}>
                {fm}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
