import { ReactNode, useEffect } from 'react'
import { clsx } from 'clsx'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
}

export default function Modale({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
}: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const sizes = {
    sm: 'sm:max-w-md',
    md: 'sm:max-w-2xl',
    lg: 'sm:max-w-4xl',
    xl: 'sm:max-w-6xl',
    full: 'sm:max-w-full',
  }

  return (
    <div
      className="fixed inset-0 z-50 w-screen overflow-y-auto"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-gray-900/75 transition-opacity"
        aria-hidden="true"
      />

      {/* Modal Container */}
      <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        {/* Modal Panel */}
        <div
          className={clsx(
            'relative transform overflow-hidden rounded-xl bg-white dark:bg-background-dark text-left shadow-xl transition-all sm:my-8 sm:w-full',
            sizes[size],
            'flex flex-col max-h-[90vh]'
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Modal Header */}
          {title && (
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-background-dark sticky top-0 z-20">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {title}
              </h2>
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="rounded-full p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors focus:outline-none"
                  type="button"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              )}
            </div>
          )}

          {/* Modal Body */}
          <div className="px-6 py-6 overflow-y-auto bg-background-light dark:bg-[#0f111a] flex-1">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}

