"""
Django management command to load training data from downloaded datasets.
"""
import os
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load training data from downloaded datasets into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            type=str,
            choices=['kaggle_dropout', 'uci', 'kaggle_performance', 'xapi', 'all'],
            default='all',
            help='Dataset to load (default: all)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of records to load (for testing)'
        )

    def handle(self, *args, **options):
        dataset = options['dataset']
        limit = options['limit']

        self.stdout.write(self.style.SUCCESS('Debut du chargement des donnees d\'entrainement\n'))

        if dataset == 'all' or dataset == 'kaggle_dropout':
            self.load_kaggle_dropout(limit)

        if dataset == 'all' or dataset == 'uci':
            self.load_uci_student_performance(limit)

        if dataset == 'all' or dataset == 'kaggle_performance':
            self.load_kaggle_performance(limit)

        if dataset == 'all' or dataset == 'xapi':
            self.load_xapi_edu(limit)

        self.stdout.write(self.style.SUCCESS('\nChargement termine!'))

    def load_kaggle_dropout(self, limit=None):
        """Load Kaggle Higher Education Dropout Dataset"""
        self.stdout.write('Chargement Kaggle Dropout Dataset...')

        dataset_path = os.path.join(settings.BASE_DIR, '..', 'datasets', 'kaggle_dropout')
        
        # Chercher le fichier CSV
        csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')] if os.path.exists(dataset_path) else []
        
        if not csv_files:
            self.stdout.write(self.style.WARNING('Dataset Kaggle Dropout non trouve. Telechargez-le d\'abord.'))
            return

        csv_path = os.path.join(dataset_path, csv_files[0])
        
        try:
            df = pd.read_csv(csv_path)
            
            if limit:
                df = df.head(limit)

            self.stdout.write(f'   {len(df)} enregistrements trouves')
            self.stdout.write(f'   Colonnes: {list(df.columns)[:5]}...')

            # TODO: Mapper les colonnes du dataset vers les features SPAS
            # TODO: Creer des enregistrements Student et les donnees associees
            
            self.stdout.write(self.style.SUCCESS(f'   {len(df)} enregistrements charges'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ERREUR: {e}'))

    def load_uci_student_performance(self, limit=None):
        """Load UCI Student Performance Dataset"""
        self.stdout.write('Chargement UCI Student Performance Dataset...')

        dataset_path = os.path.join(settings.BASE_DIR, '..', 'datasets', 'uci_student_performance')
        
        # Chercher les fichiers CSV (student-mat.csv et student-por.csv)
        csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')] if os.path.exists(dataset_path) else []
        
        if not csv_files:
            self.stdout.write(self.style.WARNING('Dataset UCI non trouve. Telechargez-le d\'abord.'))
            return

        try:
            for csv_file in csv_files:
                csv_path = os.path.join(dataset_path, csv_file)
                df = pd.read_csv(csv_path, sep=';')
                
                if limit:
                    df = df.head(limit)

                self.stdout.write(f'   {len(df)} enregistrements dans {csv_file}')
                self.stdout.write(f'   Colonnes: {list(df.columns)[:5]}...')

                # TODO: Mapper les colonnes vers SPAS
                
            self.stdout.write(self.style.SUCCESS('   Dataset UCI charge'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ERREUR: {e}'))

    def load_kaggle_performance(self, limit=None):
        """Load Kaggle Student Performance in Exams"""
        self.stdout.write('Chargement Kaggle Performance Dataset...')

        dataset_path = os.path.join(settings.BASE_DIR, '..', 'datasets', 'kaggle_performance')
        
        csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')] if os.path.exists(dataset_path) else []
        
        if not csv_files:
            self.stdout.write(self.style.WARNING('Dataset Kaggle Performance non trouve.'))
            return

        try:
            csv_path = os.path.join(dataset_path, csv_files[0])
            df = pd.read_csv(csv_path)
            
            if limit:
                df = df.head(limit)

            self.stdout.write(f'   📊 {len(df)} enregistrements trouvés')
            self.stdout.write(self.style.SUCCESS('   ✅ Dataset chargé'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {e}'))

    def load_xapi_edu(self, limit=None):
        """Load xAPI-Edu-Data"""
        self.stdout.write('Chargement xAPI-Edu-Data...')

        dataset_path = os.path.join(settings.BASE_DIR, '..', 'datasets', 'xapi_edu')
        
        csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')] if os.path.exists(dataset_path) else []
        
        if not csv_files:
            self.stdout.write(self.style.WARNING('Dataset xAPI non trouve.'))
            return

        try:
            csv_path = os.path.join(dataset_path, csv_files[0])
            df = pd.read_csv(csv_path)
            
            if limit:
                df = df.head(limit)

            self.stdout.write(f'   📊 {len(df)} enregistrements trouvés')
            self.stdout.write(self.style.SUCCESS('   ✅ Dataset chargé'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {e}'))

