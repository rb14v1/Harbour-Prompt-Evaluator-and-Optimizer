import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import EvaluationForm from './components/EvaluationForm';
import SummaryCards from './components/SummaryCards';
import DimensionsTable from './components/DimensionsTable';
import SyntheticDatasetView from './components/SyntheticDatasetView';
import PromptComparison from './components/PromptComparison';
import HistoryModal from './components/HistoryModal';
import { Database, BarChart3, Split, Cpu } from 'lucide-react';

const PIPELINE_STEPS = [
  { id: 'prep', label: 'Preprocessor Agent', desc: 'Cleaning & Normalizing' },
  { id: 'analyze', label: 'Analyzer Agent', desc: 'Extracting Semantics & Requirements' },
  { id: 'eval', label: 'Evaluator Agent', desc: '15-Dimension Quality Scoring' },
  { id: 'gen', label: 'Synthetic Generator Agent', desc: 'Synthesizing Test Cases' },
  { id: 'opt', label: 'Improver Agent', desc: 'Injecting Guardrails & Restructuring' },
  { id: 'val', label: 'Validator Agent', desc: 'Quality Checking & Repairing' },
  { id: 'reeval', label: 'Re-Validator Agent', desc: 'Independent Re-Scoring' },
];

export default function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('prompt_optimizer_theme') || 'dark';
  });

  const [department, setDepartment] = useState('');
  const [taskType, setTaskType] = useState('');
  const [prompt, setPrompt] = useState('');
  const [datasetSize, setDatasetSize] = useState(5);

  const [isLoading, setIsLoading] = useState(false);
  const [stepStatus, setStepStatus] = useState({});
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const [activeTab, setActiveTab] = useState('comparison');
  const [isExporting, setIsExporting] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Sync theme with document attribute & localStorage
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('prompt_optimizer_theme', theme);
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleEvaluate = async (e) => {
    if (e) e.preventDefault();
    if (!prompt.trim() || !department.trim() || !taskType.trim()) return;

    setIsLoading(true);
    setError(null);
    setStepStatus({});

    try {
      const payload = {
        department: department.trim(),
        task_type: taskType.trim(),
        prompt: prompt.trim(),
        dataset_size: datasetSize
      };

      let res;
      try {
        res = await fetch('/api/evaluate/stream/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } catch (e) {
        res = null;
      }

      // Fallback to direct backend URL if proxy fails
      if (!res || !res.ok) {
        try {
          const directRes = await fetch('http://127.0.0.1:8000/api/evaluate/stream/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          if (directRes.ok) {
            res = directRes;
          }
        } catch (directErr) {
          // keep original res
        }
      }

      if (!res || !res.ok) {
        const errData = res ? await res.json().catch(() => ({})) : {};
        throw new Error(errData.error || `Evaluation failed with status ${res ? res.status : 'Network Error'}`);
      }

      let finalData = null;
      const handleLine = (line) => {
        if (!line.trim()) return;
        const event = JSON.parse(line);
        if (event.event === 'start') {
          setStepStatus((prev) => ({ ...prev, [event.step]: 'running' }));
        } else if (event.event === 'done') {
          setStepStatus((prev) => ({ ...prev, [event.step]: 'done' }));
        } else if (event.event === 'result') {
          finalData = event.data;
        } else if (event.event === 'error') {
          throw new Error(event.error);
        }
      };

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();
        lines.forEach(handleLine);
      }
      buffer += decoder.decode();
      buffer.split('\n').forEach(handleLine);

      if (!finalData) {
        throw new Error('Evaluation ended before a result was returned');
      }

      setResult(finalData);
      setActiveTab('comparison');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportExcel = async () => {
    if (!result) return;
    setIsExporting(true);
    try {
      if (result.id) {
        window.open(`http://127.0.0.1:8000/api/evaluations/${result.id}/export-excel/`, '_blank');
      } else {
        let res = await fetch('/api/export-excel/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(result)
        }).catch(() => null);

        if (!res || !res.ok) {
          res = await fetch('http://127.0.0.1:8000/api/export-excel/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(result)
          });
        }

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Prompt_Evaluation_${result.prompt_id || 'REPORT'}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    } finally {
      setTimeout(() => setIsExporting(false), 1000);
    }
  };

  const handleSelectHistoryItem = (item) => {
    setResult({
      ...item,
      test_case_validation: item.test_case_validation_json
    });
    setIsHistoryOpen(false);
    setActiveTab('comparison');
  };

  return (
    <div className="app-container">
      {/* Top Navbar with Day/Dark mode switch */}
      <Header
        onExportExcel={handleExportExcel}
        hasResult={!!result}
        isExporting={isExporting}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        onOpenHistory={() => setIsHistoryOpen(true)}
      />

      {/* Main Studio Input Form */}
      <EvaluationForm
        department={department}
        setDepartment={setDepartment}
        taskType={taskType}
        setTaskType={setTaskType}
        prompt={prompt}
        setPrompt={setPrompt}
        onSubmit={handleEvaluate}
        isLoading={isLoading}
      />

      {/* Visual Agent Execution Pipeline during Execution */}
      {isLoading && (
        <div className="stepper-container">
          <div className="stepper-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Cpu size={20} color="#6366f1" />
              <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-main)' }}>
                Multi-Agent Execution Pipeline
              </h3>
            </div>
            <span style={{ fontSize: '0.8rem', color: '#818cf8', fontWeight: 700 }}>
              {PIPELINE_STEPS.filter((s) => stepStatus[s.id] === 'done').length} of {PIPELINE_STEPS.length} completed
            </span>
          </div>

          <div className="stepper-nodes">
            {PIPELINE_STEPS.map((step) => {
              const isActive = stepStatus[step.id] === 'running';
              const isDone = stepStatus[step.id] === 'done';

              return (
                <div
                  key={step.id}
                  className={`stepper-node ${isActive ? 'active' : ''} ${isDone ? 'completed' : ''}`}
                >
                  <div style={{ fontSize: '0.7rem', color: isDone ? '#10b981' : (isActive ? '#818cf8' : 'var(--text-muted)'), fontWeight: 700 }}>
                    {isDone ? 'COMPLETED' : (isActive ? 'PROCESSING...' : 'WAITING')}
                  </div>
                  <div className="stepper-node-title">{step.label}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {step.desc}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="error-banner" style={{ borderRadius: '12px', padding: '16px 20px', marginBottom: '28px', display: 'flex', alignItems: 'flex-start', gap: '12px', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#f43f5e' }}>
          <div style={{ marginTop: '2px' }}>
            <AlertCircle size={20} color="#f43f5e" />
          </div>
          <div style={{ flex: 1 }}>
            <strong style={{ fontSize: '0.95rem' }}>Evaluation Error</strong>
            <p style={{ fontSize: '0.875rem', marginTop: '4px', color: 'rgba(244, 63, 94, 0.8)' }}>{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            style={{ background: 'none', border: 'none', color: '#f43f5e', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '0 4px' }}
            title="Dismiss"
          >
            <X size={18} />
          </button>
        </div>
      )}

      {/* Evaluation Results Suite */}
      {result && (
        <div>
          {/* KPI Score Cards */}
          <SummaryCards result={result} />

          {/* Navigation Tabs */}
          <div className="tabs-header">
            <button
              type="button"
              className={`tab-button ${activeTab === 'comparison' ? 'active' : ''}`}
              onClick={() => setActiveTab('comparison')}
            >
              <Split size={18} />
              <span>Original vs Improved Prompt</span>
            </button>

            <button
              type="button"
              className={`tab-button ${activeTab === 'dataset' ? 'active' : ''}`}
              onClick={() => setActiveTab('dataset')}
            >
              <Database size={18} />
              <span>Synthetic Dataset Hub</span>
              <span className="tab-pill-badge">
                {result.synthetic_dataset?.dataset_size || 0}
              </span>
            </button>

            <button
              type="button"
              className={`tab-button ${activeTab === 'dimensions' ? 'active' : ''}`}
              onClick={() => setActiveTab('dimensions')}
            >
              <BarChart3 size={18} />
              <span>15-Dimension Scorecard</span>
            </button>
          </div>

          {/* Active Tab Views */}
          {activeTab === 'comparison' && <PromptComparison result={result} />}
          {activeTab === 'dataset' && <SyntheticDatasetView result={result} />}
          {activeTab === 'dimensions' && <DimensionsTable result={result} />}
        </div>
      )}

      {/* History Modal */}
      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectItem={handleSelectHistoryItem}
      />
    </div>
  );
}
