import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface CardProps {
  children: ReactNode
  className?: string
  title?: string
  subtitle?: string
  icon?: string
  iconColor?: string
  hover?: boolean
}

export default function Carte({
  children,
  className,
  title,
  subtitle,
  icon,
  iconColor = 'primary',
  hover = false,
}: CardProps) {
  const iconColors = {
    primary: 'bg-blue-50 text-primary dark:bg-blue-900/20 dark:text-blue-300',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-300',
    orange: 'bg-orange-50 text-orange-600 dark:bg-orange-900/20 dark:text-orange-300',
    green: 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-300',
    red: 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-300',
  }

  return (
    <div
      className={clsx(
        'rounded-xl border border-gray-200 bg-white dark:bg-surface-dark dark:border-gray-800 shadow-sm',
        hover && 'transition-shadow hover:shadow-md',
        className
      )}
    >
      {(title || icon) && (
        <div className="p-6 pb-4">
          <div className="flex items-center justify-between mb-4">
            {title && (
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {title}
              </p>
            )}
            {icon && (
              <span
                className={clsx(
                  'rounded-full p-2',
                  iconColors[iconColor as keyof typeof iconColors] ||
                    iconColors.primary
                )}
              >
                <span className="material-symbols-outlined text-[20px]">
                  {icon}
                </span>
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              {subtitle}
            </p>
          )}
        </div>
      )}
      <div className={title || icon ? 'px-6 pb-6' : 'p-6'}>{children}</div>
    </div>
  )
}

