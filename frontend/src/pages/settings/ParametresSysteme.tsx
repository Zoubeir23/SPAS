import { useState } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'

export default function ParametresSysteme() {
  const [activeTab, setActiveTab] = useState('ai')
  const [highRiskThreshold, setHighRiskThreshold] = useState(10)
  const [mediumRiskThreshold, setMediumRiskThreshold] = useState(12.5)
  const [dailyPredictions, setDailyPredictions] = useState(true)
  const [autoAlerts, setAutoAlerts] = useState(false)
  const [retrainingFrequency, setRetrainingFrequency] = useState('monthly')

  const tabs = [
    { id: 'general', label: 'Général' },
    { id: 'ai', label: 'IA & Prédictions' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'security', label: 'Sécurité' },
  ]

  return (
    <MiseEnPagePrincipale title="Paramètres Système">
      <div className="mx-auto max-w-4xl flex flex-col gap-6">
        {/* Page Heading */}
        <div className="flex flex-col gap-3">
          <h1 className="text-4xl font-black leading-tight tracking-tight text-gray-900 dark:text-white">
            Paramètres Système
          </h1>
          <p className="text-base text-gray-500 dark:text-gray-400 leading-normal">
            Configurez les paramètres globaux et les modèles d'intelligence artificielle de la plateforme ISI.
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-800">
          <div className="flex gap-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group flex flex-col items-center justify-center border-b-[3px] pb-[13px] pt-4 min-w-fit transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-gray-900 dark:text-white'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-gray-200'
                }`}
              >
                <p className="text-sm font-bold leading-normal tracking-[0.015em]">{tab.label}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'ai' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Risk Thresholds */}
            <div className="lg:col-span-2 space-y-6">
              {/* Risk Thresholds Carte */}
              <Carte>
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-bold leading-tight text-gray-900 dark:text-white">
                      Seuils de Risque
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Définissez les notes seuils (sur 20) pour la classification automatique du risque de décrochage.
                    </p>
                  </div>
                  <span className="material-symbols-outlined text-gray-400" title="Informations">
                    info
                  </span>
                </div>

                {/* High Risk Slider */}
                <div className="mb-8">
                  <div className="flex justify-between items-center mb-2">
                    <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                      <span className="w-2 h-2 rounded-full bg-red-500"></span>
                      Risque Élevé (Prioritaire)
                    </label>
                    <span className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 px-2 py-1 rounded text-xs font-bold">
                      &lt; {highRiskThreshold.toFixed(1)}
                    </span>
                  </div>
                  <div className="relative w-full h-6 flex items-center">
                    <input
                      type="range"
                      min="0"
                      max="20"
                      step="0.5"
                      value={highRiskThreshold}
                      onChange={(e) => setHighRiskThreshold(Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-red-600 focus:ring-0 focus:outline-none"
                    />
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    Les étudiants avec une moyenne inférieure à ce seuil seront marqués en rouge.
                  </p>
                </div>

                {/* Medium Risk Slider */}
                <div className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                      <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                      Risque Moyen (À surveiller)
                    </label>
                    <span className="bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 px-2 py-1 rounded text-xs font-bold">
                      {highRiskThreshold.toFixed(1)} - {mediumRiskThreshold.toFixed(1)}
                    </span>
                  </div>
                  <div className="relative w-full h-6 flex items-center">
                    <input
                      type="range"
                      min={highRiskThreshold}
                      max="20"
                      step="0.5"
                      value={mediumRiskThreshold}
                      onChange={(e) => setMediumRiskThreshold(Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-amber-500 focus:ring-0 focus:outline-none"
                    />
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    Zone d'alerte préventive nécessitant un suivi pédagogique.
                  </p>
                </div>

                {/* Visual Bar */}
                <div className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800">
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider">
                    Aperçu de la distribution
                  </p>
                  <div className="h-4 w-full rounded-full flex overflow-hidden">
                    <div
                      className="h-full bg-red-500"
                      style={{ width: `${(highRiskThreshold / 20) * 100}%` }}
                      title={`Risque Élevé: 0-${highRiskThreshold}`}
                    ></div>
                    <div
                      className="h-full bg-amber-500"
                      style={{ width: `${((mediumRiskThreshold - highRiskThreshold) / 20) * 100}%` }}
                      title={`Risque Moyen: ${highRiskThreshold}-${mediumRiskThreshold}`}
                    ></div>
                    <div
                      className="h-full bg-emerald-500 flex-1"
                      title={`Risque Faible: >${mediumRiskThreshold}`}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-400 mt-2 font-mono">
                    <span>0</span>
                    <span className="pl-14">{highRiskThreshold.toFixed(1)}</span>
                    <span className="pl-4">{mediumRiskThreshold.toFixed(1)}</span>
                    <span>20</span>
                  </div>
                </div>
              </Carte>

              {/* Automation Carte */}
              <Carte>
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-bold leading-tight text-gray-900 dark:text-white">
                      Automatisation & Maintenance
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Gérez la fréquence des analyses et le cycle de vie du modèle prédictif.
                    </p>
                  </div>
                  <span className="material-symbols-outlined text-gray-400">settings_suggest</span>
                </div>
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-gray-900 dark:text-white">
                        Prédictions journalières
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Exécuter le modèle chaque nuit à 03:00.
                      </span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={dailyPredictions}
                        onChange={(e) => setDailyPredictions(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-gray-900 dark:text-white">
                        Alertes automatiques
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Notifier les responsables pédagogiques en cas de changement de risque.
                      </span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={autoAlerts}
                        onChange={(e) => setAutoAlerts(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  <div className="pt-4 border-t border-gray-100 dark:border-gray-800">
                    <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                      Fréquence de ré-entrainement
                    </label>
                    <div className="relative">
                      <select
                        value={retrainingFrequency}
                        onChange={(e) => setRetrainingFrequency(e.target.value)}
                        className="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block p-2.5"
                      >
                        <option value="weekly">Hebdomadaire (Dimanche)</option>
                        <option value="monthly">Mensuel (1er du mois)</option>
                        <option value="quarterly">Trimestriel</option>
                        <option value="manual">Manuel uniquement</option>
                      </select>
                      <span className="absolute right-3 top-3 material-symbols-outlined text-gray-500 text-sm pointer-events-none">
                        expand_more
                      </span>
                    </div>
                  </div>
                </div>
              </Carte>
            </div>

            {/* Right Column: Model Info */}
            <div className="lg:col-span-1">
              <Carte className="bg-primary/5 border-primary/20 dark:bg-primary/10 dark:border-primary/30">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                    <span className="material-symbols-outlined text-primary">psychology</span>
                  </div>
                  <div>
                    <h3 className="text-gray-900 dark:text-white font-bold text-sm">Modèle Actif</h3>
                    <p className="text-primary text-xs font-semibold">ISI-Predict v2.4.1</p>
                  </div>
                </div>
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Type</span>
                    <span className="font-medium text-gray-900 dark:text-white">Random Forest</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Précision</span>
                    <span className="font-medium text-emerald-600">94.2%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">F1-Score</span>
                    <span className="font-medium text-gray-900 dark:text-white">0.892</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Dernière mise à jour</span>
                    <span className="font-medium text-gray-900 dark:text-white">24 Oct 2023</span>
                  </div>
                </div>
                <Bouton variant="outline" className="w-full">
                  Voir les détails
                </Bouton>
              </Carte>
            </div>
          </div>
        )}

        {activeTab === 'general' && (
          <Carte>
            <p className="text-gray-600 dark:text-gray-400">Section Général à implémenter</p>
          </Carte>
        )}

        {activeTab === 'notifications' && (
          <Carte>
            <p className="text-gray-600 dark:text-gray-400">Section Notifications à implémenter</p>
          </Carte>
        )}

        {activeTab === 'security' && (
          <Carte>
            <p className="text-gray-600 dark:text-gray-400">Section Sécurité à implémenter</p>
          </Carte>
        )}
      </div>
    </MiseEnPagePrincipale>
  )
}
