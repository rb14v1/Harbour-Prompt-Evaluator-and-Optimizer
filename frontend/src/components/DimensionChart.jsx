import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DimensionChart({ scores }) {
  if (!scores) return null

  const data = Object.entries(scores).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    score: value,
    fill: value < 7.5 ? '#ef4444' : '#10b981', // Red if weak, green if good
    status: value < 7.5 ? 'Weak' : 'Good'
  }))

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">Quality Dimensions</h3>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span>Weak (&lt;7.5)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span>Good (≥7.5)</span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 10]} label={{ value: 'Score', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value) => value.toFixed(2)}
            cursor={{ fill: 'rgba(14, 165, 233, 0.1)' }}
          />
          <Legend />
          <Bar dataKey="score" name="Dimension Score" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
