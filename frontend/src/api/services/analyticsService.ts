import apiClient from '../axiosConfig';

// Types pour les analytics
export interface DropoutEvolution {
  month: string;
  predicted: number;
  real: number;
}

export interface ProgramPerformance {
  program: string;
  programId: number;
  success: number;
  risk: number;
  dropout: number;
  totalStudents: number;
}

export interface InterventionEfficacy {
  type: string;
  students: number;
  gpaImpact: string;
  retention: string;
  efficacy: 'Élevée' | 'Moyenne' | 'Faible';
}

export interface AnalyticsMetrics {
  riskGlobal: number;
  interventionsActives: number;
  precisionModele: number;
  dropoutEvolution: DropoutEvolution[];
  performanceByProgram: ProgramPerformance[];
  interventionEfficacy: InterventionEfficacy[];
  tempsReponseHeures: number;
}

export interface RiskDistribution {
  level: string;
  count: number;
  percentage: number;
}

export interface EnrollmentEvolution {
  year: number;
  count: number;
}

export interface DashboardStats {
  totalStudents: number;
  activePrograms: number;
  sessionsCount: number;
  successRate: number;
  enrollmentEvolution: EnrollmentEvolution[];
  programDistribution: { name: string; value: number }[];
  riskDistribution: RiskDistribution[];
  predictedDropoutRate: number;
}

export const analyticsService = {
  /**
   * Récupère les métriques globales pour la page Analytics Avancées
   */
  async getMetrics(dateFrom?: string, dateTo?: string): Promise<AnalyticsMetrics> {
    const params: Record<string, string> = {};
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    
    const response = await apiClient.get<AnalyticsMetrics>('/analytics/metrics/', { params });
    return response.data;
  },

  /**
   * Récupère les statistiques du dashboard général
   */
  async getDashboardStats(academicYear?: string): Promise<DashboardStats> {
    const params: Record<string, string> = {};
    if (academicYear) params.academic_year = academicYear;
    
    const response = await apiClient.get<DashboardStats>('/analytics/dashboard/', { params });
    return response.data;
  },

  /**
   * Récupère la distribution des risques pour le dashboard prédictif
   */
  async getRiskDistribution(sessionId?: number): Promise<RiskDistribution[]> {
    const params: Record<string, number> = {};
    if (sessionId) params.session_id = sessionId;
    
    const response = await apiClient.get<{ distribution: RiskDistribution[] }>('/analytics/risk-distribution/', { params });
    return response.data.distribution;
  },

  /**
   * Récupère l'évolution du décrochage prédit vs réel
   */
  async getDropoutEvolution(months?: number): Promise<DropoutEvolution[]> {
    const params: Record<string, number> = {};
    if (months) params.months = months;
    
    const response = await apiClient.get<{ evolution: DropoutEvolution[] }>('/analytics/dropout-evolution/', { params });
    return response.data.evolution;
  },

  /**
   * Récupère les performances par programme
   */
  async getProgramPerformance(): Promise<ProgramPerformance[]> {
    const response = await apiClient.get<{ programs: ProgramPerformance[] }>('/analytics/program-performance/');
    return response.data.programs;
  },

  /**
   * Récupère l'efficacité des interventions
   */
  async getInterventionEfficacy(): Promise<InterventionEfficacy[]> {
    const response = await apiClient.get<{ interventions: InterventionEfficacy[] }>('/analytics/intervention-efficacy/');
    return response.data.interventions;
  },

  /**
   * Export des analytics en Excel
   */
  async exportExcel(dateFrom?: string, dateTo?: string): Promise<Blob> {
    const params: Record<string, string> = {};
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    
    const response = await apiClient.get('/analytics/export-excel/', {
      params,
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Génère un rapport PDF
   */
  async generateReportPDF(dateFrom?: string, dateTo?: string): Promise<Blob> {
    const params: Record<string, string> = {};
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    
    const response = await apiClient.get('/analytics/generate-report-pdf/', {
      params,
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Récupère l'historique de performance des modèles ML
   */
  async getModelPerformanceHistory(modelId?: number): Promise<{ date: string; accuracy: number; f1_score: number }[]> {
    const params: Record<string, number> = {};
    if (modelId) params.model_id = modelId;
    
    const response = await apiClient.get<{ history: { date: string; accuracy: number; f1_score: number }[] }>('/analytics/model-performance/', { params });
    return response.data.history;
  },

  /**
   * Récupère les facteurs de prédiction pour un étudiant (SHAP values)
   */
  async getPredictionFactors(studentId: number): Promise<{ factor: string; impact: number; value: string }[]> {
    const response = await apiClient.get<{ factors: { factor: string; impact: number; value: string }[] }>(`/analytics/prediction-factors/${studentId}/`);
    return response.data.factors;
  },

  /**
   * Récupère l'évolution du risque d'un étudiant
   */
  async getRiskEvolution(studentId: number): Promise<{ date: string; risk_score: number }[]> {
    const response = await apiClient.get<{ evolution: { date: string; risk_score: number }[] }>(`/analytics/risk-evolution/${studentId}/`);
    return response.data.evolution;
  }
};

export default analyticsService;
