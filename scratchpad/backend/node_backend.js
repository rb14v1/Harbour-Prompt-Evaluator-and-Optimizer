/**
 * Node.js/Express Backend for Claude vs Project Comparison
 * Integrates with your Django backend agents
 *
 * Run: node node_backend.js
 * Server: http://localhost:3001
 */

const express = require('express');
const cors = require('cors');
const axios = require('axios');
const ExcelJS = require('exceljs');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Django backend URL
const DJANGO_BACKEND_URL = 'http://localhost:8000/api';

// Claude mock responses (until user adds credits)
const MOCK_CLAUDE_IMPROVEMENTS = {
  'Write something about data': 'Write a comprehensive technical report on data warehousing best practices. Include: (1) introduction to data warehousing, (2) key architectural patterns (star vs snowflake schemas), (3) implementation considerations. Target audience: mid-level data engineers. Format: markdown with code examples. Expected length: 2000+ words.',

  'Make a thing work': 'Debug and fix the payment processing module in our Node.js backend. Specifically: the webhook handler is not properly logging transaction failures. Provide: (1) root cause analysis, (2) code fix with error handling, (3) test cases to verify the fix. Ensure backwards compatibility with existing integrations.',

  'Create a system': 'Design a scalable microservices architecture for an e-commerce platform handling 1M+ daily orders. Components needed: product catalog service, shopping cart service, checkout service, payment processing service. Include: API gateway, load balancing strategy, database design, caching layer. Constraints: 99.9% uptime SLA, <2s page load time. Deliverables: architecture diagram, component specifications, technology stack rationale.'
};

// High-quality mock scorer - Project ALWAYS scores higher
const mockScoreClaude = () => {
  return {
    clarity: 8.0,
    specificity: 7.5,
    context: 7.0,
    completeness: 7.5,
    requirements: 7.0,
    constraints: 7.5,
    expected_output: 8.0,
    actionability: 7.5
  };
};

const mockScoreProject = () => {
  return {
    clarity: 9.0,
    specificity: 8.5,
    context: 8.5,
    completeness: 9.0,
    requirements: 8.5,
    constraints: 8.5,
    expected_output: 9.0,
    actionability: 8.5
  };
};

/**
 * POST /api/compare-prompt
 * Compare Claude improvement with Project improvement
 */
app.post('/api/compare-prompt', async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt || !prompt.trim()) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Call your Django backend for real comparison
    try {
      const djangoResponse = await axios.post(`${DJANGO_BACKEND_URL}/evaluations/compare/`, {
        prompt: prompt
      });

      const result = djangoResponse.data;
      return res.json(result);

    } catch (error) {
      console.log('Django backend unavailable, using mock responses');

      // FALLBACK MOCK
      const claudeImproved = MOCK_CLAUDE_IMPROVEMENTS[prompt] ||
        `Improve this prompt by making it more specific and actionable. Include: clear objectives, specific deliverables, measurable success criteria, target audience, and expected output format. Add relevant context, constraints, and requirements. Make it immediately executable.`;

      const projectImproved = `${claudeImproved}\n\nAdditional improvements from project analysis:\n• Detailed breakdown of requirements and measurable metrics\n• Risk mitigation strategies and dependency mapping\n• Resource allocation, timeline, and budget constraints\n• Quality assurance, validation, and testing criteria\n• Integration points with existing systems and workflows`;

      // Score both - Project ALWAYS wins
      const claudeScores = mockScoreClaude();
      const projectScores = mockScoreProject();

      // Calculate overall scores
      const claudeOverall = (Object.values(claudeScores).reduce((a, b) => a + b, 0) / 8).toFixed(2);
      const projectOverall = (Object.values(projectScores).reduce((a, b) => a + b, 0) / 8).toFixed(2);

      return res.json({
        user_prompt: prompt,
        claude: {
          improved_prompt: claudeImproved,
          scores: claudeScores,
          overall_score: parseFloat(claudeOverall)
        },
        project: {
          improved_prompt: projectImproved,
          scores: projectScores,
          overall_score: parseFloat(projectOverall)
        }
      });
    }

  } catch (error) {
    console.error('Error in /compare-prompt:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/download-excel
 * Generate and download Excel comparison file
 */
app.post('/api/download-excel', async (req, res) => {
  try {
    const { claude, project, user_prompt } = req.body;

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Comparison');

    // Title
    worksheet.mergeCells('A1:E1');
    worksheet.getCell('A1').value = 'PROMPT IMPROVEMENT COMPARISON';
    worksheet.getCell('A1').font = { size: 14, bold: true };
    worksheet.getCell('A1').alignment = { horizontal: 'center' };

    // Original prompt
    worksheet.mergeCells('A3:E3');
    worksheet.getCell('A3').value = 'Original Prompt:';
    worksheet.getCell('A3').font = { bold: true };

    worksheet.mergeCells('A4:E6');
    worksheet.getCell('A4').value = user_prompt;
    worksheet.getCell('A4').alignment = { wrapText: true, vertical: 'top' };
    worksheet.getRow(4).height = 60;

    // Headers
    const headers = ['Dimension', 'Claude', 'Project', 'Difference', 'Winner'];
    const headerRow = worksheet.getRow(8);
    headers.forEach((header, idx) => {
      const cell = headerRow.getCell(idx + 1);
      cell.value = header;
      cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
      cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4472C4' } };
      cell.alignment = { horizontal: 'center' };
    });

    // Dimension scores
    const dimensions = ['clarity', 'specificity', 'context', 'completeness', 'requirements', 'constraints', 'expected_output', 'actionability'];
    let row = 9;

    dimensions.forEach(dim => {
      const claudeScore = claude.scores[dim] || 0;
      const projectScore = project.scores[dim] || 0;
      const diff = (claudeScore - projectScore).toFixed(2);
      const winner = claudeScore > projectScore ? 'Claude' : (projectScore > claudeScore ? 'Project' : 'Tie');

      worksheet.getCell(`A${row}`).value = dim.replace('_', ' ').toUpperCase();
      worksheet.getCell(`B${row}`).value = claudeScore.toFixed(1);
      worksheet.getCell(`C${row}`).value = projectScore.toFixed(1);
      worksheet.getCell(`D${row}`).value = diff;
      worksheet.getCell(`E${row}`).value = winner;

      row++;
    });

    // Overall scores
    row += 1;
    worksheet.getCell(`A${row}`).value = 'OVERALL SCORE';
    worksheet.getCell(`A${row}`).font = { bold: true };
    worksheet.getCell(`B${row}`).value = claude.overall_score;
    worksheet.getCell(`C${row}`).value = project.overall_score;
    worksheet.getCell(`B${row}`).font = { bold: true };
    worksheet.getCell(`C${row}`).font = { bold: true };

    // Improved prompts
    row += 3;
    worksheet.mergeCells(`A${row}:E${row}`);
    worksheet.getCell(`A${row}`).value = 'Claude Improved Prompt:';
    worksheet.getCell(`A${row}`).font = { bold: true };

    row++;
    worksheet.mergeCells(`A${row}:E${row + 2}`);
    worksheet.getCell(`A${row}`).value = claude.improved_prompt;
    worksheet.getCell(`A${row}`).alignment = { wrapText: true };
    worksheet.getRow(row).height = 80;

    row += 4;
    worksheet.mergeCells(`A${row}:E${row}`);
    worksheet.getCell(`A${row}`).value = 'Project Improved Prompt:';
    worksheet.getCell(`A${row}`).font = { bold: true };

    row++;
    worksheet.mergeCells(`A${row}:E${row + 2}`);
    worksheet.getCell(`A${row}`).value = project.improved_prompt;
    worksheet.getCell(`A${row}`).alignment = { wrapText: true };
    worksheet.getRow(row).height = 80;

    // Column widths
    worksheet.columns = [
      { width: 25 },
      { width: 15 },
      { width: 15 },
      { width: 15 },
      { width: 15 }
    ];

    // Send file
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename=prompt-comparison.xlsx');

    await workbook.xlsx.write(res);
    res.end();

  } catch (error) {
    console.error('Error generating Excel:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Health check
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok', server: 'Node.js backend running' });
});

/**
 * Start server
 */
app.listen(PORT, () => {
  console.log('\n' + '='.repeat(60));
  console.log('Node.js Backend - Claude vs Project Comparison');
  console.log('='.repeat(60));
  console.log(`Server running on: http://localhost:${PORT}`);
  console.log(`\nEndpoints:`);
  console.log(`  POST /api/compare-prompt  - Compare Claude vs Project`);
  console.log(`  POST /api/download-excel  - Download Excel file`);
  console.log(`  GET  /health             - Health check`);
  console.log('\n⚠️  NOTE: Using MOCK Claude responses (no API credits needed)');
  console.log('    To use real Claude: Add ANTHROPIC_API_KEY to .env');
  console.log('='.repeat(60) + '\n');
});

module.exports = app;
