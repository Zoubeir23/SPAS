import { InputHTMLAttributes, forwardRef, useId } from 'react'
import { clsx } from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  leftIcon?: string
  rightIcon?: string
  onRightIconClick?: () => void
  rightIconLabel?: string
}

const ChampSaisie = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      leftIcon,
      rightIcon,
      onRightIconClick,
      rightIconLabel,
      className,
      id,
      ...props
    },
    ref
  ) => {
    const generatedId = useId()
    const inputId = id || generatedId
    const errorId = `${inputId}-error`

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
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <span className="material-symbols-outlined text-gray-400 dark:text-gray-500 text-[20px]">
                {leftIcon}
              </span>
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : undefined}
            className={clsx(
              'block w-full rounded-lg border-0 py-3 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary dark:bg-background-dark dark:ring-gray-600 dark:text-white sm:text-sm sm:leading-6 bg-[#f8f9fb] dark:bg-opacity-50 transition-all',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              !leftIcon && !rightIcon && 'px-4',
              error &&
                'ring-red-500 focus:ring-red-500 dark:ring-red-500 dark:focus:ring-red-500',
              className
            )}
            {...props}
          />
<<<<<<< Updated upstream
          {rightIcon &&
            (onRightIconClick ? (
              <button
                type="button"
                className="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer bg-transparent border-0 p-0"
                onClick={onRightIconClick}
                aria-label={rightIconLabel || 'Toggle input action'}
=======
          {rightIcon && (
            <div
              className={clsx(
                'absolute inset-y-0 right-0 flex items-center pr-4',
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
>>>>>>> Stashed changes
              >
                <span className="material-symbols-outlined text-[20px] text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  {rightIcon}
                </span>
              </button>
            ) : (
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <span className="material-symbols-outlined text-[20px] text-gray-400">
                  {rightIcon}
                </span>
              </div>
            ))}
        </div>
        {error && (
          <p
            id={errorId}
            className="mt-1 text-sm text-red-600 dark:text-red-400"
          >
            {error}
          </p>
        )}
      </div>
    )
  }
)

ChampSaisie.displayName = 'ChampSaisie'

export default ChampSaisie
