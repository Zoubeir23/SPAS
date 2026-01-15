import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts'

interface SHAPFactor {
  feature: string
  value: string | number
  contribution: number
  direction: 'positive' | 'negative'
}

interface GraphiqueSHAPProps {
  /** Facteurs SHAP avec leurs contributions */
  factors: SHAPFactor[]
  /** Hauteur du graphique */
  height?: number
  /** Afficher les valeurs sur les barres */
  showValues?: boolean
  /** Titre du graphique */
  title?: string
}

/**
 * Composant de visualisation SHAP (SHapley Additive exPlanations).
 *
 * SHAP explique les prédictions en montrant la contribution de chaque feature
 * au score de risque final. C'est une méthode d'explicabilité IA basée sur
 * la théorie des jeux (valeurs de Shapley).
 *
 * - Barres rouges : augmentent le risque d'abandon
 * - Barres vertes : diminuent le risque d'abandon
 */
export default function GraphiqueSHAP({
  factors,
  height = 400,
  showValues = true,
  title = 'Impact des facteurs sur le risque',
}: GraphiqueSHAPProps) {
  // Trier par valeur absolue de contribution (plus impactants en haut)
  const sortedFactors = [...factors].sort(
    (a, b) => Math.abs(b.contribution) - Math.abs(a.contribution)
  )

  // Données pour le graphique
  const chartData = sortedFactors.map(factor => ({
    name: factor.feature,
    value: factor.contribution * 100, // En pourcentage
    rawValue: factor.value,
    isPositive: factor.direction === 'positive',
    fill: factor.direction === 'positive' ? '#EF4444' : '#10B981',
  }))

  // Tooltip personnalisé
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-w-xs">
          <p className="font-semibold text-gray-900 dark:text-white mb-2">{data.name}</p>
          <div className="space-y-1 text-sm">
            <p className="text-gray-600 dark:text-gray-300">
              <span className="font-medium">Valeur observée:</span> {data.rawValue}
            </p>
            <p className={data.isPositive ? 'text-red-600' : 'text-green-600'}>
              <span className="font-medium">Impact:</span> {data.value > 0 ? '+' : ''}
              {data.value.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
              {data.isPositive ? "↑ Augmente le risque d'abandon" : "↓ Diminue le risque d'abandon"}
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  // Étiquette personnalisée sur les barres
  const CustomLabel = ({ x, y, width, value }: any) => {
    if (!showValues) return null
    const isPositive = value >= 0
    return (
      <text
        x={isPositive ? x + width + 5 : x + width - 5}
        y={y + 12}
        fill={isPositive ? '#EF4444' : '#10B981'}
        textAnchor={isPositive ? 'start' : 'end'}
        fontSize={11}
        fontWeight={600}
      >
        {value > 0 ? '+' : ''}
        {value.toFixed(1)}%
      </text>
    )
  }

  return (
    <div className="w-full">
      {title && (
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{title}</h4>
      )}

      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 10, right: 80, left: 120, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />

            <XAxis
              type="number"
              domain={[-30, 30]}
              tickFormatter={value => `${value > 0 ? '+' : ''}${value}%`}
              className="text-xs fill-gray-600 dark:fill-gray-400"
            />

            <YAxis
              type="category"
              dataKey="name"
              width={110}
              tick={{ fontSize: 12 }}
              className="fill-gray-700 dark:fill-gray-300"
            />

            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }} />

            {/* Ligne de référence à zéro */}
            <ReferenceLine x={0} stroke="#9CA3AF" strokeWidth={2} />

            <Bar dataKey="value" radius={[4, 4, 4, 4]} label={<CustomLabel />}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Légende */}
      <div className="mt-4 flex flex-wrap items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500"></div>
          <span className="text-gray-600 dark:text-gray-400">Augmente le risque</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-green-500"></div>
          <span className="text-gray-600 dark:text-gray-400">Diminue le risque</span>
        </div>
      </div>

      {/* Explication SHAP */}
      <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-100 dark:border-purple-800">
        <div className="flex items-start gap-3">
          <span className="material-symbols-outlined text-primary text-xl">psychology</span>
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              Explication par SHAP (Shapley Additive Explanations)
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              Ce graphique montre comment chaque facteur contribue au score de risque prédit. Les
              valeurs sont calculées via la théorie des jeux (valeurs de Shapley) pour garantir une
              attribution équitable de l'importance de chaque feature.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
