import { useState, useCallback } from 'react'

export function usePasswordVisibility() {
  const [isVisible, setIsVisible] = useState(false)

  const toggle = useCallback(() => {
    setIsVisible((prev) => !prev)
  }, [])

  return {
    isVisible,
    toggle,
    type: isVisible ? 'text' : 'password',
    icon: isVisible ? 'visibility_off' : 'visibility',
  }
}

