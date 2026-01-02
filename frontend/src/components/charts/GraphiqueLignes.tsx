import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface LineChartProps {
  data: Array<Record<string, any>>
  dataKey: string
  lines: Array<{ key: string; name: string; color?: string }>
  xAxisKey?: string
  height?: number
}

export default function GraphiqueLignes({
  data,
  dataKey: _dataKey,
  lines,
  xAxisKey = 'name',
  height = 300,
}: LineChartProps) {
  // _dataKey is required by interface but not used directly
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={data}>
        <CartesianGrid strokeDasharray="4 4" stroke="#e2e8f0" />
        <XAxis
          dataKey={xAxisKey}
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
        />
        <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
          }}
        />
        <Legend />
        {lines.map((line) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            name={line.name}
            stroke={line.color || '#1c41a6'}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  )
}

