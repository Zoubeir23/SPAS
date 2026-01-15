import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import ModaleConfirmation from '@/components/common/ModaleConfirmation'
import { settingsService, type SystemSettings } from '@/api/services/settingsService'
import { mlService, type MLModel } from '@/api/services/mlService'
import { ROUTES } from '@/utils/constants'

export default function ParametresSysteme() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('ai')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [resetConfirmation, setResetConfirmation] = useState(false)
  
  // Settings state
  const [_settings, setSettings] = useState<SystemSettings | null>(null)
  
  // Active ML Model
  const [activeModel, setActiveModel] = useState<MLModel | null>(null)
  
  // Derived states for UI (converted from API format)
  const [highRiskThreshold, setHighRiskThreshold] = useState(10)
  const [mediumRiskThreshold, setMediumRiskThreshold] = useState(12.5)
  const [dailyPredictions, setDailyPredictions] = useState(true)
  const [autoAlerts, setAutoAlerts] = useState(false)
  const [retrainingFrequency, setRetrainingFrequency] = useState('monthly')
  
  // General settings
  const [systemLanguage, setSystemLanguage] = useState<'fr' | 'en'>('fr')
  const [systemTimezone, setSystemTimezone] = useState('Africa/Dakar')
  const [systemDateFormat, setSystemDateFormat] = useState('DD/MM/YYYY')
  const [maintenanceMode, setMaintenanceMode] = useState(false)
  
  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [smsNotifications, setSmsNotifications] = useState(false)
  const [pushNotifications, setPushNotifications] = useState(true)
  
  // Security settings
  const [dataRetentionYears, setDataRetentionYears] = useState(5)

  useEffect(() => {
    loadSettings()
    loadActiveModel()
  }, [])

  const loadActiveModel = async () => {
    try {
      const model = await mlService.getActiveModel()
      setActiveModel(model)
    } catch (err) {
      console.error('Erreur lors du chargement du modèle actif:', err)
    }
  }

  const loadSettings = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await settingsService.getSettings()
      setSettings(data)
      
      // Convert API thresholds (0-1) to grade scale (0-20)
      setHighRiskThreshold(data.ml_risk_threshold_low * 20)
      setMediumRiskThreshold(data.ml_risk_threshold_medium * 20)
      setDailyPredictions(data.ml_auto_training)
      setAutoAlerts(data.alert_auto_create)
      setRetrainingFrequency(data.ml_training_frequency)
      
      // General settings
      setSystemLanguage(data.system_language || 'fr')
      setSystemTimezone(data.system_timezone || 'Africa/Dakar')
      setSystemDateFormat(data.system_date_format || 'DD/MM/YYYY')
      setMaintenanceMode(data.system_maintenance_mode || false)
      
      // Notification settings
      setEmailNotifications(data.notification_email_enabled ?? true)
      setSmsNotifications(data.notification_sms_enabled ?? false)
      setPushNotifications(data.notification_push_enabled ?? true)
      
      // Security settings
      setDataRetentionYears(data.data_retention_years || 5)
    } catch (err) {
      console.error('Erreur lors du chargement des paramètres:', err)
      setError('Impossible de charger les paramètres système')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveSettings = async () => {
    setSaving(true)
    setError(null)
    setSuccessMessage(null)
    try {
      const updatedSettings = await settingsService.updateSettings({
        ml_risk_threshold_low: highRiskThreshold / 20,
        ml_risk_threshold_medium: mediumRiskThreshold / 20,
        ml_risk_threshold_high: (mediumRiskThreshold + 2) / 20, // High threshold above medium
        ml_auto_training: dailyPredictions,
        ml_training_frequency: retrainingFrequency as 'daily' | 'weekly' | 'monthly',
        alert_auto_create: autoAlerts,
        // General settings
        system_language: systemLanguage,
        system_timezone: systemTimezone,
        system_date_format: systemDateFormat,
        system_maintenance_mode: maintenanceMode,
        // Notification settings
        notification_email_enabled: emailNotifications,
        notification_sms_enabled: smsNotifications,
        notification_push_enabled: pushNotifications,
        // Security settings
        data_retention_years: dataRetentionYears,
      })
      setSettings(updatedSettings)
      setSuccessMessage('Paramètres enregistrés avec succès')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err: any) {
      console.error('Erreur lors de la sauvegarde:', err)
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde des paramètres')
    } finally {
      setSaving(false)
    }
  }

  const handleResetSettings = async () => {
    setSaving(true)
    setError(null)
    try {
      const result = await settingsService.resetSettings()
      setSettings(result.data)
      setHighRiskThreshold(result.data.ml_risk_threshold_low * 20)
      setMediumRiskThreshold(result.data.ml_risk_threshold_medium * 20)
      setDailyPredictions(result.data.ml_auto_training)
      setAutoAlerts(result.data.alert_auto_create)
      setRetrainingFrequency(result.data.ml_training_frequency)
      // General settings
      setSystemLanguage(result.data.system_language || 'fr')
      setSystemTimezone(result.data.system_timezone || 'Africa/Dakar')
      setSystemDateFormat(result.data.system_date_format || 'DD/MM/YYYY')
      setMaintenanceMode(result.data.system_maintenance_mode || false)
      // Notification settings
      setEmailNotifications(result.data.notification_email_enabled ?? true)
      setSmsNotifications(result.data.notification_sms_enabled ?? false)
      setPushNotifications(result.data.notification_push_enabled ?? true)
      // Security settings
      setDataRetentionYears(result.data.data_retention_years || 5)
      setSuccessMessage(result.message)
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err: any) {
      console.error('Erreur lors de la réinitialisation:', err)
      setError(err.response?.data?.detail || 'Erreur lors de la réinitialisation')
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { id: 'general', label: 'Général' },
    { id: 'ai', label: 'IA & Prédictions' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'security', label: 'Sécurité' },
  ]

  if (loading) {
    return (
      <MiseEnPagePrincipale title="Paramètres Système">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Chargement des paramètres...</span>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  return (
    <MiseEnPagePrincipale title="Paramètres Système">
      <div className="mx-auto max-w-4xl flex flex-col gap-6">
        {/* Page Heading */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-4xl font-black leading-tight tracking-tight text-gray-900 dark:text-white">
              Paramètres Système
            </h1>
            <p className="text-base text-gray-500 dark:text-gray-400 leading-normal">
              Configurez les paramètres globaux et les modèles d'intelligence artificielle de la plateforme ISI.
            </p>
          </div>
          <div className="flex gap-3">
            <Bouton variant="outline" onClick={() => setResetConfirmation(true)} disabled={saving}>
              <span className="material-symbols-outlined text-sm mr-1">restart_alt</span>
              Réinitialiser
            </Bouton>
            <Bouton onClick={handleSaveSettings} disabled={saving}>
              {saving ? (
                <>
                  <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                  Enregistrement...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-sm mr-1">save</span>
                  Enregistrer
                </>
              )}
            </Bouton>
          </div>
        </div>

        {/* Success/Error Messages */}
        {successMessage && (
          <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-green-700 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800">
            <span className="material-symbols-outlined mr-2 align-middle">check_circle</span>
            {successMessage}
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800">
            <span className="material-symbols-outlined mr-2 align-middle">error</span>
            {error}
          </div>
        )}

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
                    <p className="text-primary text-xs font-semibold">
                      {activeModel ? `${activeModel.name} ${activeModel.version}` : 'Aucun modèle actif'}
                    </p>
                  </div>
                </div>
                {activeModel ? (
                  <>
                    <div className="space-y-3 mb-6">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 dark:text-gray-400">Type</span>
                        <span className="font-medium text-gray-900 dark:text-white">{activeModel.algorithm || 'XGBoost'}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 dark:text-gray-400">Précision</span>
                        <span className="font-medium text-emerald-600">
                          {typeof activeModel.accuracy === 'string' 
                            ? parseFloat(activeModel.accuracy).toFixed(1) 
                            : (activeModel.accuracy > 1 ? activeModel.accuracy.toFixed(1) : (activeModel.accuracy * 100).toFixed(1))}%
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 dark:text-gray-400">F1-Score</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {typeof activeModel.f1Score === 'string' 
                            ? parseFloat(activeModel.f1Score).toFixed(3) 
                            : (activeModel.f1Score?.toFixed(3) ?? 'N/A')}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 dark:text-gray-400">Dernière mise à jour</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {activeModel.trainedAt 
                            ? new Date(activeModel.trainedAt).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
                            : 'N/A'}
                        </span>
                      </div>
                    </div>
                    <Bouton variant="outline" className="w-full" onClick={() => navigate(`${ROUTES.ML_MODELS}/${activeModel.id}`)}>
                      Voir les détails
                    </Bouton>
                  </>
                ) : (
                  <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
                    <p>Aucun modèle ML n'est actuellement actif.</p>
                    <Bouton variant="outline" className="mt-4" onClick={() => navigate(ROUTES.ML_MODELS)}>
                      Gérer les modèles
                    </Bouton>
                  </div>
                )}
              </Carte>
            </div>
          </div>
        )}

        {activeTab === 'general' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Paramètres régionaux */}
            <Carte>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">language</span>
                </div>
                <div>
                  <h3 className="text-gray-900 dark:text-white font-bold">Paramètres Régionaux</h3>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">Langue, fuseau horaire et format de date</p>
                </div>
              </div>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Langue du système
                  </label>
                  <div className="relative">
                    <select
                      value={systemLanguage}
                      onChange={(e) => setSystemLanguage(e.target.value as 'fr' | 'en')}
                      className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white appearance-none cursor-pointer focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="fr">🇫🇷 Français</option>
                      <option value="en">🇬🇧 English</option>
                    </select>
                    <span className="absolute right-3 top-3 material-symbols-outlined text-gray-500 text-sm pointer-events-none">
                      expand_more
                    </span>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Fuseau horaire
                  </label>
                  <div className="relative">
                    <select
                      value={systemTimezone}
                      onChange={(e) => setSystemTimezone(e.target.value)}
                      className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white appearance-none cursor-pointer focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="Africa/Dakar">Africa/Dakar (UTC+0)</option>
                      <option value="Europe/Paris">Europe/Paris (UTC+1/+2)</option>
                      <option value="Africa/Abidjan">Africa/Abidjan (UTC+0)</option>
                      <option value="Africa/Lagos">Africa/Lagos (UTC+1)</option>
                    </select>
                    <span className="absolute right-3 top-3 material-symbols-outlined text-gray-500 text-sm pointer-events-none">
                      expand_more
                    </span>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Format de date
                  </label>
                  <div className="relative">
                    <select
                      value={systemDateFormat}
                      onChange={(e) => setSystemDateFormat(e.target.value)}
                      className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white appearance-none cursor-pointer focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="DD/MM/YYYY">DD/MM/YYYY (31/12/2024)</option>
                      <option value="MM/DD/YYYY">MM/DD/YYYY (12/31/2024)</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD (2024-12-31)</option>
                    </select>
                    <span className="absolute right-3 top-3 material-symbols-outlined text-gray-500 text-sm pointer-events-none">
                      expand_more
                    </span>
                  </div>
                </div>
              </div>
            </Carte>
            
            {/* Mode Maintenance */}
            <Carte>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
                  <span className="material-symbols-outlined text-amber-600 dark:text-amber-400">construction</span>
                </div>
                <div>
                  <h3 className="text-gray-900 dark:text-white font-bold">Mode Maintenance</h3>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">Gérer l'accessibilité du système</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-amber-500">warning</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Activer le mode maintenance</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Les utilisateurs non-admin ne pourront pas accéder</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={maintenanceMode}
                    onClick={() => setMaintenanceMode(!maintenanceMode)}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                      maintenanceMode ? 'bg-amber-500' : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                  >
                    <span
                      className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                        maintenanceMode ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
                
                {maintenanceMode && (
                  <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                    <div className="flex gap-3">
                      <span className="material-symbols-outlined text-amber-600">info</span>
                      <div>
                        <p className="text-sm font-medium text-amber-800 dark:text-amber-200">Mode maintenance actif</p>
                        <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                          Seuls les administrateurs peuvent accéder au système. Les autres utilisateurs verront une page de maintenance.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Informations système</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Version</span>
                    <span className="font-medium text-gray-900 dark:text-white">SPAS v2.1.0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Environnement</span>
                    <span className={`font-medium ${maintenanceMode ? 'text-amber-600' : 'text-emerald-600'}`}>
                      {maintenanceMode ? 'Maintenance' : 'Production'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Langue active</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {systemLanguage === 'fr' ? '🇫🇷 Français' : '🇬🇧 English'}
                    </span>
                  </div>
                </div>
              </div>
            </Carte>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Notifications par Email */}
            <Carte className={emailNotifications ? 'ring-2 ring-primary/30' : ''}>
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                  <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-2xl">mail</span>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={emailNotifications}
                  onClick={() => setEmailNotifications(!emailNotifications)}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                    emailNotifications ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      emailNotifications ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Notifications Email</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Recevez des alertes par email lors d'événements importants
              </p>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Alertes de risque élevé</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Rapports hebdomadaires</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Mises à jour système</span>
                </div>
              </div>
              {emailNotifications && (
                <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                  <p className="text-xs text-amber-700 dark:text-amber-300 flex items-start gap-2">
                    <span className="material-symbols-outlined text-sm mt-0.5">warning</span>
                    <span>Serveur SMTP non configuré. Contactez l'administrateur pour activer l'envoi d'emails.</span>
                  </p>
                </div>
              )}
            </Carte>
            
            {/* Notifications SMS */}
            <Carte className={smsNotifications ? 'ring-2 ring-primary/30' : ''}>
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
                  <span className="material-symbols-outlined text-green-600 dark:text-green-400 text-2xl">sms</span>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={smsNotifications}
                  onClick={() => setSmsNotifications(!smsNotifications)}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                    smsNotifications ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      smsNotifications ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Notifications SMS</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Alertes critiques envoyées par SMS sur votre téléphone
              </p>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Alertes urgentes uniquement</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Confirmation d'actions critiques</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Alertes de sécurité</span>
                </div>
              </div>
              {smsNotifications && (
                <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                  <p className="text-xs text-amber-700 dark:text-amber-300 flex items-start gap-2">
                    <span className="material-symbols-outlined text-sm mt-0.5">warning</span>
                    <span>Provider SMS non configuré (Twilio, etc.). Contactez l'administrateur système.</span>
                  </p>
                </div>
              )}
            </Carte>
            
            {/* Notifications Push */}
            <Carte className={pushNotifications ? 'ring-2 ring-primary/30' : ''}>
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
                  <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-2xl">notifications_active</span>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={pushNotifications}
                  onClick={() => setPushNotifications(!pushNotifications)}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                    pushNotifications ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      pushNotifications ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Notifications Push</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Notifications en temps réel dans votre navigateur
              </p>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Mises à jour en temps réel</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Nouvelles prédictions</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span>Tâches assignées</span>
                </div>
              </div>
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-xs text-blue-700 dark:text-blue-300 flex items-start gap-2">
                  <span className="material-symbols-outlined text-sm mt-0.5">info</span>
                  <span>Les notifications push fonctionnent uniquement dans l'application (pas de push système).</span>
                </p>
              </div>
            </Carte>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Rétention des données */}
            <Carte>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                  <span className="material-symbols-outlined text-red-600 dark:text-red-400">database</span>
                </div>
                <div>
                  <h3 className="text-gray-900 dark:text-white font-bold">Rétention des Données</h3>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">Politique de conservation des données</p>
                </div>
              </div>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Durée de conservation (années)
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={dataRetentionYears}
                      onChange={(e) => setDataRetentionYears(parseInt(e.target.value))}
                      className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary"
                    />
                    <span className="text-2xl font-bold text-primary min-w-[3rem] text-center">
                      {dataRetentionYears}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    Les données des étudiants seront conservées pendant {dataRetentionYears} an{dataRetentionYears > 1 ? 's' : ''} après leur sortie.
                  </p>
                </div>
                
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">info</span>
                    Données concernées
                  </h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                      Notes et évaluations
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                      Historique de présence
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                      Prédictions et alertes
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                      Interventions pédagogiques
                    </li>
                  </ul>
                </div>
              </div>
            </Carte>
            
            {/* Sécurité & Accès */}
            <Carte>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
                  <span className="material-symbols-outlined text-emerald-600 dark:text-emerald-400">shield</span>
                </div>
                <div>
                  <h3 className="text-gray-900 dark:text-white font-bold">Sécurité & Accès</h3>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">Paramètres de sécurité du système</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-emerald-500">verified_user</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Authentification JWT</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Tokens sécurisés avec refresh</p>
                    </div>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-full">
                    Actif
                  </span>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-blue-500">lock</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Chiffrement HTTPS</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">TLS 1.3 pour toutes les connexions</p>
                    </div>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-full">
                    Actif
                  </span>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-purple-500">group</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Contrôle d'accès RBAC</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">4 rôles : Admin, Enseignant, DS, Pédagogique</p>
                    </div>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-full">
                    Actif
                  </span>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-amber-500">schedule</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Expiration des sessions</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Déconnexion automatique après inactivité</p>
                    </div>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded-full">
                    24h
                  </span>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Audit & Journalisation</h4>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-blue-600">history</span>
                    <div>
                      <p className="text-sm font-medium text-blue-800 dark:text-blue-200">Journalisation activée</p>
                      <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                        Toutes les actions sont enregistrées pour l'audit de conformité RGPD.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Carte>
          </div>
        )}

        <ModaleConfirmation
          isOpen={resetConfirmation}
          onClose={() => setResetConfirmation(false)}
          onConfirm={handleResetSettings}
          title="Réinitialiser les paramètres"
          message="Êtes-vous sûr de vouloir réinitialiser tous les paramètres aux valeurs par défaut ? Cette action est irréversible."
          confirmText="Réinitialiser"
          cancelText="Annuler"
          variant="warning"
          isLoading={saving}
        />
      </div>
    </MiseEnPagePrincipale>
  )
}
