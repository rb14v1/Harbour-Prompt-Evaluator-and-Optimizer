import React from 'react';
import { Play, Sparkles, Building2, Briefcase, FileText } from 'lucide-react';

const DEPARTMENTS = [
  { value: "Software", label: "Software" },
  { value: "Communication", label: "Communication" },
  { value: "Design", label: "Design" },
  { value: "Engineering", label: "Engineering" },
  { value: "Finance", label: "Finance" },
  { value: "Human resources", label: "Human resources" },
  { value: "Learning and development", label: "Learning and development" },
  { value: "Marketing", label: "Marketing" },
  { value: "Product management", label: "Product management" },
  { value: "Support", label: "Support" },
  { value: "Commercial", label: "Commercial" },
  { value: "Delivery management", label: "Delivery management" },
  { value: "Business analysis", label: "Business analysis" },
];

const TASK_TYPES = [
  { value: "create content", label: "create content" },
  { value: "research", label: "research" },
  { value: "deep research/analysis", label: "deep research/analysis" },
  { value: "plan and Organise", label: "plan and Organise" },
  { value: "ideate/brainstorm", label: "ideate/brainstorm" },
  { value: "summarize/review", label: "summarize/review" },
  { value: "explain/teach", label: "explain/teach" },
  { value: "optimize/improve", label: "optimize/improve" },
];

export default function EvaluationForm({
  department,
  setDepartment,
  taskType,
  setTaskType,
  prompt,
  setPrompt,
  onSubmit,
  isLoading
}) {
  return (
    <div className="form-card">
      <div className="form-header-area">
        <div className="form-title-group">
          <h2>
            <Sparkles size={22} color="#6366f1" />
            <span>Prompt Evaluation & Synthetic Dataset Studio</span>
          </h2>
          <p>
            Select your department and task type from the dropdown options below, then enter your prompt.
          </p>
        </div>
      </div>

      <form onSubmit={onSubmit}>
        <div className="form-grid-row">
          {/* Department Dropdown */}
          <div className="form-group">
            <label className="form-label">
              <Building2 size={15} color="#6366f1" />
              Department
            </label>
            <select
              className="form-select"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              required
            >
              <option value="" disabled>-- Select Department --</option>
              {DEPARTMENTS.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
          </div>

          {/* Task Type Dropdown */}
          <div className="form-group">
            <label className="form-label">
              <Briefcase size={15} color="#8b5cf6" />
              Task Type
            </label>
            <select
              className="form-select"
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              required
            >
              <option value="" disabled>-- Select Task Type --</option>
              {TASK_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Prompt Input */}
        <div className="form-group" style={{ marginBottom: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className="form-label">
              <FileText size={15} color="#ec4899" />
              Prompt Payload to Analyze & Optimize
            </label>

          </div>
          <textarea
            className="form-textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type or paste your prompt here (e.g. Create technical documentation for a JWT authentication system using Node.js and Express)..."
            required
            rows={5}
          />
        </div>

        {/* Submit Action */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '16px' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading || !prompt.trim() || !department.trim() || !taskType.trim()}
            style={{ padding: '13px 32px', fontSize: '0.95rem' }}
          >
            <Play size={18} />
            <span>{isLoading ? 'Evaluating Prompt...' : 'Evaluate Prompt'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
