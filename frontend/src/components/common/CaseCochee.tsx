import { InputHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

const CaseCochee = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, className, id, ...props }, ref) => {
    const checkboxId =
      id || `checkbox-${Math.random().toString(36).substr(2, 9)}`

    return (
      <div className="flex items-center">
        <input
          ref={ref}
          id={checkboxId}
          type="checkbox"
          className={clsx(
            'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary checked:bg-primary',
            className
          )}
          style={{
            backgroundImage: props.checked
              ? "url('data:image/svg+xml,%3csvg viewBox=%270 0 16 16%27 fill=%27rgb(255,255,255)%27 xmlns=%27http://www.w3.org/2000/svg%27%3e%3cpath d=%27M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z%27/%3e%3c/svg%3e')"
              : undefined,
          }}
          {...props}
        />
        {label && (
          <label
            htmlFor={checkboxId}
            className="ml-2 block text-sm text-gray-900 dark:text-gray-300"
          >
            {label}
          </label>
        )}
      </div>
    )
  }
)

CaseCochee.displayName = 'CaseCochee'

export default CaseCochee

