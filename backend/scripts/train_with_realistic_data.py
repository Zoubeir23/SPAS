#!/usr/bin/env python
"""
Script d'entraînement avec données réalistes.

Ce script permet d'entraîner le modèle ML avec différentes sources de données :
1. Données réalistes générées (basées sur statistiques éducatives réelles)
2. Données importées depuis CSV
3. Données des vrais étudiants en base de données

Usage:
    python scripts/train_with_realistic_data.py --source realistic
    python scripts/train_with_realistic_data.py --source csv --file data.csv
    python scripts/train_with_realistic_data.py --source database
"""
import os
import sys
import argparse
from datetime import datetime

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from apps.ml.models import MLModel, TrainingJob
from apps.ml.services import (
    DropoutRiskPredictor,
    generate_synthetic_training_data,
    generate_realistic_education_data,
    load_training_data_from_csv,
    load_training_data_from_database,
)


def train_model(source: str, csv_file: str = None, algorithm: str = 'random_forest', 
                n_samples: int = 2000, activate: bool = True):
    """
    Entraîne un modèle ML avec la source de données spécifiée.
    
    Args:
        source: 'synthetic', 'realistic', 'csv', ou 'database'
        csv_file: Chemin vers le fichier CSV (si source='csv')
        algorithm: Algorithme ML à utiliser
        n_samples: Nombre d'échantillons pour données synthétiques/réalistes
        activate: Activer le modèle après entraînement
    """
    print("=" * 70)
    print("🎓 SPAS - Entraînement du Modèle ML de Prédiction d'Abandon")
    print("=" * 70)
    print()
    
    # 1. Charger les données
    print(f"📊 Source de données: {source.upper()}")
    print("-" * 50)
    
    if source == 'synthetic':
        print(f"Génération de {n_samples} échantillons synthétiques (ancienne méthode)...")
        X, y = generate_synthetic_training_data(n_samples)
        print(f"✅ {len(X)} échantillons générés")
        
    elif source == 'realistic':
        print(f"Génération de {n_samples} échantillons réalistes...")
        print("  (Basé sur statistiques UNESCO/European Commission)")
        X, y = generate_realistic_education_data(n_samples)
        print(f"✅ {len(X)} échantillons générés")
        
    elif source == 'csv':
        if not csv_file:
            raise ValueError("--file est requis pour source=csv")
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"Fichier non trouvé: {csv_file}")
        print(f"Chargement depuis: {csv_file}")
        X, y, feature_names = load_training_data_from_csv(csv_file)
        print(f"✅ {len(X)} échantillons chargés avec {len(feature_names)} features")
        
    elif source == 'database':
        print("Chargement des étudiants depuis la base de données...")
        try:
            X, y = load_training_data_from_database()
            print(f"✅ {len(X)} étudiants chargés")
        except ValueError as e:
            print(f"⚠️  {e}")
            print("Fallback sur données réalistes...")
            X, y = generate_realistic_education_data(n_samples)
    else:
        raise ValueError(f"Source inconnue: {source}")
    
    # Afficher distribution des classes
    from collections import Counter
    class_counts = Counter(y)
    print(f"\n📈 Distribution des classes:")
    print(f"   - Low risk (0):    {class_counts[0]} ({class_counts[0]/len(y)*100:.1f}%)")
    print(f"   - Medium risk (1): {class_counts[1]} ({class_counts[1]/len(y)*100:.1f}%)")
    print(f"   - High risk (2):   {class_counts[2]} ({class_counts[2]/len(y)*100:.1f}%)")
    
    # 2. Entraîner le modèle
    print()
    print(f"🤖 Entraînement avec {algorithm}...")
    print("-" * 50)
    
    predictor = DropoutRiskPredictor()
    
    def progress_callback(progress, step, details=''):
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r   [{bar}] {progress:3d}% - {step}", end='', flush=True)
        if progress == 100:
            print()
    
    metrics = predictor.train(
        X, y,
        algorithm=algorithm,
        progress_callback=progress_callback
    )
    
    # 3. Afficher les résultats
    print()
    print("📊 Métriques du modèle:")
    print("-" * 50)
    print(f"   Accuracy:  {metrics['accuracy']:.2f}%")
    print(f"   Precision: {metrics['precision']:.2f}%")
    print(f"   Recall:    {metrics['recall']:.2f}%")
    print(f"   F1 Score:  {metrics['f1_score']:.2f}%")
    print(f"   CV Mean:   {metrics['cv_mean']:.2f}% (±{metrics['cv_std']:.2f}%)")
    
    # Feature importance
    if 'feature_importance' in metrics:
        print()
        print("🔍 Importance des features (top 5):")
        print("-" * 50)
        sorted_features = sorted(
            metrics['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for name, importance in sorted_features:
            bar = '█' * int(importance * 50)
            print(f"   {name:25s}: {importance:.3f} {bar}")
    
    # 4. Sauvegarder le modèle
    print()
    print("💾 Sauvegarde du modèle...")
    print("-" * 50)
    model_path = predictor.save_model()
    print(f"   Fichier: {model_path}")
    
    # 5. Créer l'entrée en base de données
    # Déterminer la version
    existing_versions = MLModel.objects.filter(
        name='DropoutRiskPredictor'
    ).values_list('version', flat=True)
    
    if existing_versions:
        try:
            max_version = max(int(v.split('.')[-1]) for v in existing_versions if v)
            new_version = f"1.0.{max_version + 1}"
        except:
            new_version = "1.1.0"
    else:
        new_version = "1.0.0"
    
    ml_model = MLModel.objects.create(
        name='DropoutRiskPredictor',
        version=new_version,
        status=MLModel.Status.INACTIVE,
        accuracy=metrics['accuracy'],
        precision=metrics['precision'],
        recall=metrics['recall'],
        f1_score=metrics['f1_score'],
        trained_at=timezone.now(),
        training_data_size=len(X)
    )
    
    print(f"   Modèle enregistré: {ml_model}")
    
    # 6. Activer si demandé
    if activate:
        ml_model.activate()
        print(f"   ✅ Modèle activé!")
    
    # 7. Test de prédiction
    print()
    print("🧪 Test de prédiction...")
    print("-" * 50)
    
    # Étudiant à risque
    test_student_high_risk = {
        'average_grade': 7,
        'attendance_rate': 55,
        'assignments_completed': 40,
        'late_submissions': 6,
        'absences_count': 12,
        'consecutive_absences': 3,
        'grade_trend': -0.35,
        'participation_score': 35,
        'weeks_enrolled': 12,
        'failed_subjects': 3,
    }
    
    # Bon étudiant
    test_student_good = {
        'average_grade': 15,
        'attendance_rate': 95,
        'assignments_completed': 92,
        'late_submissions': 0,
        'absences_count': 2,
        'consecutive_absences': 0,
        'grade_trend': 0.1,
        'participation_score': 85,
        'weeks_enrolled': 16,
        'failed_subjects': 0,
    }
    
    pred_high = predictor.predict_risk(test_student_high_risk)
    pred_good = predictor.predict_risk(test_student_good)
    
    print(f"   Étudiant à risque: score={pred_high['risk_score']:.1f}, level={pred_high['risk_level']}")
    print(f"   Bon étudiant:      score={pred_good['risk_score']:.1f}, level={pred_good['risk_level']}")
    
    if pred_high['risk_score'] > pred_good['risk_score']:
        print("   ✅ Prédictions cohérentes!")
    else:
        print("   ⚠️ Les prédictions semblent incohérentes, vérifier les données")
    
    print()
    print("=" * 70)
    print("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS!")
    print("=" * 70)
    print(f"\nModèle: {ml_model.name} v{ml_model.version}")
    print(f"Accuracy: {metrics['accuracy']:.2f}%")
    print(f"Fichier: {model_path}")
    
    return ml_model, metrics


def compare_data_sources():
    """Compare les performances des différentes sources de données."""
    print()
    print("=" * 70)
    print("📊 COMPARAISON DES SOURCES DE DONNÉES")
    print("=" * 70)
    print()
    
    results = {}
    
    # Test avec données synthétiques
    print("1. Données synthétiques (ancienne méthode)...")
    X_syn, y_syn = generate_synthetic_training_data(1000)
    predictor_syn = DropoutRiskPredictor()
    metrics_syn = predictor_syn.train(X_syn, y_syn)
    results['synthetic'] = metrics_syn['accuracy']
    print(f"   Accuracy: {metrics_syn['accuracy']:.2f}%")
    
    # Test avec données réalistes
    print("\n2. Données réalistes (nouvelle méthode)...")
    X_real, y_real = generate_realistic_education_data(2000)
    predictor_real = DropoutRiskPredictor()
    metrics_real = predictor_real.train(X_real, y_real)
    results['realistic'] = metrics_real['accuracy']
    print(f"   Accuracy: {metrics_real['accuracy']:.2f}%")
    
    print()
    print("📈 RÉSUMÉ:")
    print("-" * 50)
    for source, accuracy in results.items():
        print(f"   {source:15s}: {accuracy:.2f}%")
    
    best = max(results.items(), key=lambda x: x[1])
    print(f"\n✅ Meilleure source: {best[0]} ({best[1]:.2f}%)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Entraîner le modèle ML avec différentes sources de données'
    )
    parser.add_argument(
        '--source', 
        choices=['synthetic', 'realistic', 'csv', 'database', 'compare'],
        default='realistic',
        help='Source des données d\'entraînement'
    )
    parser.add_argument(
        '--file', 
        type=str,
        help='Chemin vers le fichier CSV (si source=csv)'
    )
    parser.add_argument(
        '--algorithm',
        choices=['random_forest', 'gradient_boosting', 'logistic_regression'],
        default='random_forest',
        help='Algorithme ML à utiliser'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=2000,
        help='Nombre d\'échantillons (pour synthetic/realistic)'
    )
    parser.add_argument(
        '--no-activate',
        action='store_true',
        help='Ne pas activer le modèle après entraînement'
    )
    
    args = parser.parse_args()
    
    if args.source == 'compare':
        compare_data_sources()
    else:
        train_model(
            source=args.source,
            csv_file=args.file,
            algorithm=args.algorithm,
            n_samples=args.samples,
            activate=not args.no_activate
        )
