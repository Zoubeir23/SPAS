import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface BadgeProps {
  children: ReactNode
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'primary'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export default function Badge({
  children,
  variant = 'primary',
  size = 'md',
  className,
}: BadgeProps) {
  const variants = {
    success:
      'bg-success-100 text-success-800 dark:bg-success-900/20 dark:text-success-400',
    warning:
      'bg-warning-100 text-warning-800 dark:bg-warning-900/20 dark:text-warning-400',
    danger: 'bg-danger-100 text-danger-800 dark:bg-danger-900/20 dark:text-danger-400',
    info: 'bg-info-100 text-info-800 dark:bg-info-900/20 dark:text-info-400',
    primary:
      'bg-primary/10 text-primary dark:bg-primary/20 dark:text-info-400',
  }

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full font-medium',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  )
}

