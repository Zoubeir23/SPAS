import { InputHTMLAttributes } from 'react'
import { clsx } from 'clsx'

interface SearchBarProps extends InputHTMLAttributes<HTMLInputElement> {
  onSearch?: (query: string) => void
}

export default function BarreRecherche({
  className,
  onSearch,
  ...props
}: SearchBarProps) {
  return (
    <div className={clsx('relative', className)}>
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <span className="material-symbols-outlined text-gray-400">search</span>
      </div>
      <input
        type="search"
        className="block w-full pl-10 pr-4 py-2 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder-gray-400 dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500/30"
        {...props}
      />
    </div>
  )
}

