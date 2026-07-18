import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface AlertProps {
  type?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  children: ReactNode
  className?: string
  onClose?: () => void
}

export default function Alerte({
  type = 'info',
  title,
  children,
  className,
  onClose,
}: AlertProps) {
  const styles = {
    success:
      'bg-success-50 text-success-800 border-success-200 dark:bg-success-900/20 dark:text-success-400 dark:border-success-800',
    error:
      'bg-danger-50 text-danger-800 border-danger-200 dark:bg-danger-900/20 dark:text-danger-400 dark:border-danger-800',
    warning:
      'bg-warning-50 text-warning-800 border-warning-200 dark:bg-warning-900/20 dark:text-warning-400 dark:border-warning-800',
    info: 'bg-info-50 text-info-800 border-info-200 dark:bg-info-900/20 dark:text-info-400 dark:border-info-800',
  }

  return (
    <div
      className={clsx(
        'rounded-lg border p-4',
        styles[type],
        className
      )}
      role="alert"
    >
      <div className="flex items-start">
        <div className="flex-1">
          {title && (
            <h3 className="font-semibold mb-1">{title}</h3>
          )}
          <div className="text-sm">{children}</div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-current opacity-70 hover:opacity-100"
            aria-label="Fermer"
          >
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        )}
      </div>
    </div>
  )
}

