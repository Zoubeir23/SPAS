import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from 'react-router-dom'
import { loginSchema, type LoginFormData } from '@/utils/validators'
import { useAuth } from '@/hooks/useAuth'
import { usePasswordVisibility } from '@/hooks/usePasswordVisibility'
import MiseEnPageAuth from '@/components/layout/MiseEnPageAuth'
import ChampSaisie from '@/components/common/ChampSaisie'
import Bouton from '@/components/common/Bouton'
import CaseCochee from '@/components/common/CaseCochee'
import Alerte from '@/components/common/Alerte'
import Logo from '@/components/common/Logo'
import { ROUTES } from '@/utils/constants'
import { APP_DESCRIPTION } from '@/utils/constants'

export default function Connexion() {
  const [error, setError] = useState<string | null>(null)
  const { login, isLoading } = useAuth()
  const passwordVisibility = usePasswordVisibility()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false,
    },
  })

  const onSubmit = async (data: LoginFormData) => {
    setError(null)
    const result = await login({
      email: data.email,
      password: data.password,
      rememberMe: data.rememberMe,
    })

    if (!result.success) {
      setError(result.error || 'Une erreur est survenue lors de la connexion')
    }
  }

  return (
    <MiseEnPageAuth>
      {/* Header / Logo Area */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center mb-8">
        <div className="w-24 h-24 rounded-full bg-white dark:bg-surface-dark shadow-sm flex items-center justify-center mb-6 border border-slate-100 dark:border-slate-700">
          <Logo size="lg" variant="default" showText={false} />
        </div>
        <h2 className="text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
          Connexion
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          {APP_DESCRIPTION}
        </p>
      </div>

      {/* Login Card */}
      <div className="mt-2 sm:mx-auto sm:w-full sm:max-w-[480px]">
        <div className="bg-white dark:bg-surface-dark py-10 px-6 shadow-xl shadow-slate-200/50 dark:shadow-black/30 rounded-xl sm:px-12 border border-slate-100 dark:border-slate-700">
          {error && (
            <div className="mb-6">
              <Alerte type="error" onClose={() => setError(null)}>
                {error}
              </Alerte>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email Field */}
            <ChampSaisie
              label="Adresse email"
              type="email"
              placeholder="nom@exemple.com"
              autoComplete="email"
              error={errors.email?.message}
              {...register('email')}
            />

            {/* Password Field */}
            <div>
              <ChampSaisie
                label="Mot de passe"
                type={passwordVisibility.type}
                placeholder="••••••••"
                autoComplete="current-password"
                error={errors.password?.message}
                rightIcon={passwordVisibility.icon}
                onRightIconClick={passwordVisibility.toggle}
                rightIconLabel={
                  passwordVisibility.isVisible
                    ? 'Masquer le mot de passe'
                    : 'Afficher le mot de passe'
                }
                {...register('password')}
              />
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <CaseCochee
                label="Se souvenir de moi"
                {...register('rememberMe')}
              />
              <div className="text-sm leading-6">
                <Link
                  to={ROUTES.FORGOT_PASSWORD}
                  className="font-medium text-primary hover:text-primary-hover hover:underline"
                >
                  Mot de passe oublié ?
                </Link>
              </div>
            </div>

            {/* Submit Button */}
            <div>
              <Bouton
                type="submit"
                variant="primary"
                size="md"
                isLoading={isLoading}
                className="w-full"
              >
                Se connecter
              </Bouton>
            </div>
          </form>

          {/* Help/Support Link */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200 dark:border-gray-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white dark:bg-surface-dark px-2 text-gray-500 dark:text-gray-400">
                  Besoin d'aide ?
                </span>
              </div>
            </div>
            <div className="mt-6 flex justify-center gap-4">
              <a
                className="flex items-center gap-2 text-sm text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                href="#"
              >
                <span className="material-symbols-outlined text-[18px]">
                  support_agent
                </span>
                Contacter le support DSI
              </a>
            </div>
          </div>
        </div>
      </div>
    </MiseEnPageAuth>
  )
}

