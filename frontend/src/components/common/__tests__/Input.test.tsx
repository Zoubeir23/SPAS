import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ChampSaisie from '../ChampSaisie'

describe('Input Component', () => {
  it('should render input with label', () => {
    render(<ChampSaisie label="Email" />)
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
  })

  it('should render input without label', () => {
    render(<ChampSaisie placeholder="Enter text" />)
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
  })

  it('should display error message', () => {
    render(<ChampSaisie error="This field is required" />)
    expect(screen.getByText('This field is required')).toBeInTheDocument()
  })

  it('should apply error styling when error is present', () => {
    const { container } = render(<ChampSaisie error="Error" />)
    const input = container.querySelector('input')
    expect(input?.className).toContain('ring-red-500')
  })

  it('should render with left icon', () => {
    const { container } = render(<ChampSaisie leftIcon="mail" />)
    const icon = container.querySelector('.material-symbols-outlined')
    expect(icon).toBeInTheDocument()
  })

  it('should render with right icon', () => {
    const { container } = render(<ChampSaisie rightIcon="visibility" />)
    const icons = container.querySelectorAll('.material-symbols-outlined')
    expect(icons.length).toBeGreaterThan(0)
  })
})

