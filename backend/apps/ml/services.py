"""
Machine Learning Service for SPAS.

This module provides the core ML functionality for predicting student dropout risk
using XGBoost with SHAP explanations. It includes:
- Data preprocessing and feature engineering
- Model training with XGBoost, Random Forest, Gradient Boosting
- SHAP-based explainability for individual predictions
- SMOTE for handling imbalanced datasets
- Risk score prediction with feature importance analysis
- Model persistence and versioning
"""
import os
import logging
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)

# XGBoost for high-performance gradient boosting
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    xgb = None

# SHAP for model explainability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    shap = None

# SMOTE for handling imbalanced data
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
    SMOTE = None

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Model storage path
ML_MODELS_PATH = getattr(settings, 'ML_MODEL_PATH', 'ml_models/')


class DropoutRiskPredictor:
    """
    Predicts student dropout risk using machine learning.

    This class handles the complete ML pipeline for SPAS:
    - Feature extraction from student data
    - Model training with cross-validation
    - Risk score prediction
    - Feature importance analysis (SHAP)
    """

    # 24 features computed from real database data
    # NO hardcoded defaults - features can be None if data unavailable
    DEFAULT_FEATURES = [
        # Grade-based features (1-5)
        'average_grade',        # Moyenne des notes (0-20)
        'grade_std',            # Ecart-type des notes
        'min_grade',            # Note minimale
        'failed_subjects',      # Matieres echouees (count)
        'grade_trend',          # Tendance des notes (-1 a 1)

        # Attendance-based features (6-12)
        'attendance_rate',      # Taux de presence (0-100)
        'absences_count',       # Nombre total d'absences
        'late_count',           # Nombre de retards
        'unexcused_absence_rate', # Taux d'absences non justifiees
        'consecutive_absences', # Absences consecutives max
        'recent_attendance_rate', # Taux presence 30 derniers jours
        'attendance_trend',     # Tendance presence (-1 a 1)

        # Academic progression features (13-18)
        'exam_vs_assignment_diff', # Diff exam vs devoirs
        'subjects_count',       # Nombre de matieres
        'pass_rate',            # Taux de reussite (%)
        'best_subject_avg',     # Meilleure moyenne matiere
        'worst_subject_avg',    # Pire moyenne matiere
        'subject_spread',       # Ecart best-worst

        # Temporal/engagement features (19-24)
        'weeks_enrolled',       # Semaines depuis inscription
        'days_since_last_grade', # Jours depuis derniere note
        'days_since_last_attendance', # Jours depuis derniere presence
        'activity_per_week',    # Frequence d'activite
        'prediction_count',     # Nombre de predictions anterieures
        'previous_risk_score',  # Score de risque precedent
    ]

    # Minimum features required for prediction (without heuristics)
    MIN_FEATURES_FOR_PREDICTION = 5

    # Algorithm configurations
    ALGORITHMS = {
        'random_forest': {
            'class': RandomForestClassifier,
            'params': {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42,
                'n_jobs': -1
            }
        },
        'gradient_boosting': {
            'class': GradientBoostingClassifier,
            'params': {
                'n_estimators': 100,
                'max_depth': 5,
                'learning_rate': 0.1,
                'min_samples_split': 5,
                'random_state': 42
            }
        },
        'logistic_regression': {
            'class': LogisticRegression,
            'params': {
                'C': 1.0,
                'max_iter': 1000,
                'random_state': 42,
                'n_jobs': -1
            }
        }
    }

    # Add XGBoost if available
    if XGBOOST_AVAILABLE:
        ALGORITHMS['xgboost'] = {
            'class': xgb.XGBClassifier,
            'params': {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'objective': 'binary:logistic',
                'eval_metric': 'logloss',
                'use_label_encoder': False,
                'random_state': 42,
                'n_jobs': -1
            }
        }

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the predictor.

        Args:
            model_path: Path to a saved model file. If None, model must be trained.
        """
        self.model = None
        self.scaler = None
        self.explainer = None  # SHAP explainer
        self.feature_names = self.DEFAULT_FEATURES.copy()
        self.model_version = None
        self.training_metrics = {}
        self.algorithm_name = None
        self.roc_data = None  # Store ROC curve data

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def prepare_features(self, student_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract and prepare features from student data.
        """
        features = []

        for feature_name in self.feature_names:
            value = student_data.get(feature_name, 0)
            # Handle None values
            if value is None:
                value = 0
            features.append(float(value))

        return np.array(features).reshape(1, -1)

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        algorithm: str = 'xgboost',
        hyperparameters: Optional[Dict] = None,
        feature_names: Optional[List[str]] = None,
        test_size: float = 0.2,
        use_smote: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Train a new model on the provided data with SMOTE and SHAP support.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target labels (0 = low risk, 1 = medium risk, 2 = high risk)
            algorithm: Algorithm to use ('xgboost', 'random_forest', 'gradient_boosting', 'logistic_regression')
            hyperparameters: Optional hyperparameter overrides
            feature_names: Optional list of feature names
            test_size: Fraction of data to use for testing
            use_smote: Whether to use SMOTE for handling imbalanced data
            progress_callback: Optional callback(progress, step, message)

        Returns:
            Dictionary with training metrics including ROC data
        """
        if progress_callback:
            progress_callback(5, 'Initialisation', 'Preparation des donnees...')

        # Store feature names
        if feature_names:
            self.feature_names = feature_names

        # Get algorithm configuration - default to xgboost if available
        if algorithm not in self.ALGORITHMS:
            algorithm = 'xgboost' if XGBOOST_AVAILABLE else 'random_forest'
            logger.warning(f"Unknown algorithm, defaulting to {algorithm}")

        self.algorithm_name = algorithm
        algo_config = self.ALGORITHMS[algorithm]
        params = algo_config['params'].copy()
        if hyperparameters:
            params.update(hyperparameters)

        if progress_callback:
            progress_callback(10, 'Split donnees', 'Division train/test stratifiee...')

        # Stratified split to maintain class distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        if progress_callback:
            progress_callback(15, 'Scaling', 'Normalisation des features...')

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Apply SMOTE if available and requested
        if use_smote and SMOTE_AVAILABLE and len(X_train) > 10:
            if progress_callback:
                progress_callback(25, 'SMOTE', 'Equilibrage des classes avec SMOTE...')
            try:
                smote = SMOTE(random_state=42)
                X_train_scaled, y_train = smote.fit_resample(X_train_scaled, y_train)
                logger.info(f"SMOTE applied: {len(y_train)} samples after resampling")
            except Exception as e:
                logger.warning(f"SMOTE failed: {e}, continuing without resampling")

        if progress_callback:
            progress_callback(35, 'Entrainement', f'Entrainement {algorithm}...')

        # Train model
        self.model = algo_config['class'](**params)
        self.model.fit(X_train_scaled, y_train)

        if progress_callback:
            progress_callback(55, 'Validation', 'Validation croisee 5-fold...')

        # Stratified 5-fold cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=cv)
        cv_mean = cv_scores.mean() * 100
        cv_std = cv_scores.std() * 100

        if progress_callback:
            progress_callback(65, 'Evaluation', 'Calcul des metriques...')

        # Evaluate on test set
        y_pred = self.model.predict(X_test_scaled)

        # Calculate ROC curve data for binary or multiclass
        roc_data = None
        roc_auc = None
        if hasattr(self.model, 'predict_proba'):
            try:
                y_proba = self.model.predict_proba(X_test_scaled)
                n_classes = len(np.unique(y))

                if n_classes == 2:
                    # Binary classification ROC
                    fpr, tpr, thresholds = roc_curve(y_test, y_proba[:, 1])
                    roc_auc = roc_auc_score(y_test, y_proba[:, 1]) * 100
                    roc_data = {
                        'fpr': fpr.tolist(),
                        'tpr': tpr.tolist(),
                        'thresholds': thresholds.tolist(),
                        'auc': roc_auc
                    }
                else:
                    # Multiclass - use OvR (One vs Rest)
                    from sklearn.preprocessing import label_binarize
                    y_test_bin = label_binarize(y_test, classes=range(n_classes))
                    roc_auc = roc_auc_score(y_test_bin, y_proba, multi_class='ovr', average='weighted') * 100
                    # Store ROC for high-risk class (last class)
                    fpr, tpr, thresholds = roc_curve(y_test_bin[:, -1], y_proba[:, -1])
                    roc_data = {
                        'fpr': fpr.tolist(),
                        'tpr': tpr.tolist(),
                        'thresholds': thresholds.tolist(),
                        'auc': roc_auc
                    }
                self.roc_data = roc_data
            except Exception as e:
                logger.warning(f"Could not compute ROC: {e}")

        if progress_callback:
            progress_callback(75, 'SHAP', 'Calcul des explications SHAP...')

        # Initialize SHAP explainer if available
        if SHAP_AVAILABLE:
            try:
                # Use TreeExplainer for tree-based models, KernelExplainer for others
                if algorithm in ['xgboost', 'random_forest', 'gradient_boosting']:
                    self.explainer = shap.TreeExplainer(self.model)
                else:
                    # Sample background data for KernelExplainer
                    background = shap.sample(X_train_scaled, min(100, len(X_train_scaled)))
                    self.explainer = shap.KernelExplainer(self.model.predict_proba, background)
                logger.info("SHAP explainer initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize SHAP explainer: {e}")
                self.explainer = None

        if progress_callback:
            progress_callback(85, 'Metriques', 'Finalisation des metriques...')

        # Calculate metrics (using weighted average for multi-class)
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred) * 100,
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0) * 100,
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0) * 100,
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0) * 100,
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'algorithm': algorithm,
            'smote_applied': use_smote and SMOTE_AVAILABLE,
            'shap_available': self.explainer is not None,
        }

        # Add ROC-AUC if computed
        if roc_auc is not None:
            metrics['roc_auc'] = roc_auc
        if roc_data is not None:
            metrics['roc_curve'] = roc_data

        # Get feature importance if available
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            metrics['feature_importance'] = {
                name: float(imp)
                for name, imp in zip(self.feature_names, importance)
            }
        elif hasattr(self.model, 'coef_'):
            # For logistic regression
            importance = np.abs(self.model.coef_).mean(axis=0)
            metrics['feature_importance'] = {
                name: float(imp)
                for name, imp in zip(self.feature_names, importance)
            }

        self.training_metrics = metrics
        self.model_version = datetime.now().strftime('%Y%m%d_%H%M%S')

        if progress_callback:
            progress_callback(100, 'Termine', 'Entrainement termine avec succes!')

        logger.info(f"Model trained: {algorithm}, accuracy={metrics['accuracy']:.2f}%, ROC-AUC={roc_auc or 'N/A'}")

        return metrics

    def predict_risk(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict dropout risk for a single student.

        IMPORTANT: No fallback to heuristics. If no model is loaded or insufficient
        data, returns an error instead of fake predictions.

        Args:
            student_data: Dictionary of computed features from calculate_student_features_from_db()

        Returns:
            Dictionary with prediction results or error information
        """
        # Check data completeness - count non-None features
        available_features = sum(1 for v in student_data.values() if v is not None)
        missing_features = [k for k, v in student_data.items() if v is None]

        # If no model loaded, return error (NO HEURISTICS)
        if self.model is None:
            return {
                'risk_score': None,
                'risk_level': None,
                'factors': [],
                'confidence': 0,
                'model_version': None,
                'algorithm': None,
                'shap_explained': False,
                'error': 'NO_MODEL_LOADED',
                'error_message': 'Aucun modèle ML entrainé. Veuillez entrainer un modèle avant de générer des prédictions.',
                'available_features': available_features,
                'missing_features': missing_features,
            }

        # Check minimum data requirements
        if available_features < self.MIN_FEATURES_FOR_PREDICTION:
            return {
                'risk_score': None,
                'risk_level': None,
                'factors': [],
                'confidence': 0,
                'model_version': self.model_version,
                'algorithm': self.algorithm_name,
                'shap_explained': False,
                'error': 'INSUFFICIENT_DATA',
                'error_message': f'Données insuffisantes pour prédiction. {available_features}/{self.MIN_FEATURES_FOR_PREDICTION} features disponibles.',
                'available_features': available_features,
                'missing_features': missing_features,
            }

        # Prepare features (replace None with 0 for model input)
        features = self.prepare_features(student_data)

        # Scale features
        if self.scaler:
            features_scaled = self.scaler.transform(features)
        else:
            features_scaled = features

        # Get probability predictions
        if hasattr(self.model, 'predict_proba'):
            probas = self.model.predict_proba(features_scaled)[0]
            # Calculate weighted risk score (assuming 0=low, 1=medium, 2=high or similar)
            n_classes = len(probas)
            if n_classes == 3:
                # 0=low, 1=medium, 2=high
                risk_score = (probas[0] * 0 + probas[1] * 50 + probas[2] * 100)
            elif n_classes == 2:
                # 0=low, 1=high
                risk_score = probas[1] * 100
            else:
                risk_score = probas[-1] * 100

            confidence = max(probas) * 100
        else:
            prediction = self.model.predict(features_scaled)[0]
            risk_score = prediction * 50
            confidence = 70.0

        # Determine risk level
        if risk_score >= 75:
            risk_level = 'critical'
        elif risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        # Analyze risk factors using SHAP
        factors = self._analyze_risk_factors_shap(features_scaled, student_data)

        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'factors': factors,
            'confidence': round(confidence, 2),
            'model_version': self.model_version,
            'algorithm': self.algorithm_name,
            'shap_explained': self.explainer is not None,
            'error': None,
            'available_features': available_features,
            'missing_features': missing_features,
        }

    def _analyze_risk_factors_shap(
        self,
        features_scaled: np.ndarray,
        student_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze risk factors using SHAP values for explainability.

        Args:
            features_scaled: Scaled feature array
            student_data: Original student data dictionary

        Returns:
            List of factors with SHAP-based impacts
        """
        factors = []

        # Try SHAP explanation first
        if self.explainer is not None and SHAP_AVAILABLE:
            try:
                # Get SHAP values
                shap_values = self.explainer.shap_values(features_scaled)

                # Handle different SHAP output formats
                if isinstance(shap_values, list):
                    # Multi-class: use the high-risk class (last one)
                    shap_vals = shap_values[-1][0]
                else:
                    shap_vals = shap_values[0]

                # Create factor list sorted by absolute impact
                factor_impacts = []
                for i, (name, impact) in enumerate(zip(self.feature_names, shap_vals)):
                    value = student_data.get(name, 0)
                    factor_impacts.append({
                        'name': self._translate_feature_name(name),
                        'feature': name,
                        'impact': round(float(impact) * 100, 2),  # Convert to percentage impact
                        'value': self._format_feature_value(name, value),
                        'direction': 'risk' if impact > 0 else 'protective'
                    })

                # Sort by absolute impact and take top 5
                factor_impacts.sort(key=lambda x: abs(x['impact']), reverse=True)
                factors = factor_impacts[:5]

                logger.debug(f"SHAP factors computed: {len(factors)} factors")
                return factors

            except Exception as e:
                logger.warning(f"SHAP explanation failed: {e}, falling back to heuristics")

        # Fallback to heuristic analysis
        return self._analyze_risk_factors_heuristic(student_data)

    def _translate_feature_name(self, name: str) -> str:
        """Translate feature names to French for display."""
        translations = {
            'average_grade': 'Moyenne generale',
            'attendance_rate': 'Taux de presence',
            'assignments_completed': 'Devoirs rendus',
            'late_submissions': 'Retards de soumission',
            'absences_count': 'Nombre d\'absences',
            'consecutive_absences': 'Absences consecutives',
            'grade_trend': 'Tendance des notes',
            'participation_score': 'Score de participation',
            'weeks_enrolled': 'Semaines inscrit',
            'failed_subjects': 'Matieres echouees',
        }
        return translations.get(name, name.replace('_', ' ').title())

    def _format_feature_value(self, name: str, value: Any) -> str:
        """Format feature value for display."""
        if value is None:
            return 'N/A'
        if name in ['average_grade']:
            return f'{value:.1f}/20'
        if name in ['attendance_rate', 'assignments_completed', 'participation_score']:
            return f'{value:.1f}%'
        if name in ['grade_trend']:
            trend = 'en hausse' if value > 0 else 'en baisse' if value < 0 else 'stable'
            return trend
        if name in ['absences_count', 'consecutive_absences', 'late_submissions', 'failed_subjects']:
            return str(int(value))
        if name in ['weeks_enrolled']:
            return f'{int(value)} semaines'
        return str(value)

    def get_shap_summary(self, X_sample: np.ndarray) -> Dict[str, Any]:
        """
        Generate SHAP summary data for visualization.

        Args:
            X_sample: Sample of features to explain

        Returns:
            Dictionary with SHAP summary data for plotting
        """
        if self.explainer is None or not SHAP_AVAILABLE:
            return {'error': 'SHAP explainer not available'}

        try:
            if self.scaler:
                X_scaled = self.scaler.transform(X_sample)
            else:
                X_scaled = X_sample

            shap_values = self.explainer.shap_values(X_scaled)

            # Handle different formats
            if isinstance(shap_values, list):
                shap_vals = shap_values[-1]  # High-risk class
            else:
                shap_vals = shap_values

            # Calculate mean absolute SHAP values for feature importance
            mean_abs_shap = np.abs(shap_vals).mean(axis=0)

            feature_importance = [
                {
                    'feature': name,
                    'name': self._translate_feature_name(name),
                    'importance': round(float(imp), 4)
                }
                for name, imp in zip(self.feature_names, mean_abs_shap)
            ]
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)

            return {
                'feature_importance': feature_importance,
                'shap_values': shap_vals.tolist() if isinstance(shap_vals, np.ndarray) else shap_vals,
                'feature_names': self.feature_names,
                'n_samples': len(X_sample)
            }

        except Exception as e:
            logger.error(f"SHAP summary generation failed: {e}")
            return {'error': str(e)}

    def _predict_risk_heuristic(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict risk using rule-based heuristics when no ML model is available.
        """
        avg_grade = float(student_data.get('average_grade', 10))
        attendance_rate = float(student_data.get('attendance_rate', 100))
        absences_count = int(student_data.get('absences_count', 0))
        failed_subjects = int(student_data.get('failed_subjects', 0))

        risk_score = 0
        factors = []

        # Grade-based risk
        if avg_grade < 8:
            risk_score += 40
            factors.append({'name': 'Moyenne tres faible', 'impact': 40, 'value': f'{avg_grade:.1f}/20'})
        elif avg_grade < 10:
            risk_score += 25
            factors.append({'name': 'Moyenne faible', 'impact': 25, 'value': f'{avg_grade:.1f}/20'})

        # Attendance-based risk
        if attendance_rate < 60:
            risk_score += 35
            factors.append({'name': 'Absenteisme eleve', 'impact': 35, 'value': f'{attendance_rate:.1f}%'})
        elif attendance_rate < 80:
            risk_score += 20
            factors.append({'name': 'Absenteisme modere', 'impact': 20, 'value': f'{attendance_rate:.1f}%'})

        # Failed subjects
        if failed_subjects >= 3:
            risk_score += 25
            factors.append({'name': 'Plusieurs matieres echouees', 'impact': 25, 'value': str(failed_subjects)})
        elif failed_subjects >= 1:
            risk_score += 15
            factors.append({'name': 'Matiere(s) echouee(s)', 'impact': 15, 'value': str(failed_subjects)})

        risk_score = min(100, risk_score)

        if risk_score >= 75:
            risk_level = 'critical'
        elif risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'factors': factors,
            'confidence': 50.0,
            'model_version': 'heuristic',
            'algorithm': 'heuristic',
            'shap_explained': False,
        }

    def _analyze_risk_factors_heuristic(self, student_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback method for risk factors when SHAP is not available."""
        factors = []

        avg = float(student_data.get('average_grade', 10))
        if avg < 10:
            factors.append({
                'name': 'Moyenne Faible',
                'feature': 'average_grade',
                'impact': round((10 - avg) * 4, 2),
                'value': f'{avg:.1f}/20',
                'direction': 'risk'
            })

        att = float(student_data.get('attendance_rate', 100))
        if att < 80:
            factors.append({
                'name': 'Absenteisme',
                'feature': 'attendance_rate',
                'impact': round((80 - att) * 0.5, 2),
                'value': f'{att:.1f}%',
                'direction': 'risk'
            })

        failed = int(student_data.get('failed_subjects', 0))
        if failed > 0:
            factors.append({
                'name': 'Matieres Echouees',
                'feature': 'failed_subjects',
                'impact': round(failed * 10, 2),
                'value': str(failed),
                'direction': 'risk'
            })

        # Sort by impact
        factors.sort(key=lambda x: abs(x['impact']), reverse=True)
        return factors[:5]

    def save_model(self, path: Optional[str] = None) -> str:
        """
        Save the trained model to disk.
        """
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")

        os.makedirs(ML_MODELS_PATH, exist_ok=True)

        if path is None:
            path = os.path.join(
                ML_MODELS_PATH,
                f'dropout_risk_model_{self.model_version}.joblib'
            )

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_version': self.model_version,
            'training_metrics': self.training_metrics,
            'algorithm_name': self.algorithm_name,
            'roc_data': self.roc_data,
            'saved_at': datetime.now().isoformat(),
        }

        # Note: SHAP explainer is not saved as it can be recreated
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")

        return path

    def load_model(self, path: Optional[str] = None) -> None:
        """
        Load a trained model from disk.
        """
        if path is None:
            if not os.path.exists(ML_MODELS_PATH):
                raise FileNotFoundError(f"Model directory not found: {ML_MODELS_PATH}")

            model_files = [f for f in os.listdir(ML_MODELS_PATH) if f.endswith('.joblib')]
            if not model_files:
                raise FileNotFoundError("No model files found")

            model_files.sort(reverse=True)
            path = os.path.join(ML_MODELS_PATH, model_files[0])

        model_data = joblib.load(path)

        self.model = model_data['model']
        self.scaler = model_data.get('scaler')
        self.feature_names = model_data.get('feature_names', self.DEFAULT_FEATURES)
        self.model_version = model_data.get('model_version')
        self.training_metrics = model_data.get('training_metrics', {})
        self.algorithm_name = model_data.get('algorithm_name', 'unknown')
        self.roc_data = model_data.get('roc_data')

        # Recreate SHAP explainer if possible
        if SHAP_AVAILABLE and self.model is not None:
            try:
                if self.algorithm_name in ['xgboost', 'random_forest', 'gradient_boosting']:
                    self.explainer = shap.TreeExplainer(self.model)
                    logger.info("SHAP explainer recreated from loaded model")
            except Exception as e:
                logger.warning(f"Could not recreate SHAP explainer: {e}")
                self.explainer = None

        logger.info(f"Model loaded from {path}")


def generate_synthetic_training_data(n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training data for model development and testing.
    """
    np.random.seed(42)

    # Generate features
    df = pd.DataFrame({
        'average_grade': np.random.normal(12, 3, n_samples).clip(0, 20),
        'attendance_rate': np.random.normal(85, 15, n_samples).clip(0, 100),
        'assignments_completed': np.random.normal(80, 20, n_samples).clip(0, 100),
        'late_submissions': np.random.poisson(2, n_samples).clip(0, 10),
        'absences_count': np.random.poisson(3, n_samples).clip(0, 20),
        'consecutive_absences': np.random.poisson(1, n_samples).clip(0, 5),
        'grade_trend': np.random.normal(0, 0.3, n_samples).clip(-1, 1),
        'participation_score': np.random.normal(70, 20, n_samples).clip(0, 100),
        'weeks_enrolled': np.random.randint(4, 32, n_samples),
        'failed_subjects': np.random.poisson(0.5, n_samples).clip(0, 5),
    })

    # Create target with complex non-linear relationship
    score = (
        (20 - df['average_grade']) * 4 +
        (100 - df['attendance_rate']) * 0.6 +
        (df['consecutive_absences'] * 15) +
        (df['failed_subjects'] * 20)
    )
    score += np.random.normal(0, 10, n_samples)

    # 0: Low, 1: Medium, 2: High
    y = np.zeros(n_samples, dtype=int)
    y[score > 40] = 1
    y[score > 70] = 2

    return df.values, y


def calculate_student_features_from_db(student) -> Dict[str, float]:
    """
    Calculate 24 ML features from database records for a given student.

    ALL values are computed from real database data.
    Returns None for features that cannot be computed (no fallback/default values).

    Features computed:
    1-5: Grade-based features
    6-12: Attendance-based features
    13-18: Academic progression features
    19-24: Temporal/engagement features
    """
    from apps.grades.models import Grade
    from apps.attendance.models import Attendance
    from django.db.models import Avg, Count, StdDev, Min, Max
    from django.utils import timezone
    from datetime import timedelta

    features = {}
    now = timezone.now()

    # ============================================================
    # GRADE-BASED FEATURES (1-5)
    # ============================================================
    grades = student.grades.all().order_by('date')
    grade_values = list(grades.values_list('value', flat=True))

    if grade_values:
        # 1. Average grade (0-20 scale)
        features['average_grade'] = float(np.mean(grade_values))

        # 2. Grade standard deviation (variability)
        features['grade_std'] = float(np.std(grade_values)) if len(grade_values) > 1 else 0.0

        # 3. Minimum grade
        features['min_grade'] = float(min(grade_values))

        # 4. Number of failed subjects (grade < 10)
        features['failed_subjects'] = sum(1 for g in grade_values if g < 10)

        # 5. Grade trend (comparing recent vs older grades)
        if len(grade_values) >= 4:
            mid_point = len(grade_values) // 2
            old_avg = np.mean(grade_values[:mid_point])
            recent_avg = np.mean(grade_values[mid_point:])
            # Normalized to -1 (declining) to +1 (improving)
            features['grade_trend'] = float(np.clip((recent_avg - old_avg) / 10, -1, 1))
        else:
            features['grade_trend'] = 0.0
    else:
        # NO DEFAULT VALUES - indicate missing data
        features['average_grade'] = None
        features['grade_std'] = None
        features['min_grade'] = None
        features['failed_subjects'] = None
        features['grade_trend'] = None

    # ============================================================
    # ATTENDANCE-BASED FEATURES (6-12)
    # ============================================================
    attendances = student.attendances.all().order_by('date')

    if attendances.exists():
        total_records = attendances.count()
        present_count = attendances.filter(status='present').count()
        absent_count = attendances.filter(status='absent').count()
        late_count = attendances.filter(status='late').count()
        excused_count = attendances.filter(status='excused').count()

        # 6. Attendance rate (percentage of present)
        features['attendance_rate'] = (present_count / total_records) * 100 if total_records > 0 else None

        # 7. Total absences count
        features['absences_count'] = absent_count

        # 8. Total late arrivals count
        features['late_count'] = late_count

        # 9. Unexcused absence rate
        unexcused = absent_count
        features['unexcused_absence_rate'] = (unexcused / total_records) * 100 if total_records > 0 else 0.0

        # 10. Calculate consecutive absences (actual computation)
        consecutive_absences = 0
        max_consecutive = 0
        for att in attendances:
            if att.status == 'absent':
                consecutive_absences += 1
                max_consecutive = max(max_consecutive, consecutive_absences)
            else:
                consecutive_absences = 0
        features['consecutive_absences'] = max_consecutive

        # 11. Recent attendance (last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        recent_attendance = attendances.filter(date__gte=thirty_days_ago.date())
        if recent_attendance.exists():
            recent_present = recent_attendance.filter(status='present').count()
            features['recent_attendance_rate'] = (recent_present / recent_attendance.count()) * 100
        else:
            features['recent_attendance_rate'] = None

        # 12. Attendance trend (comparing recent vs older)
        if total_records >= 10:
            mid_date = attendances[total_records // 2].date
            old_att = attendances.filter(date__lt=mid_date)
            recent_att = attendances.filter(date__gte=mid_date)

            old_rate = old_att.filter(status='present').count() / old_att.count() if old_att.exists() else 0
            recent_rate = recent_att.filter(status='present').count() / recent_att.count() if recent_att.exists() else 0
            features['attendance_trend'] = float(np.clip((recent_rate - old_rate) * 2, -1, 1))
        else:
            features['attendance_trend'] = 0.0
    else:
        # NO DEFAULT VALUES - indicate missing data
        features['attendance_rate'] = None
        features['absences_count'] = None
        features['late_count'] = None
        features['unexcused_absence_rate'] = None
        features['consecutive_absences'] = None
        features['recent_attendance_rate'] = None
        features['attendance_trend'] = None

    # ============================================================
    # ACADEMIC PROGRESSION FEATURES (13-18)
    # ============================================================

    # 13. Exam vs assignment performance difference
    exam_grades = grades.filter(type='exam').values_list('value', flat=True)
    assignment_grades = grades.filter(type__in=['assignment', 'project']).values_list('value', flat=True)

    if exam_grades and assignment_grades:
        exam_avg = np.mean(list(exam_grades))
        assignment_avg = np.mean(list(assignment_grades))
        features['exam_vs_assignment_diff'] = float(exam_avg - assignment_avg)
    else:
        features['exam_vs_assignment_diff'] = None

    # 14. Number of unique subjects with grades
    unique_subjects = grades.values('subject').distinct().count()
    features['subjects_count'] = unique_subjects if unique_subjects > 0 else None

    # 15. Pass rate (percentage of grades >= 10)
    if grade_values:
        passed = sum(1 for g in grade_values if g >= 10)
        features['pass_rate'] = (passed / len(grade_values)) * 100
    else:
        features['pass_rate'] = None

    # 16. Best subject average
    if grades.exists():
        subject_avgs = grades.values('subject').annotate(avg=Avg('value')).order_by('-avg')
        if subject_avgs:
            features['best_subject_avg'] = float(subject_avgs[0]['avg'] or 0)
        else:
            features['best_subject_avg'] = None
    else:
        features['best_subject_avg'] = None

    # 17. Worst subject average
    if grades.exists():
        subject_avgs = grades.values('subject').annotate(avg=Avg('value')).order_by('avg')
        if subject_avgs:
            features['worst_subject_avg'] = float(subject_avgs[0]['avg'] or 0)
        else:
            features['worst_subject_avg'] = None
    else:
        features['worst_subject_avg'] = None

    # 18. Subject performance spread (best - worst)
    if features.get('best_subject_avg') is not None and features.get('worst_subject_avg') is not None:
        features['subject_spread'] = features['best_subject_avg'] - features['worst_subject_avg']
    else:
        features['subject_spread'] = None

    # ============================================================
    # TEMPORAL/ENGAGEMENT FEATURES (19-24)
    # ============================================================

    # 19. Weeks since enrollment
    if student.created_at:
        days_enrolled = (now - student.created_at).days
        features['weeks_enrolled'] = days_enrolled / 7
    else:
        features['weeks_enrolled'] = None

    # 20. Days since last grade
    last_grade = grades.order_by('-date').first()
    if last_grade and last_grade.date:
        days_since_grade = (now.date() - last_grade.date).days
        features['days_since_last_grade'] = days_since_grade
    else:
        features['days_since_last_grade'] = None

    # 21. Days since last attendance record
    last_attendance = attendances.order_by('-date').first()
    if last_attendance and last_attendance.date:
        days_since_attendance = (now.date() - last_attendance.date).days
        features['days_since_last_attendance'] = days_since_attendance
    else:
        features['days_since_last_attendance'] = None

    # 22. Activity frequency (records per week)
    total_records = grades.count() + attendances.count()
    if features.get('weeks_enrolled') and features['weeks_enrolled'] > 0:
        features['activity_per_week'] = total_records / features['weeks_enrolled']
    else:
        features['activity_per_week'] = None

    # 23. Has prediction history
    predictions = student.predictions.all()
    features['prediction_count'] = predictions.count()

    # 24. Previous risk level (last prediction risk score, or None)
    last_prediction = predictions.order_by('-created_at').first()
    if last_prediction:
        features['previous_risk_score'] = float(last_prediction.risk_score)
    else:
        features['previous_risk_score'] = None

    return features


def get_feature_completeness(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Analyze feature completeness for a student.

    Returns statistics about which features are available vs missing.
    """
    total = len(features)
    available = sum(1 for v in features.values() if v is not None)
    missing = [k for k, v in features.items() if v is None]

    return {
        'total_features': total,
        'available_features': available,
        'missing_features': missing,
        'completeness_rate': (available / total) * 100 if total > 0 else 0,
        'can_predict': available >= 5  # Minimum features required for prediction
    }
