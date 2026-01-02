import { ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface GaugeChartProps {
  value: number
  maxValue?: number
  label?: string
  size?: number
  color?: string
}

export default function GraphiqueJauge({
  value,
  maxValue = 100,
  label,
  size = 200,
  color = '#1c41a6',
}: GaugeChartProps) {
  const percentage = Math.min((value / maxValue) * 100, 100)
  const data = [
    { name: 'value', value: percentage },
    { name: 'remaining', value: 100 - percentage },
  ]

  const COLORS = [color, '#e2e8f0']

  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width={size} height={size / 2}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="100%"
            startAngle={180}
            endAngle={0}
            innerRadius={size / 2 - 20}
            outerRadius={size / 2}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 text-center">
        <div className="text-3xl font-bold text-gray-900 dark:text-white">
          {value.toFixed(1)}%
        </div>
        {label && (
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {label}
          </div>
        )}
      </div>
    </div>
  )
}

