import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { clsx } from 'clsx'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import GraphiqueLignes from '@/components/charts/GraphiqueLignes'
import GraphiqueSHAP from '@/components/charts/GraphiqueSHAP'
import ModaleIntervention from '@/components/modals/ModaleIntervention'
import { studentService, Student } from '@/api/services/studentService'
import { predictionService, Prediction, PredictionFactor } from '@/api/services/predictionService'
import { interventionService, Intervention } from '@/api/services/interventionService'
import { alertService } from '@/api/services/alertService'
import { analyticsService } from '@/api/services/analyticsService'
import { ROUTES } from '@/utils/constants'
import { toast } from 'react-toastify'

interface RiskEvolutionPoint {
  month: string
  value: number
}

interface InterventionDisplay {
  date: string
  type: string
  typeColor: string
  responsible: string
  status: string
  statusVariant: 'success' | 'info' | 'warning' | 'danger'
}

export default function DetailPrediction() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [student, setStudent] = useState<Student | null>(null)
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [loading, setLoading] = useState(true)
  const [riskEvolution, setRiskEvolution] = useState<RiskEvolutionPoint[]>([])
  const [interventions, setInterventions] = useState<InterventionDisplay[]>([])
  const [isInterventionModalOpen, setIsInterventionModalOpen] = useState(false)
  const [creatingAlert, setCreatingAlert] = useState(false)

  useEffect(() => {
    const loadData = async () => {
      if (!id) return
      setLoading(true)
      try {
        const predictionData = await predictionService.getById(id)
        if (predictionData) {
          setPrediction(predictionData)
          
          let studentId = predictionData.studentId
          if (studentId) {
            const studentData = await studentService.getById(studentId)
            setStudent(studentData)
            
            // Charger l'évolution du risque depuis l'API
            try {
              const riskData = await analyticsService.getRiskEvolution(Number(studentId))
              if (riskData && riskData.length > 0) {
                const months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
                setRiskEvolution(riskData.map((r: any) => {
                  const date = new Date(r.date)
                  return {
                    month: months[date.getMonth()],
                    value: Math.round(r.risk_score * 100)
                  }
                }))
              } else {
                // Pas de données d'évolution disponibles
                setRiskEvolution([])
              }
            } catch (e) {
              console.log('Risk evolution not available')
              setRiskEvolution([])
            }
            
            // Charger les interventions depuis l'API
            try {
              const interventionsData = await interventionService.getByStudent(String(studentId))
              if (interventionsData && interventionsData.length > 0) {
                const typeColorMap: Record<string, string> = {
                  'meeting': 'purple',
                  'email': 'blue',
                  'alert': 'orange',
                  'call': 'green',
                  'tutoring': 'cyan'
                }
                const statusMap: Record<string, { status: string; variant: 'success' | 'info' | 'warning' | 'danger' }> = {
                  'completed': { status: 'Réalisé', variant: 'success' },
                  'pending': { status: 'En attente', variant: 'warning' },
                  'scheduled': { status: 'Planifié', variant: 'info' },
                  'cancelled': { status: 'Annulé', variant: 'danger' }
                }
                setInterventions(interventionsData.slice(0, 5).map((intervention: Intervention) => ({
                  date: new Date(intervention.scheduled_date || intervention.created_at || new Date()).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }),
                  type: intervention.type || 'Entretien',
                  typeColor: typeColorMap[intervention.type?.toLowerCase()] || 'gray',
                  responsible: intervention.responsible_name || 'Système',
                  status: statusMap[intervention.status]?.status || intervention.status,
                  statusVariant: statusMap[intervention.status]?.variant || 'info'
                })))
              }
            } catch (e) {
              console.log('Interventions not available')
            }
          }
        }
      } catch (error) {
        console.error('Erreur lors du chargement:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [id])

  const handleCreateAlert = async () => {
    if (!student || !prediction) return
    setCreatingAlert(true)
    try {
      await alertService.create({
        student_id: student.id,
        prediction_id: prediction.id,
        type: 'high_risk',
        message: `Alerte générée pour ${student.firstName} ${student.lastName} - Score de risque: ${prediction.riskScore}%`,
        severity: (prediction.riskScore ?? 0) >= 85 ? 'high' : 'medium'
      })
      toast.success('Alerte créée avec succès')
      navigate(ROUTES.ALERTS)
    } catch (error) {
      console.error('Erreur création alerte:', error)
      toast.error('Erreur lors de la création de l\'alerte')
    } finally {
      setCreatingAlert(false)
    }
  }

  const reloadInterventions = async () => {
    if (!student) return
    try {
      const interventionsData = await interventionService.getByStudent(String(student.id))
      if (interventionsData && interventionsData.length > 0) {
        const typeColorMap: Record<string, string> = {
          'meeting': 'purple',
          'email': 'blue',
          'alert': 'orange',
          'call': 'green',
          'tutoring': 'cyan'
        }
        const statusMap: Record<string, { status: string; variant: 'success' | 'info' | 'warning' | 'danger' }> = {
          'completed': { status: 'Réalisé', variant: 'success' },
          'pending': { status: 'En attente', variant: 'warning' },
          'scheduled': { status: 'Planifié', variant: 'info' },
          'cancelled': { status: 'Annulé', variant: 'danger' }
        }
        setInterventions(interventionsData.slice(0, 5).map((intervention: Intervention) => ({
          date: new Date(intervention.scheduled_date || intervention.created_at || new Date()).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }),
          type: intervention.type || 'Entretien',
          typeColor: typeColorMap[intervention.type?.toLowerCase()] || 'gray',
          responsible: intervention.responsible_name || 'Système',
          status: statusMap[intervention.status]?.status || intervention.status,
          statusVariant: statusMap[intervention.status]?.variant || 'info'
        })))
      }
    } catch (e) {
      console.log('Failed to reload interventions')
    }
  }

  if (loading) {
    return (
      <MiseEnPagePrincipale>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500 dark:text-gray-400">Chargement...</div>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  if (!prediction || !student) {
    return (
      <MiseEnPagePrincipale>
        <div className="mx-auto max-w-7xl">
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Prédiction non trouvée
            </h2>
            <Bouton onClick={() => navigate(ROUTES.STUDENTS)}>Retour</Bouton>
          </div>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  const getRiskLevel = () => {
    const score = prediction.riskScore ?? 0
    if (score >= 85) return { label: 'ALERTE DÉCROCHAGE', color: 'danger', threshold: 'critique' }
    if (score >= 70) return { label: 'RISQUE ÉLEVÉ', color: 'danger', threshold: 'élevé' }
    if (score >= 50) return { label: 'RISQUE MOYEN', color: 'warning', threshold: 'moyen' }
    return { label: 'RISQUE FAIBLE', color: 'success', threshold: 'faible' }
  }

  const riskInfo = getRiskLevel()

// Préparer les facteurs SHAP depuis les données API uniquement
  const shapFactors = prediction?.factors?.map((f: PredictionFactor) => ({
    feature: f.name || f.feature || 'Facteur',
    value: f.value ?? 0,
    contribution: f.contribution ?? f.impact ?? 0,
    direction: (f.direction || (f.impact && f.impact > 0 ? 'positive' : 'negative')) as 'positive' | 'negative'
  })) || []

  // Est-ce que l'explication vient de SHAP ?
  const isShapExplained = prediction?.shap_explained ?? false

  return (
    <MiseEnPagePrincipale title="Détail Prédiction">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Top Section: Profile & Risk Status */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Student Profile Carte */}
          <Carte className="lg:col-span-7 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
              <span className="material-symbols-outlined text-[180px]">school</span>
            </div>
            <div className="flex flex-col sm:flex-row gap-6 relative z-10">
              <div className="flex-shrink-0 relative">
                <div className="w-32 h-32 rounded-xl bg-gray-200 dark:bg-gray-700 shadow-md flex items-center justify-center">
                  <span className="material-symbols-outlined text-6xl text-gray-400">person</span>
                </div>
                <div className="absolute -bottom-2 -right-2 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-xs font-bold px-2 py-1 rounded-md border border-white dark:border-gray-800">
                  Actif
                </div>
              </div>
              <div className="flex flex-col justify-center flex-1">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                  {student.firstName} {student.lastName}
                </h1>
                <p className="text-purple-600 dark:text-purple-400 font-medium mb-4">
                  Matricule: <span className="text-gray-900 dark:text-gray-200">{student.matricule}</span>
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-2 gap-x-8 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-[18px]">school</span>
                    <span className="text-gray-900 dark:text-gray-300">{student.programName || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-[18px]">calendar_today</span>
                    <span className="text-gray-900 dark:text-gray-300">{student.sessionName || 'Session en cours'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-[18px]">mail</span>
                    <span className="text-gray-900 dark:text-gray-300">{student.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-[18px]">call</span>
                    <span className="text-gray-900 dark:text-gray-300">{student.phone || 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>
          </Carte>

          {/* Risk Hero Carte */}
          <Carte className={clsx(
            'lg:col-span-5 p-0 overflow-hidden',
            riskInfo.color === 'danger' && 'border-red-200 dark:border-red-900/30',
            riskInfo.color === 'warning' && 'border-amber-200 dark:border-amber-900/30',
            riskInfo.color === 'success' && 'border-green-200 dark:border-green-900/30'
          )}>
            <div className={clsx(
              'p-4 flex justify-between items-center border-b',
              riskInfo.color === 'danger' && 'bg-red-50 dark:bg-red-900/10 border-red-100 dark:border-red-900/30',
              riskInfo.color === 'warning' && 'bg-amber-50 dark:bg-amber-900/10 border-amber-100 dark:border-amber-900/30',
              riskInfo.color === 'success' && 'bg-green-50 dark:bg-green-900/10 border-green-100 dark:border-green-900/30'
            )}>
              <div className={clsx(
                'flex items-center gap-2 font-bold',
                riskInfo.color === 'danger' && 'text-red-600 dark:text-red-400',
                riskInfo.color === 'warning' && 'text-amber-600 dark:text-amber-400',
                riskInfo.color === 'success' && 'text-green-600 dark:text-green-400'
              )}>
                <span className="material-symbols-outlined">warning</span>
                <span>{riskInfo.label}</span>
              </div>
              <span className={clsx(
                'text-xs font-medium bg-white px-2 py-1 rounded border',
                riskInfo.color === 'danger' && 'dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-900/30',
                riskInfo.color === 'warning' && 'dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-900/30',
                riskInfo.color === 'success' && 'dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-900/30'
              )}>
                Mise à jour: {new Date(prediction.createdAt || Date.now()).toLocaleDateString('fr-FR')}
              </span>
            </div>
            <div className="p-6 flex-1 flex flex-col justify-center">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-sm text-purple-600 dark:text-purple-400 font-medium mb-1">Probabilité de Risque</p>
                  <div className="text-5xl font-bold text-gray-900 dark:text-white">
                    {prediction.riskScore}
                    <span className="text-2xl text-purple-600 dark:text-purple-400">%</span>
                  </div>
                </div>
                <div className="h-16 w-16 rounded-full border-4 border-red-200 dark:border-red-900/30 flex items-center justify-center relative">
                  <span className="material-symbols-outlined text-red-600 dark:text-red-400 text-3xl">trending_up</span>
                  <div className="absolute inset-0 border-4 border-red-600 dark:border-red-500 rounded-full border-l-transparent border-b-transparent rotate-[-45deg]"></div>
                </div>
              </div>
              <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-3 mb-2">
                <div 
                  className={clsx(
                    'h-3 rounded-full',
                    riskInfo.color === 'danger' && 'bg-red-600',
                    riskInfo.color === 'warning' && 'bg-amber-600',
                    riskInfo.color === 'success' && 'bg-green-600'
                  )}
                  style={{ width: `${prediction.riskScore}%` }}
                />
              </div>
              <p className={clsx(
                'text-xs font-medium mb-6',
                riskInfo.color === 'danger' && 'text-red-600 dark:text-red-400',
                riskInfo.color === 'warning' && 'text-amber-600 dark:text-amber-400',
                riskInfo.color === 'success' && 'text-green-600 dark:text-green-400'
              )}>
                Seuil {riskInfo.threshold} dépassé ({(prediction.riskScore ?? 0) >= 85 ? '>85%' : '>70%'}). Action requise {(prediction.riskScore ?? 0) >= 85 ? 'immédiate' : ''}.
              </p>
              <div className="grid grid-cols-2 gap-3 mt-auto">
                <Bouton onClick={() => setIsInterventionModalOpen(true)}>
                  <span className="material-symbols-outlined text-[18px]">add_task</span>
                  Intervention
                </Bouton>
                <Bouton variant="outline" onClick={handleCreateAlert} disabled={creatingAlert}>
                  <span className="material-symbols-outlined text-[18px]">notifications_active</span>
                  {creatingAlert ? 'Création...' : 'Alerte'}
                </Bouton>
              </div>
            </div>
          </Carte>
        </div>

        {/* Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Evolution Chart */}
          <Carte className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Évolution du Score de Risque</h3>
                <p className="text-sm text-purple-600 dark:text-purple-400">Tendance sur les 6 derniers mois</p>
              </div>
              <select className="bg-gray-50 dark:bg-gray-800 border-none text-sm rounded-lg py-1.5 px-3 focus:ring-1 focus:ring-primary text-gray-900 dark:text-white">
                <option>Semestre en cours</option>
                <option>Année complète</option>
              </select>
            </div>
            {riskEvolution.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <span className="material-symbols-outlined text-gray-300 dark:text-gray-600 text-[64px] mb-4">trending_up</span>
                <p className="text-gray-500 dark:text-gray-400 text-center">
                  Aucune donnée d'évolution disponible.<br/>
                  <span className="text-sm">L'historique apparaîtra après plusieurs prédictions.</span>
                </p>
              </div>
            ) : (
              <GraphiqueLignes
                data={riskEvolution}
                dataKey="value"
                lines={[{ key: 'value', name: 'Score de Risque', color: '#DC2626' }]}
                xAxisKey="month"
                height={250}
              />
            )}
          </Carte>

          {/* SHAP Analysis */}
          <Carte>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">psychology</span>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Facteurs Clés (SHAP)</h3>
              </div>
              {isShapExplained && shapFactors.length > 0 && (
                <span className="px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                  ✓ SHAP Explainability
                </span>
              )}
            </div>
            {shapFactors.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <span className="material-symbols-outlined text-gray-300 dark:text-gray-600 text-[64px] mb-4">science</span>
                <p className="text-gray-500 dark:text-gray-400 text-center">
                  Aucun facteur d'explication disponible.<br/>
                  <span className="text-sm">Les facteurs SHAP apparaîtront après la prédiction.</span>
                </p>
              </div>
            ) : (
              <GraphiqueSHAP
                factors={shapFactors}
                height={280}
                showValues={true}
                title=""
              />
            )}
          </Carte>
        </div>

        {/* History & Interventions Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Intervention List */}
          <Carte className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Historique d'Interventions</h3>
              <Link to={ROUTES.ALERTS} className="text-primary text-sm font-medium hover:underline">Voir tout</Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-800 text-xs text-purple-600 dark:text-purple-400 uppercase tracking-wider">
                    <th className="pb-3 font-medium">Date</th>
                    <th className="pb-3 font-medium">Type</th>
                    <th className="pb-3 font-medium">Responsable</th>
                    <th className="pb-3 font-medium">Statut</th>
                    <th className="pb-3 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {interventions.map((intervention, index) => (
                    <tr key={index} className="group hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <td className="py-4 border-b border-gray-50 dark:border-gray-800 text-gray-900 dark:text-gray-300">
                        {intervention.date}
                      </td>
                      <td className="py-4 border-b border-gray-50 dark:border-gray-800">
                        <span className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full bg-${intervention.typeColor}-500`}></span>
                          {intervention.type}
                        </span>
                      </td>
                      <td className="py-4 border-b border-gray-50 dark:border-gray-800 text-purple-600 dark:text-purple-400">
                        {intervention.responsible}
                      </td>
                      <td className="py-4 border-b border-gray-50 dark:border-gray-800">
                        <Badge variant={intervention.statusVariant} size="sm">
                          {intervention.status}
                        </Badge>
                      </td>
                      <td className="py-4 border-b border-gray-50 dark:border-gray-800 text-right">
                        <button className="text-purple-600 dark:text-purple-400 hover:text-primary transition-colors">
                          <span className="material-symbols-outlined text-[20px]">visibility</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Carte>

          {/* Notes & Metadata */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            {/* Quick Notes */}
            <Carte className="flex-1">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Notes Rapides</h3>
              <div className="space-y-4">
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-purple-600 dark:text-purple-400 mb-1 flex justify-between">
                    <span>Prof. Mathématiques</span>
                    <span>Hier</span>
                  </p>
                  <p className="text-sm text-gray-900 dark:text-gray-300 italic">
                    "{student.firstName} semble désintéressé(e) en classe depuis deux semaines. A surveiller."
                  </p>
                </div>
                <div className="relative">
                  <input
                    className="w-full pl-3 pr-10 py-2 text-sm bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-1 focus:ring-primary focus:border-primary"
                    placeholder="Ajouter une note..."
                    type="text"
                  />
                  <button className="absolute right-2 top-2 text-primary hover:text-purple-700 dark:hover:text-purple-300">
                    <span className="material-symbols-outlined text-[20px]">send</span>
                  </button>
                </div>
              </div>
            </Carte>

            {/* Metadata Carte */}
            <Carte>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Informations Prédiction</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-purple-600 dark:text-purple-400">Modèle</span>
                  <span className="text-gray-900 dark:text-white font-medium">{prediction.modelVersion}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-600 dark:text-purple-400">Date de calcul</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {new Date(prediction.createdAt || Date.now()).toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-600 dark:text-purple-400">Taux de réussite prédit</span>
                  <span className="text-gray-900 dark:text-white font-medium">{prediction.predictedSuccessRate}%</span>
                </div>
              </div>
            </Carte>
          </div>
        </div>
      </div>

      {/* Modale d'intervention */}
      <ModaleIntervention
        isOpen={isInterventionModalOpen}
        onClose={() => setIsInterventionModalOpen(false)}
        studentId={student.id}
        onSuccess={() => {
          setIsInterventionModalOpen(false)
          reloadInterventions()
        }}
      />
    </MiseEnPagePrincipale>
  )
}
