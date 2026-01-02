import { InputHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  leftIcon?: string
  rightIcon?: string
  onRightIconClick?: () => void
}

const ChampSaisie = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      leftIcon,
      rightIcon,
      onRightIconClick,
      className,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium leading-6 text-gray-900 dark:text-gray-200 mb-2"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="material-symbols-outlined text-gray-400 dark:text-gray-500">
                {leftIcon}
              </span>
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={clsx(
              'block w-full rounded-lg border-0 py-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary dark:bg-background-dark dark:ring-gray-600 dark:text-white sm:text-sm sm:leading-6 bg-[#f8f9fb] dark:bg-opacity-50 transition-all',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error &&
                'ring-red-500 focus:ring-red-500 dark:ring-red-500 dark:focus:ring-red-500',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div
              className={clsx(
                'absolute inset-y-0 right-0 flex items-center pr-3',
                onRightIconClick && 'cursor-pointer'
              )}
              onClick={onRightIconClick}
            >
              <span
                className={clsx(
                  'material-symbols-outlined text-[20px]',
                  onRightIconClick
                    ? 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                    : 'text-gray-400'
                )}
              >
                {rightIcon}
              </span>
            </div>
          )}
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
      </div>
    )
  }
)

ChampSaisie.displayName = 'ChampSaisie'

export default ChampSaisie

