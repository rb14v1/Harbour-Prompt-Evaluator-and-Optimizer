# Prompt Evaluator Frontend

React + Vite frontend for the Prompt Evaluator and Optimizer system.

## Features

- ✅ Submit and evaluate prompts
- ✅ View detailed evaluation results with 8-dimension scoring
- ✅ Visual score charts (Recharts)
- ✅ Evaluation history and statistics
- ✅ Dark mode toggle
- ✅ Responsive design (Tailwind CSS)
- ✅ Auto-improvement suggestions
- ✅ Real-time API integration

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icons

## Quick Start

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Update VITE_API_URL if backend is on different URL
# Default: http://localhost:8000/api
```

### Development

```bash
# Start dev server
npm run dev
```

Server runs at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

Output: `frontend/dist/`

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── Header.jsx       # Navigation header
│   │   ├── Footer.jsx       # Footer
│   │   ├── PromptForm.jsx   # Prompt input form
│   │   ├── EvaluationResult.jsx  # Results display
│   │   ├── ScoreCard.jsx    # Score badge
│   │   ├── DimensionChart.jsx    # Score chart
│   │   └── LoadingSpinner.jsx    # Loading indicator
│   ├── pages/               # Page components
│   │   ├── Home.jsx         # Home/evaluation page
│   │   ├── Results.jsx      # Results detail page
│   │   ├── History.jsx      # Evaluation history
│   │   └── About.jsx        # About page
│   ├── services/            # API integration
│   │   └── api.js           # Axios client
│   ├── App.jsx              # Main app component
│   ├── App.css              # App styles
│   ├── index.css            # Global styles (Tailwind)
│   └── main.jsx             # React entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
├── postcss.config.js        # PostCSS configuration
├── package.json             # Dependencies
├── .env.example             # Environment template
└── README.md               # This file
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

### Tailwind CSS

Configured in `tailwind.config.js` with:
- Custom colors (primary, success, warning, danger)
- Dark mode support
- Utility classes

### Vite Config

- Dev server port: 5173
- Build output: `dist/`
- React Fast Refresh enabled

## API Integration

### Available Endpoints

- `POST /evaluations/evaluate/` - Evaluate single prompt
- `POST /evaluations/batch_evaluate/` - Batch evaluation
- `GET /history/` - Get evaluation history
- `GET /history/stats/` - Get statistics
- `GET /evaluations/{id}/detail/` - Get evaluation details

### API Service

Located in `src/services/api.js`:

```javascript
import { evaluationAPI } from '@/services/api'

// Evaluate prompt
const result = await evaluationAPI.evaluatePrompt('Your prompt')

// Get history
const history = await evaluationAPI.getHistory()

// Get stats
const stats = await evaluationAPI.getStats()
```

## Components

### PromptForm
- Text input for prompts
- Submit button with loading state
- Error display
- Calls `/api/evaluations/evaluate/`

### EvaluationResult
- Displays full evaluation results
- Shows original vs improved prompt
- Score cards with visualizations
- Dimension chart using Recharts
- Improvement history timeline

### DimensionChart
- Bar chart of 8 dimensions
- Uses Recharts library
- Responsive container
- Interactive tooltips

### ScoreCard
- Circular badge showing score
- Color-coded (red/yellow/green/blue)
- Progress bar
- Supporting text

## Styling

### Tailwind CSS

Configured with dark mode support:

```jsx
<div className="dark:bg-gray-800 bg-white">
  Dark mode aware component
</div>
```

### Custom Classes

Added in `src/index.css`:

```css
.btn, .btn-primary, .btn-secondary
.card
.input, .label
.spinner
.score-badge
```

### Dark Mode Toggle

Store in localStorage:

```javascript
const [darkMode, setDarkMode] = useState(() => {
  const saved = localStorage.getItem('darkMode')
  return saved ? JSON.parse(saved) : false
})
```

## Pages

### Home Page
- Hero section with features
- Prompt evaluation form
- Feature highlights
- How it works guide

### Results Page
- Display full evaluation
- Show improvement history
- View dimension charts
- Compare original vs improved

### History Page
- List all past evaluations
- Display statistics
- Quick status view
- Click to view details

### About Page
- Project information
- How it works explanation
- Technology stack
- Dimension descriptions

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Other Platforms

1. Build: `npm run build`
2. Upload `dist/` folder to hosting
3. Configure routing (SPA mode)
4. Set environment variables

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### API Connection Error

```
Check:
1. Backend running: http://localhost:8000/api/health/
2. VITE_API_URL in .env is correct
3. Backend CORS allows frontend origin
```

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Dark Mode Not Working

Ensure `dark` class is toggled on `<html>` element:

```javascript
if (darkMode) {
  document.documentElement.classList.add('dark')
} else {
  document.documentElement.classList.remove('dark')
}
```

## Performance Tips

- Use React DevTools Profiler
- Code splitting via React Router
- Image optimization
- Lazy load components if needed

## Contributing

1. Follow existing code style
2. Use Tailwind classes for styling
3. Keep components focused and reusable
4. Add comments for complex logic
5. Test in both light and dark modes

## License

Same as backend project

## Support

- Backend URL: http://localhost:8000
- API Docs: Check backend README
- Issues: Report in GitHub

---

**Ready to start?**

```bash
npm install
npm run dev
```

Visit: `http://localhost:5173`
