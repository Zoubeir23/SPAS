import { clsx } from 'clsx'
import Modale from '@/components/modals/Modale'
import Bouton from './Bouton'

interface ModaleConfirmationProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void | Promise<void>
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
  isLoading?: boolean
}

export default function ModaleConfirmation({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirmation',
  message,
  confirmText = 'Confirmer',
  cancelText = 'Annuler',
  variant = 'danger',
  isLoading = false,
}: ModaleConfirmationProps) {
  const handleConfirm = async () => {
    await onConfirm()
    onClose()
  }

  const iconColors = {
    danger: 'text-red-600 dark:text-red-400',
    warning: 'text-orange-600 dark:text-orange-400',
    info: 'text-blue-600 dark:text-blue-400',
  }

  const iconNames = {
    danger: 'warning',
    warning: 'error_outline',
    info: 'info',
  }

  const buttonVariants: Record<string, 'primary' | 'secondary' | 'outline' | 'danger' | 'warning'> = {
    danger: 'danger',
    warning: 'warning',
    info: 'primary',
  }

  return (
    <Modale isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <div className="space-y-6">
        {/* Icon and Message */}
        <div className="flex flex-col items-center text-center space-y-4">
          <div className={clsx(
            'flex items-center justify-center w-16 h-16 rounded-full',
            variant === 'danger' && 'bg-red-50 dark:bg-red-900/20',
            variant === 'warning' && 'bg-orange-50 dark:bg-orange-900/20',
            variant === 'info' && 'bg-blue-50 dark:bg-blue-900/20'
          )}>
            <span className={`material-symbols-outlined text-4xl ${iconColors[variant]}`}>
              {iconNames[variant]}
            </span>
          </div>
          <p className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
            {message}
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Bouton
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isLoading}
          >
            {cancelText}
          </Bouton>
          <Bouton
            type="button"
            variant={buttonVariants[variant]}
            onClick={handleConfirm}
            isLoading={isLoading}
            disabled={isLoading}
          >
            {confirmText}
          </Bouton>
        </div>
      </div>
    </Modale>
  )
}

