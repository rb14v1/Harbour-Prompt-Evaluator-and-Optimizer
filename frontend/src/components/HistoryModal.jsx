import React, { useEffect, useState } from 'react';
import { X, FileSpreadsheet, RefreshCw, ArrowRight } from 'lucide-react';
import { API_BASE } from '../config';

export default function HistoryModal({ isOpen, onClose, onSelectItem }) {
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/evaluations/`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setHistoryList(Array.isArray(data) ? data : data.results ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#ffffff' }}>
              Evaluation History & Reports
            </h3>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ padding: '4px 8px', fontSize: '0.75rem' }}
              onClick={fetchHistory}
              title="Refresh"
            >
              <RefreshCw size={13} />
            </button>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ padding: '6px' }}
            onClick={onClose}
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {loading && (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
              Loading past evaluations...
            </div>
          )}

          {error && (
            <div style={{ padding: '16px', background: 'rgba(239,68,68,0.12)', color: '#fca5a5', borderRadius: '8px', marginBottom: '16px' }}>
              Failed to load history: {error}
            </div>
          )}

          {!loading && historyList.length === 0 && (
            <div style={{ textAlign: 'center', padding: '50px 20px', color: 'var(--text-secondary)' }}>
              No evaluations stored yet. Run an evaluation from the studio to start building history.
            </div>
          )}

          {!loading &&
            historyList.map((item) => (
              <div
                key={item.id}
                className="history-item"
                onClick={() => {
                  onSelectItem(item);
                  onClose();
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 800, color: '#818cf8', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>
                      {item.prompt_id}
                    </span>
                    <span className="badge-cat">{item.department}</span>
                    <span className="badge-cat">{item.task_type}</span>
                  </div>
                  <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', maxWidth: '520px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.original_prompt}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span>{item.overall_original_score?.toFixed(1)}</span>
                      <ArrowRight size={12} color="var(--text-dim)" />
                      <span>{item.overall_improved_score?.toFixed(1)}</span>
                    </div>
                    <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                      {item.synthetic_dataset?.dataset_size || 20} test cases
                    </div>
                  </div>

                  <a
                    href={`${API_BASE}/api/evaluations/${item.id}/export-excel/`}
                    className="btn btn-secondary"
                    style={{ padding: '8px 12px', fontSize: '0.8rem' }}
                    onClick={(e) => e.stopPropagation()}
                    title="Download Excel Report"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <FileSpreadsheet size={15} color="#10b981" />
                  </a>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
