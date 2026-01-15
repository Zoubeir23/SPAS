import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

interface ROCData {
  fpr: number[]
  tpr: number[]
  thresholds?: number[]
  auc: number
}

interface GraphiqueROCProps {
  /** Données de la courbe ROC (fpr, tpr, auc) */
  data?: ROCData
  /** Hauteur du graphique en pixels */
  height?: number
  /** Afficher le seuil optimal */
  showOptimalThreshold?: boolean
}

/**
 * Composant de visualisation de la courbe ROC (Receiver Operating Characteristic).
 *
 * La courbe ROC montre le compromis entre le taux de vrais positifs (TPR/Recall)
 * et le taux de faux positifs (FPR) pour différents seuils de classification.
 *
 * - La ligne diagonale représente un classificateur aléatoire (AUC = 0.5)
 * - Plus la courbe est proche du coin supérieur gauche, meilleur est le modèle
 * - L'aire sous la courbe (AUC) résume la performance globale
 */
export default function GraphiqueROC({
  data,
  height = 350,
  showOptimalThreshold = true,
}: GraphiqueROCProps) {
  // Données de démonstration si aucune donnée fournie
  const defaultData: ROCData = {
    fpr: [0, 0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 1.0],
    tpr: [0, 0.45, 0.65, 0.78, 0.85, 0.9, 0.93, 0.96, 0.98, 0.99, 1.0],
    auc: 0.94,
    thresholds: [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
  }

  const rocData = data || defaultData

  // Transformer les données pour Recharts
  const chartData = rocData.fpr.map((fpr, i) => ({
    fpr: fpr * 100, // Convertir en pourcentage
    tpr: rocData.tpr[i] * 100,
    threshold: rocData.thresholds?.[i] ?? null,
    // Ligne diagonale (classificateur aléatoire)
    random: fpr * 100,
  }))

  // Trouver le point optimal (maximise TPR - FPR, ou Youden's J statistic)
  let optimalIndex = 0
  let maxJ = 0
  rocData.fpr.forEach((fpr, i) => {
    const j = rocData.tpr[i] - fpr
    if (j > maxJ) {
      maxJ = j
      optimalIndex = i
    }
  })

  const optimalPoint = {
    fpr: rocData.fpr[optimalIndex] * 100,
    tpr: rocData.tpr[optimalIndex] * 100,
    threshold: rocData.thresholds?.[optimalIndex] ?? 0.5,
  }

  // Tooltip personnalisé
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Point de la courbe ROC
          </p>
          <div className="space-y-1 text-xs">
            <p className="text-gray-600 dark:text-gray-300">
              <span className="font-medium">Taux Faux Positifs (FPR):</span> {data.fpr.toFixed(1)}%
            </p>
            <p className="text-gray-600 dark:text-gray-300">
              <span className="font-medium">Taux Vrais Positifs (TPR):</span> {data.tpr.toFixed(1)}%
            </p>
            {data.threshold !== null && (
              <p className="text-primary font-medium">Seuil: {data.threshold.toFixed(2)}</p>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full" style={{ height: `${height}px`, minHeight: `${height}px` }}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />

          <XAxis
            dataKey="fpr"
            type="number"
            domain={[0, 100]}
            tickFormatter={value => `${value}%`}
            label={{
              value: 'Taux de Faux Positifs (1 - Spécificité)',
              position: 'insideBottom',
              offset: -5,
              className: 'fill-gray-600 dark:fill-gray-400 text-xs',
            }}
            className="text-xs fill-gray-600 dark:fill-gray-400"
          />

          <YAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={value => `${value}%`}
            label={{
              value: 'Taux de Vrais Positifs (Sensibilité)',
              angle: -90,
              position: 'insideLeft',
              className: 'fill-gray-600 dark:fill-gray-400 text-xs',
            }}
            className="text-xs fill-gray-600 dark:fill-gray-400"
          />

          <Tooltip content={<CustomTooltip />} />

          <Legend
            wrapperStyle={{ paddingTop: '10px' }}
            formatter={value => (
              <span className="text-gray-700 dark:text-gray-300 text-sm">{value}</span>
            )}
          />

          {/* Ligne diagonale (classificateur aléatoire) */}
          <Line
            type="linear"
            dataKey="random"
            stroke="#9CA3AF"
            strokeDasharray="5 5"
            strokeWidth={2}
            dot={false}
            name="Aléatoire (AUC = 0.50)"
            legendType="line"
          />

          {/* Zone sous la courbe ROC */}
          <defs>
            <linearGradient id="colorAUC" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366F1" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          {/* Courbe ROC */}
          <Line
            type="monotone"
            dataKey="tpr"
            stroke="#6366F1"
            strokeWidth={3}
            dot={{ r: 4, fill: '#6366F1', strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 6, fill: '#4F46E5', strokeWidth: 2, stroke: '#fff' }}
            name={`Modèle (AUC = ${rocData.auc.toFixed(2)})`}
            legendType="line"
          />

          {/* Point optimal */}
          {showOptimalThreshold && (
            <ReferenceLine
              x={optimalPoint.fpr}
              stroke="#10B981"
              strokeDasharray="3 3"
              strokeWidth={2}
              label={{
                value: `Seuil optimal: ${optimalPoint.threshold.toFixed(2)}`,
                position: 'top',
                className: 'fill-green-600 text-xs font-medium',
              }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      {/* Légende explicative */}
      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
        <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary"></div>
            <span>
              AUC = <strong className="text-primary">{rocData.auc.toFixed(2)}</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>
              Seuil optimal:{' '}
              <strong className="text-green-600">{optimalPoint.threshold.toFixed(2)}</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span>
              TPR au seuil optimal: <strong>{optimalPoint.tpr.toFixed(1)}%</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span>
              FPR au seuil optimal: <strong>{optimalPoint.fpr.toFixed(1)}%</strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
