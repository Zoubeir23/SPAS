import { useState } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import GraphiqueLignes from '@/components/charts/GraphiqueLignes'
import GraphiqueBarres from '@/components/charts/GraphiqueBarres'
import { exportToExcel, exportDashboardToPDF, type ExportColumn } from '@/utils/exportService'

export default function AnalysesAvancees() {
  const [startDate, setStartDate] = useState('2023-09-01')
  const [endDate, setEndDate] = useState('2024-06-30')

  const [dropoutData] = useState([
    { month: 'Sep', predicted: 3.2, real: 3.1 },
    { month: 'Oct', predicted: 3.5, real: 3.3 },
    { month: 'Nov', predicted: 3.8, real: 3.6 },
    { month: 'Déc', predicted: 4.0, real: 3.9 },
    { month: 'Jan', predicted: 4.2, real: 4.1 },
    { month: 'Fév', predicted: 4.5, real: 4.3 },
    { month: 'Mar', predicted: 4.3, real: 4.2 },
    { month: 'Avr', predicted: 4.1, real: 4.0 },
    { month: 'Mai', predicted: 3.9, real: 3.8 },
    { month: 'Juin', predicted: 3.7, real: 3.6 },
  ])

  const [performanceByProgram] = useState([
    { program: 'Data Science', success: 85, risk: 12, dropout: 3 },
    { program: 'Informatique', success: 78, risk: 18, dropout: 4 },
    { program: 'Cybersécurité', success: 82, risk: 15, dropout: 3 },
    { program: 'IA', success: 88, risk: 10, dropout: 2 },
  ])

  const [interventionEfficacy] = useState([
    { type: 'Soutien Psychologique', students: 45, gpaImpact: '+0.5 pts', retention: '+15%', efficacy: 'Élevée' },
    { type: 'Tutorat par les pairs', students: 120, gpaImpact: '+0.2 pts', retention: '+8%', efficacy: 'Moyenne' },
    { type: 'Atelier de Méthodologie', students: 85, gpaImpact: '+0.8 pts', retention: '+12%', efficacy: 'Élevée' },
    { type: 'Rappel Automatique SMS', students: 350, gpaImpact: '0.0 pts', retention: '+1%', efficacy: 'Faible' },
  ])

  const handleExportPDF = () => {
    const kpis = [
      { label: 'Risque de Décrochage Global', value: '4.2%' },
      { label: 'Interventions Actives', value: '128' },
      { label: 'Précision Modèle IA', value: '94.8%' },
    ]

    const interventionColumns: ExportColumn[] = [
      { key: 'type', label: 'Type d\'Intervention' },
      { key: 'students', label: 'Nombre d\'Étudiants' },
      { key: 'gpaImpact', label: 'Impact Moyen (GPA)' },
      { key: 'retention', label: 'Rétention' },
      { key: 'efficacy', label: 'Efficacité' },
    ]

    const dropoutColumns: ExportColumn[] = [
      { key: 'month', label: 'Mois' },
      { key: 'predicted', label: 'Prédit (IA)', format: (v) => `${v}%` },
      { key: 'real', label: 'Réel', format: (v) => `${v}%` },
    ]

    exportDashboardToPDF(
      {
        title: 'Rapport Analytics Avancées',
        kpis,
        tables: [
          {
            title: 'Efficacité des Interventions',
            data: interventionEfficacy,
            columns: interventionColumns,
          },
          {
            title: 'Taux de Décrochage Prédit vs Réel',
            data: dropoutData,
            columns: dropoutColumns,
          },
        ],
        charts: [
          {
            title: 'Taux de Décrochage Prédit vs Réel',
            description: 'Comparaison sur l\'année académique en cours',
          },
          {
            title: 'Performance par Filière',
            description: 'Répartition des taux de réussite, risque et décrochage',
          },
        ],
      },
      `analytics-avancees-${new Date().toISOString().split('T')[0]}`
    )
  }

  const handleExportExcel = () => {
    const interventionColumns: ExportColumn[] = [
      { key: 'type', label: 'Type d\'Intervention' },
      { key: 'students', label: 'Nombre d\'Étudiants' },
      { key: 'gpaImpact', label: 'Impact Moyen (GPA)' },
      { key: 'retention', label: 'Rétention' },
      { key: 'efficacy', label: 'Efficacité' },
    ]

    exportToExcel(
      interventionEfficacy,
      interventionColumns,
      `rapport-analytics-${new Date().toISOString().split('T')[0]}`,
      'Efficacité Interventions'
    )
  }

  return (
    <MiseEnPagePrincipale title="Analytics Avancées">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Breadcrumbs */}
        <nav className="mb-4 flex items-center text-sm font-medium text-gray-600 dark:text-gray-400">
          <button className="hover:text-primary transition-colors">Accueil</button>
          <span className="mx-2 text-gray-400">/</span>
          <span className="text-primary font-semibold">Analytics Avancées</span>
        </nav>

        {/* Page Heading & Date Filters */}
        <div className="mb-8 flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-gray-900 dark:text-white">
              Analytics Avancées
            </h1>
            <p className="text-base text-gray-600 dark:text-gray-400">
              Suivi des performances académiques et prédictions IA en temps réel.
            </p>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
                Période du
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
                  calendar_today
                </span>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="h-10 w-40 rounded-lg border border-gray-200 bg-white px-3 pl-10 text-sm font-medium text-gray-900 focus:border-primary focus:ring-1 focus:ring-primary dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">au</label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
                  event
                </span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="h-10 w-40 rounded-lg border border-gray-200 bg-white px-3 pl-10 text-sm font-medium text-gray-900 focus:border-primary focus:ring-1 focus:ring-primary dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
            <Bouton className="mb-[1px]">
              <span className="material-symbols-outlined text-lg">filter_list</span>
              Appliquer
            </Bouton>
          </div>
        </div>

        {/* KPI Cartes Row */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {/* KPI 1 */}
          <Carte>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Risque de Décrochage Global
              </h3>
              <span className="rounded-full bg-red-100 p-1.5 text-red-600 dark:bg-red-900/30 dark:text-red-400">
                <span className="material-symbols-outlined text-sm font-bold">trending_up</span>
              </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">4.2%</p>
              <span className="text-sm font-medium text-red-500">+0.8%</span>
            </div>
            <p className="mt-1 text-xs text-gray-600 dark:text-gray-500">vs mois dernier</p>
          </Carte>

          {/* KPI 2 */}
          <Carte>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Interventions Actives
              </h3>
              <span className="rounded-full bg-primary/20 p-1.5 text-primary">
                <span className="material-symbols-outlined text-sm font-bold">psychology</span>
              </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">128</p>
              <span className="text-sm font-medium text-green-600">+12%</span>
            </div>
            <p className="mt-1 text-xs text-gray-600 dark:text-gray-500">vs mois dernier</p>
          </Carte>

          {/* KPI 3 */}
          <Carte>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Précision Modèle IA
              </h3>
              <span className="rounded-full bg-green-100 p-1.5 text-green-600 dark:bg-green-900/30 dark:text-green-400">
                <span className="material-symbols-outlined text-sm font-bold">auto_awesome</span>
              </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">94.8%</p>
              <span className="text-sm font-medium text-green-600">+1.2%</span>
            </div>
            <p className="mt-1 text-xs text-gray-600 dark:text-gray-500">Score F1</p>
          </Carte>
        </div>

        {/* Main Chart: Dropout Rate */}
        <Carte className="lg:col-span-8">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                Taux de Décrochage Prédit vs Réel
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Comparaison sur l'année académique en cours
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-primary"></span>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Prédit (IA)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-green-600"></span>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Réel</span>
              </div>
            </div>
          </div>
          <GraphiqueLignes
            data={dropoutData}
            dataKey="month"
            lines={[
              { key: 'predicted', name: 'Prédit (IA)', color: '#7c3bed' },
              { key: 'real', name: 'Réel', color: '#16A34A' },
            ]}
            height={300}
          />
        </Carte>

        {/* Performance by Program */}
        <Carte>
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Performance par Filière
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Répartition des taux de réussite, risque et décrochage
            </p>
          </div>
          <GraphiqueBarres
            data={performanceByProgram}
            bars={[
              { key: 'success', name: 'Réussite', color: '#16A34A' },
              { key: 'risk', name: 'À risque', color: '#F59E0B' },
              { key: 'dropout', name: 'Décrochage', color: '#DC2626' },
            ]}
            xAxisKey="program"
            height={300}
          />
        </Carte>

        {/* Additional Analytics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Distribution */}
          <Carte>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              Distribution des Risques
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Faible</span>
                  <span className="font-semibold text-gray-900 dark:text-white">65%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div className="bg-green-500 h-3 rounded-full" style={{ width: '65%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Moyen</span>
                  <span className="font-semibold text-gray-900 dark:text-white">25%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div className="bg-amber-500 h-3 rounded-full" style={{ width: '25%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Élevé</span>
                  <span className="font-semibold text-gray-900 dark:text-white">8%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div className="bg-red-500 h-3 rounded-full" style={{ width: '8%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Critique</span>
                  <span className="font-semibold text-gray-900 dark:text-white">2%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div className="bg-red-700 h-3 rounded-full" style={{ width: '2%' }}></div>
                </div>
              </div>
            </div>
          </Carte>

          {/* Intervention Effectiveness */}
          <Carte>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              Efficacité des Interventions
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">Entretien individuel</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Taux de succès: 78%</p>
                </div>
                <span className="text-2xl font-bold text-green-600">78%</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">Tutorat</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Taux de succès: 65%</p>
                </div>
                <span className="text-2xl font-bold text-green-600">65%</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">Alerte précoce</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Taux de succès: 52%</p>
                </div>
                <span className="text-2xl font-bold text-amber-600">52%</span>
              </div>
            </div>
          </Carte>
        </div>

        {/* Export Buttons */}
        <div className="sticky bottom-4 z-20 mt-8 flex flex-wrap justify-end gap-4 rounded-xl border border-gray-200 bg-white/80 p-4 shadow-lg backdrop-blur-md dark:border-gray-800 dark:bg-gray-900/80">
          <Bouton
            onClick={handleExportPDF}
            variant="outline"
            className="flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-lg">picture_as_pdf</span>
            Générer PDF
          </Bouton>
          <Bouton
            onClick={handleExportExcel}
            className="flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-lg">table_view</span>
            Exporter Rapport Excel
          </Bouton>
        </div>
      </div>
    </MiseEnPagePrincipale>
  )
}
