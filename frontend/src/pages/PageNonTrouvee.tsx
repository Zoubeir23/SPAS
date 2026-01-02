import { Link } from 'react-router-dom'
import { ROUTES } from '@/utils/constants'
import Bouton from '@/components/common/Bouton'

export default function PageNonTrouvee() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">
          404
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          Page non trouvée
        </p>
        <Link to={ROUTES.LOGIN}>
          <Bouton variant="primary">Retour à l'accueil</Bouton>
        </Link>
      </div>
    </div>
  )
}

