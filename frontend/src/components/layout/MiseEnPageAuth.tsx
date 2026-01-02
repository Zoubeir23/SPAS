import { ReactNode } from 'react'

interface AuthLayoutProps {
  children: ReactNode
}

export default function MiseEnPageAuth({ children }: AuthLayoutProps) {
  return (
    <div className="relative flex min-h-screen w-full flex-col justify-center py-12 sm:px-6 lg:px-8 overflow-hidden">
      {/* Background Gradient Decoration */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-background-light dark:bg-background-dark">
        <div className="absolute top-0 -left-4 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-50"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl opacity-50"></div>
      </div>

      {children}

      {/* Footer */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <p className="text-center text-xs text-gray-500 dark:text-gray-500">
          © 2024 ISI - Institut Supérieur d'Informatique. Tous droits réservés.
        </p>
      </div>
    </div>
  )
}

