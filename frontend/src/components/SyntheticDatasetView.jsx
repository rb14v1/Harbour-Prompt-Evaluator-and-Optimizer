import React, { useState, useMemo } from 'react';
import { Search, Database, Copy, Check, Filter, Layers, AlertTriangle, Download, Sparkles } from 'lucide-react';

export default function SyntheticDatasetView({ result }) {
  if (!result) return null;

  const datasets = result.synthetic_datasets?.length
    ? result.synthetic_datasets
    : [{ dataset_index: 1, ...(result.synthetic_dataset || {}), dataset_summary: result.dataset_summary || {} }];

  const [datasetPosition, setDatasetPosition] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [edgeOnly, setEdgeOnly] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [copiedAll, setCopiedAll] = useState(false);

  const current = datasets[datasetPosition] || datasets[0];
  const testCases = current.test_cases || [];
  const summary = current.dataset_summary || {};
  const diffDist = summary.difficulty_distribution || {};
  const catDist = summary.category_distribution || {};
  const totalDatasets = datasets.length;

  const goToDataset = (position) => {
    setDatasetPosition(Math.min(Math.max(position, 0), totalDatasets - 1));
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleCopyAllJSON = () => {
    navigator.clipboard.writeText(JSON.stringify(testCases, null, 2));
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(testCases, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Synthetic_Dataset_${result.prompt_id || 'EXPORT'}_${current.dataset_index || datasetPosition + 1}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const filteredCases = useMemo(() => {
    return testCases.filter((tc) => {
      // Difficulty match
      if (selectedDifficulty !== 'ALL' && tc.difficulty !== selectedDifficulty) {
        return false;
      }
      // Category match
      if (selectedCategory !== 'ALL' && tc.category !== selectedCategory) {
        return false;
      }
      // Edge only
      if (edgeOnly && !tc.edge_case && tc.difficulty !== 'Hard') {
        return false;
      }
      // Search match
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const inId = tc.test_case_id?.toLowerCase().includes(q);
        const inInput = tc.input?.toLowerCase().includes(q);
        const inOutput = tc.expected_output?.toLowerCase().includes(q);
        const inCat = tc.category?.toLowerCase().includes(q);
        const inNotes = tc.notes?.toLowerCase().includes(q);
        return inId || inInput || inOutput || inCat || inNotes;
      }
      return true;
    });
  }, [testCases, searchQuery, selectedDifficulty, selectedCategory, edgeOnly]);

  const categories = Object.keys(catDist);

  return (
    <div className="section-panel">
      <div className="panel-title">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Database size={22} color="#8b5cf6" />
          <span>Prompt-Specific Synthetic Test Cases</span>
          <span className="tab-pill-badge" style={{ background: 'rgba(139, 92, 246, 0.25)', color: '#d8b4fe' }}>
            {testCases.length} Generated Cases
          </span>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ padding: '8px 14px', fontSize: '0.8rem' }}
            onClick={handleCopyAllJSON}
          >
            {copiedAll ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copiedAll ? 'Copied All JSON' : 'Copy All JSON'}</span>
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            style={{ padding: '8px 14px', fontSize: '0.8rem' }}
            onClick={handleExportJSON}
          >
            <Download size={14} />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Dataset Navigator */}
      {totalDatasets > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', margin: '12px 0' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ padding: '6px 12px', fontSize: '0.8rem' }}
            onClick={() => goToDataset(datasetPosition - 1)}
            disabled={datasetPosition === 0}
          >
            Previous
          </button>
          <select
            value={datasetPosition}
            onChange={(e) => goToDataset(Number(e.target.value))}
            style={{ padding: '6px 10px', fontSize: '0.8rem' }}
          >
            {datasets.map((ds, pos) => (
              <option key={ds.dataset_index ?? pos} value={pos}>
                Dataset {ds.dataset_index ?? pos + 1} of {totalDatasets}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ padding: '6px 12px', fontSize: '0.8rem' }}
            onClick={() => goToDataset(datasetPosition + 1)}
            disabled={datasetPosition === totalDatasets - 1}
          >
            Next
          </button>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {totalDatasets} datasets generated from this prompt
          </span>
        </div>
      )}

      {/* Dataset Summary Banner */}
      <div className="dataset-summary-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)' }}>TIER DISTRIBUTION:</span>
          <span className="badge-easy">Easy: {diffDist.Easy || 0}</span>
          <span className="badge-med">Medium: {diffDist.Medium || 0}</span>
          <span className="badge-hard">Hard: {diffDist.Hard || 0}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)' }}>CATEGORIES:</span>
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              className={`preset-chip ${selectedCategory === cat ? 'active' : ''}`}
              style={{ padding: '2px 8px', fontSize: '0.725rem' }}
              onClick={() => setSelectedCategory(selectedCategory === cat ? 'ALL' : cat)}
            >
              {cat} ({catDist[cat]})
            </button>
          ))}
        </div>
      </div>

      {/* Filters Bar */}
      <div className="dataset-filters">
        <div className="dataset-search-box">
          <Search size={17} className="search-icon-pos" />
          <input
            type="text"
            className="form-input"
            placeholder="Search test case inputs, outputs, domain categories, or edge cases..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Difficulty filter buttons */}
        <div className="difficulty-pill-group">
          {['ALL', 'Easy', 'Medium', 'Hard'].map((diff) => (
            <button
              key={diff}
              type="button"
              className={`diff-btn ${selectedDifficulty === diff ? 'active' : ''}`}
              onClick={() => setSelectedDifficulty(diff)}
            >
              {diff}
            </button>
          ))}
        </div>

        {/* Category Dropdown */}
        <select
          className="form-select"
          style={{ width: '190px', padding: '9px 12px', fontSize: '0.85rem' }}
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value="ALL">All Categories ({categories.length})</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        {/* Edge case toggle */}
        <button
          type="button"
          className={`btn btn-secondary ${edgeOnly ? 'active' : ''}`}
          onClick={() => setEdgeOnly(!edgeOnly)}
          style={{
            borderColor: edgeOnly ? '#8b5cf6' : 'var(--border-medium)',
            background: edgeOnly ? 'rgba(139, 92, 246, 0.25)' : 'rgba(255, 255, 255, 0.05)',
            fontSize: '0.825rem',
            padding: '9px 16px'
          }}
        >
          <AlertTriangle size={15} color={edgeOnly ? '#d8b4fe' : 'var(--text-muted)'} />
          <span>Edge Cases Only</span>
        </button>
      </div>

      {/* Test Cases List */}
      {filteredCases.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '50px 20px', color: 'var(--text-secondary)' }}>
          No synthetic test cases match your filter criteria.
        </div>
      ) : (
        <div className="test-cases-list">
          {filteredCases.map((tc) => {
            const diffClass =
              tc.difficulty === 'Easy'
                ? 'badge-easy'
                : tc.difficulty === 'Hard'
                ? 'badge-hard'
                : 'badge-med';

            return (
              <div key={tc.test_case_id} className="test-case-card">
                <div className="tc-top">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span className="tc-id-badge">{tc.test_case_id}</span>
                    <span className={diffClass}>{tc.difficulty}</span>
                    <span className="badge-cat">{tc.category}</span>
                    {(tc.edge_case || tc.difficulty === 'Hard') && (
                      <span className="badge-edge">Edge Case Resilience</span>
                    )}
                  </div>

                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ padding: '6px 12px', fontSize: '0.775rem' }}
                    onClick={() => handleCopy(tc.test_case_id, `INPUT:\n${tc.input}\n\nEXPECTED OUTPUT:\n${tc.expected_output}`)}
                  >
                    {copiedId === tc.test_case_id ? (
                      <>
                        <Check size={14} color="#10b981" />
                        <span style={{ color: '#10b981' }}>Copied Case</span>
                      </>
                    ) : (
                      <>
                        <Copy size={14} />
                        <span>Copy Test Case</span>
                      </>
                    )}
                  </button>
                </div>

                <div className="tc-body">
                  <div className="tc-block">
                    <div className="tc-block-title">
                      <span>Input Scenario / Payload</span>
                    </div>
                    <div className="tc-block-content">{tc.input}</div>
                  </div>

                  <div className="tc-block">
                    <div className="tc-block-title">
                      <span>Expected Model Output</span>
                    </div>
                    <div className="tc-block-content">{tc.expected_output}</div>
                  </div>
                </div>

                {tc.notes && (
                  <div className="tc-notes">
                    <strong style={{ color: 'var(--text-main)' }}>Validation Criteria:</strong> {tc.notes}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
