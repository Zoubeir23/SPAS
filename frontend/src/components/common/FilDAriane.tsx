import { Link } from 'react-router-dom'
import { clsx } from 'clsx'

interface BreadcrumbItem {
  label: string
  path?: string
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  className?: string
}

export default function FilDAriane({ items, className }: BreadcrumbsProps) {
  return (
    <nav className={clsx('flex items-center', className)}>
      <ol className="flex items-center space-x-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-center">
            {index > 0 && (
              <span className="material-symbols-outlined text-[16px] text-gray-500 mx-2">
                chevron_right
              </span>
            )}
            {item.path && index < items.length - 1 ? (
              <Link
                to={item.path}
                className="text-sm font-medium text-gray-600 hover:text-primary transition-colors dark:text-gray-400 dark:hover:text-blue-400"
              >
                {item.label}
              </Link>
            ) : (
              <span
                className={clsx(
                  'text-sm',
                  index === items.length - 1
                    ? 'font-semibold text-primary dark:text-blue-400'
                    : 'font-medium text-gray-600 dark:text-gray-400'
                )}
              >
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}

