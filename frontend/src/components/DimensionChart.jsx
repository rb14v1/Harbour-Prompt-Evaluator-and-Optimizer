import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DimensionChart({ scores }) {
  if (!scores) return null

  const data = Object.entries(scores).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    score: value,
  }))

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-4">Quality Dimensions</h3>
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
          <Bar dataKey="score" fill="#0ea5e9" name="Dimension Score" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
