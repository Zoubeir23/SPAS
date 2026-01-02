import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Bouton from '../Bouton'

describe('Button Component', () => {
  it('should render button with children', () => {
    render(<Bouton>Click me</Bouton>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('should call onClick when clicked', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<Bouton onClick={handleClick}>Click me</Bouton>)
    await user.click(screen.getByText('Click me'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should be disabled when disabled prop is true', () => {
    render(<Bouton disabled>Disabled</Bouton>)
    expect(screen.getByText('Disabled')).toBeDisabled()
  })

  it('should show loading state', () => {
    render(<Bouton isLoading>Submit</Bouton>)
    expect(screen.getByText('Chargement...')).toBeInTheDocument()
  })

  it('should apply variant classes', () => {
    const { container } = render(<Bouton variant="primary">Primary</Bouton>)
    const button = container.querySelector('button')
    expect(button?.className).toContain('bg-primary')
  })

  it('should apply size classes', () => {
    const { container } = render(<Bouton size="lg">Large</Bouton>)
    const button = container.querySelector('button')
    expect(button?.className).toContain('px-4')
  })
})

