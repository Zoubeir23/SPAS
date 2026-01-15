"""
Script pour télécharger les datasets recommandés pour SPAS.
"""
import os
import sys
import urllib.request
import zipfile
import logging

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_uci_student_performance():
    """Télécharge UCI Student Performance Dataset"""
    logger.info("Telechargement UCI Student Performance...")
    
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00320/student.zip"
    output_dir = "datasets/uci_student_performance"
    
    os.makedirs(output_dir, exist_ok=True)
    
    zip_path = os.path.join(output_dir, "student.zip")
    
    try:
        urllib.request.urlretrieve(url, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        os.remove(zip_path)
        logger.info(f"OK Dataset sauvegarde dans {output_dir}/")
        return True
    except Exception as e:
        logger.error(f"ERREUR lors du telechargement UCI: {e}")
        return False


def download_kaggle_dropout_dataset():
    """Télécharge Kaggle Student Dropout Dataset"""
    logger.info("Telechargement Kaggle Dropout Dataset...")
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        output_dir = "datasets/kaggle_dropout"
        os.makedirs(output_dir, exist_ok=True)
        
        api.dataset_download_files(
            'thedevastator/higher-education-predictors-of-student-retention',
            path=output_dir,
            unzip=True
        )
        
        logger.info(f"OK Dataset sauvegarde dans {output_dir}/")
        return True
    except ImportError:
        logger.warning("ATTENTION: Kaggle API non installee. Installez avec: pip install kaggle")
        logger.info("Vous pouvez telecharger manuellement depuis:")
        logger.info("   https://www.kaggle.com/datasets/thedevastator/higher-education-predictors-of-student-retention")
        return False
    except Exception as e:
        logger.error(f"ERREUR lors du telechargement Kaggle Dropout: {e}")
        logger.info("Assurez-vous d'avoir configure ~/.kaggle/kaggle.json")
        return False


def download_kaggle_performance_dataset():
    """Télécharge Kaggle Student Performance in Exams"""
    logger.info("Telechargement Kaggle Performance Dataset...")
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        output_dir = "datasets/kaggle_performance"
        os.makedirs(output_dir, exist_ok=True)
        
        api.dataset_download_files(
            'spscientist/students-performance-in-exams',
            path=output_dir,
            unzip=True
        )
        
        logger.info(f"OK Dataset sauvegarde dans {output_dir}/")
        return True
    except ImportError:
        logger.warning("ATTENTION: Kaggle API non installee.")
        return False
    except Exception as e:
        logger.error(f"ERREUR lors du telechargement Kaggle Performance: {e}")
        return False


def download_xapi_edu_data():
    """Télécharge xAPI-Edu-Data"""
    logger.info("Telechargement xAPI-Edu-Data...")
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        output_dir = "datasets/xapi_edu"
        os.makedirs(output_dir, exist_ok=True)
        
        api.dataset_download_files(
            'aljarah/xAPI-Edu-Data',
            path=output_dir,
            unzip=True
        )
        
        logger.info(f"OK Dataset sauvegarde dans {output_dir}/")
        return True
    except ImportError:
        logger.warning("ATTENTION: Kaggle API non installee.")
        return False
    except Exception as e:
        logger.error(f"ERREUR lors du telechargement xAPI-Edu: {e}")
        return False


if __name__ == "__main__":
    print("Debut telechargement datasets pour SPAS\n")
    
    # Créer dossier principal
    os.makedirs("datasets", exist_ok=True)
    
    results = {}
    
    try:
        # Dataset 1: UCI
        results['uci'] = download_uci_student_performance()
        print()
        
        # Dataset 2: Kaggle Dropout (PRINCIPAL)
        results['kaggle_dropout'] = download_kaggle_dropout_dataset()
        print()
        
        # Dataset 3: Kaggle Performance
        results['kaggle_performance'] = download_kaggle_performance_dataset()
        print()
        
        # Dataset 4: xAPI
        results['xapi'] = download_xapi_edu_data()
        print()
        
        # Résumé
        print("=" * 60)
        print("RESUME DU TELECHARGEMENT")
        print("=" * 60)
        for name, success in results.items():
            status = "OK" if success else "ECHEC"
            print(f"{status} {name}: {'Succes' if success else 'Echec'}")
        
        successful = sum(results.values())
        total = len(results)
        print(f"\n{successful}/{total} datasets telecharges avec succes")
        
        if successful > 0:
            print(f"Localisation: {os.path.abspath('datasets')}/")
        
    except Exception as e:
        logger.error(f"ERREUR generale: {e}")
        print("\nAssurez-vous d'avoir:")
        print("   1. Installe kaggle: pip install kaggle")
        print("   2. Configure votre API key dans ~/.kaggle/kaggle.json")
        print("   3. Une connexion internet stable")

