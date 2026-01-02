import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from 'react-router-dom'
import {
  forgotPasswordSchema,
  type ForgotPasswordFormData,
} from '@/utils/validators'
import { authService } from '@/api/services/authService'
import MiseEnPageAuth from '@/components/layout/MiseEnPageAuth'
import ChampSaisie from '@/components/common/ChampSaisie'
import Bouton from '@/components/common/Bouton'
import Alerte from '@/components/common/Alerte'
import Logo from '@/components/common/Logo'
import { ROUTES } from '@/utils/constants'

export default function MotDePasseOublie() {
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setError(null)
    setIsLoading(true)

    try {
      await authService.forgotPassword(data.email)
      setSuccess(true)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Une erreur est survenue. Veuillez réessayer.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <MiseEnPageAuth>
      {/* Header / Logo Area */}
      <div className="mb-8 flex flex-col items-center gap-3">
        <Logo size="md" variant="compact" showText={true} />
      </div>

      {/* Main Card */}
      <main className="w-full max-w-[480px] bg-white dark:bg-[#1c212e] rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none border border-[#e8ebf2] dark:border-[#2d3748] overflow-hidden">
        {/* Card Header */}
        <div className="px-8 pt-8 pb-4 text-center">
          <div className="mx-auto mb-6 flex size-14 items-center justify-center rounded-full bg-blue-50 dark:bg-blue-900/20">
            <span className="material-symbols-outlined text-[32px] text-primary dark:text-blue-400">
              lock_reset
            </span>
          </div>
          <h2 className="text-[#0f121a] dark:text-white text-2xl font-bold leading-tight tracking-[-0.015em] mb-3">
            Réinitialisation du mot de passe
          </h2>
          <p className="text-[#536493] dark:text-gray-400 text-base font-normal leading-normal">
            Entrez votre adresse email institutionnelle. Nous vous enverrons un
            lien pour réinitialiser votre mot de passe.
          </p>
        </div>

        {/* Form Content */}
        <div className="px-8 pb-8 pt-2 flex flex-col gap-6">
          {error && (
            <Alerte type="error" onClose={() => setError(null)}>
              {error}
            </Alerte>
          )}

          {success ? (
            <>
              <Alerte type="success" title="Email envoyé !">
                Un lien de réinitialisation a été envoyé à votre adresse email.
                Veuillez vérifier votre boîte de réception.
              </Alerte>
              <Link to={ROUTES.LOGIN}>
                <Bouton variant="primary" size="md" className="w-full">
                  Retour à la connexion
                </Bouton>
              </Link>
            </>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Email ChampSaisie */}
              <ChampSaisie
                label="Adresse Email"
                type="email"
                placeholder="exemple@isi.edu"
                leftIcon="mail"
                error={errors.email?.message}
                {...register('email')}
              />

              {/* Submit Bouton */}
              <Bouton
                type="submit"
                variant="primary"
                size="md"
                isLoading={isLoading}
                className="w-full"
              >
                Envoyer le lien
              </Bouton>

              {/* Back Link */}
              <div className="text-center pt-2">
                <Link
                  to={ROUTES.LOGIN}
                  className="inline-flex items-center gap-2 text-[#536493] dark:text-gray-400 hover:text-primary dark:hover:text-blue-400 text-sm font-medium leading-normal transition-colors group"
                >
                  <span className="material-symbols-outlined text-[18px] transition-transform group-hover:-translate-x-1">
                    arrow_back
                  </span>
                  Retour à la connexion
                </Link>
              </div>
            </form>
          )}
        </div>

        {/* Optional Visual Divider or Footer in card */}
        <div className="h-1 w-full bg-gradient-to-r from-transparent via-[#e8ebf2] dark:via-[#2d3748] to-transparent opacity-50"></div>
        <div className="px-8 py-4 bg-[#f8f9fb] dark:bg-[#171b26] text-center">
          <p className="text-xs text-[#536493] dark:text-gray-500">
            Besoin d'aide ? Contactez{' '}
            <a
              className="underline hover:text-primary dark:hover:text-blue-400"
              href="#"
            >
              le support informatique
            </a>
            .
          </p>
        </div>
      </main>
    </MiseEnPageAuth>
  )
}

