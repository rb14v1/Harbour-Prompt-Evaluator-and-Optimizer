import React, { useState } from 'react';
import { Copy, Check, Sparkles, CheckCircle2, ArrowRight, Layers, ShieldCheck } from 'lucide-react';

export default function PromptComparison({ result }) {
  if (!result) return null;

  const origPrompt = result.original_prompt || '';
  const impPrompt = result.improved_prompt || '';
  const metadata = result.improvement_metadata || {};
  const changes = metadata.explanation_of_changes || [];
  const sections = metadata.structural_sections_added || [];

  const [copied, setCopied] = useState(false);

  const handleCopyImproved = () => {
    navigator.clipboard.writeText(impPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const origWords = origPrompt.split(/\s+/).filter(Boolean).length;
  const impWords = impPrompt.split(/\s+/).filter(Boolean).length;

  return (
    <div className="section-panel">
      <div className="panel-title">
        <div>
          <span>Prompt Optimization & Architecture Comparison</span>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', fontWeight: 500, marginTop: '2px' }}>
            Side-by-side prompt reconstruction with structured delimiters, schema injection, and guardrails
          </p>
        </div>

        <button
          type="button"
          className="btn btn-success"
          style={{ padding: '8px 18px', fontSize: '0.85rem' }}
          onClick={handleCopyImproved}
        >
          {copied ? (
            <>
              <Check size={16} />
              <span>Copied Improved Prompt!</span>
            </>
          ) : (
            <>
              <Copy size={16} />
              <span>Copy Optimized Prompt</span>
            </>
          )}
        </button>
      </div>

      <div className="comparison-grid">
        {/* Original */}
        <div className="prompt-box">
          <div className="prompt-box-header">
            <span className="prompt-box-title" style={{ color: 'var(--text-secondary)' }}>
              Original Submitted Prompt
            </span>

          </div>
          <div className="prompt-box-content">{origPrompt}</div>
        </div>

        {/* Improved */}
        <div className="prompt-box improved">
          <div className="prompt-box-header">
            <span className="prompt-box-title" style={{ color: '#34d399' }}>
              <Sparkles size={18} color="#34d399" />
              Optimized Production-Ready Prompt
            </span>

          </div>
          <div className="prompt-box-content">{impPrompt}</div>
        </div>
      </div>

      {/* Structural Sections & Engineering Enhancements */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {/* Sections Added */}
        <div style={{ background: 'rgba(0,0,0,0.3)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <h4 style={{ fontSize: '0.875rem', fontWeight: 800, color: '#ffffff', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={16} color="#6366f1" />
            Structural Sections Injected
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {(sections.length > 0 ? sections : [
              "Role & Objective", "Context & Prerequisites", "Step-by-Step Instructions", "Output Schema", "Constraints & Guardrails", "Edge Case Protocol"
            ]).map((sec, idx) => (
              <span key={idx} className="badge-cat" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#a5b4fc', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                {sec}
              </span>
            ))}
          </div>
        </div>

        {/* Changes Applied */}
        <div style={{ background: 'rgba(0,0,0,0.3)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <h4 style={{ fontSize: '0.875rem', fontWeight: 800, color: '#ffffff', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={16} color="#10b981" />
            Architectural Enhancements Applied
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {changes.map((ch, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                <CheckCircle2 size={14} color="#10b981" style={{ marginTop: '2px', flexShrink: 0 }} />
                <span>{ch}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
