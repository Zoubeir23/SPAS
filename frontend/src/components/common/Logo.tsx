import { useState } from 'react'
import { clsx } from 'clsx'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'compact' | 'full'
  className?: string
  showText?: boolean
}

const sizeClasses = {
  sm: 'h-8 w-8',
  md: 'h-12 w-12',
  lg: 'h-16 w-16',
  xl: 'h-24 w-24',
}

const textSizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-2xl',
}

export default function Logo({
  size = 'md',
  variant = 'default',
  className,
  showText = true,
}: LogoProps) {
  const [imageError, setImageError] = useState(false)
  const logoSize = sizeClasses[size]
  const textSize = textSizeClasses[size]

  if (variant === 'compact') {
    return (
      <div className={clsx('flex items-center gap-2', className)}>
        {imageError ? (
          <div className={clsx(logoSize, 'bg-primary/10 rounded-lg flex items-center justify-center')}>
            <span className={clsx('text-primary font-bold', textSize)}>ISI</span>
          </div>
        ) : (
          <img
            src="/images/image.png"
            alt="Logo ISI - Institut Supérieur d'Informatique"
            className={clsx(logoSize, 'object-contain')}
            onError={() => setImageError(true)}
          />
        )}
        {showText && (
          <div className="flex flex-col">
            <span className="text-slate-900 dark:text-white text-sm font-bold leading-tight">
              ISI Analytics
            </span>
            <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">
              Système Académique
            </span>
          </div>
        )}
      </div>
    )
  }

  if (variant === 'full') {
    return (
      <div className={clsx('flex flex-col items-center', className)}>
        <div className={clsx('mb-4', logoSize)}>
          {imageError ? (
            <div className={clsx('w-full h-full bg-primary/10 rounded-lg flex items-center justify-center')}>
              <span className={clsx('text-primary font-bold', textSize)}>ISI</span>
            </div>
          ) : (
            <img
              src="/images/image.png"
              alt="Logo ISI - Institut Supérieur d'Informatique"
              className={clsx('w-full h-full object-contain')}
              onError={() => setImageError(true)}
            />
          )}
        </div>
        {showText && (
          <>
            <h1 className="text-center text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
              GROUPE ISI
            </h1>
            <p className="mt-1 text-center text-sm text-gray-600 dark:text-gray-400">
              Institut Supérieur d'Informatique
            </p>
          </>
        )}
      </div>
    )
  }

  // Variant par défaut
  return (
    <div className={clsx('flex items-center justify-center', className)}>
      {imageError ? (
        <div className={clsx(logoSize, 'bg-primary/10 rounded-lg flex items-center justify-center')}>
          <span className={clsx('text-primary font-bold', textSize)}>ISI</span>
        </div>
      ) : (
        <img
          src="/images/image.png"
          alt="Logo ISI - Institut Supérieur d'Informatique"
          className={clsx(logoSize, 'object-contain')}
          onError={() => setImageError(true)}
        />
      )}
    </div>
  )
}

