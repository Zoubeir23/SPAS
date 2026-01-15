import { describe, it, expect, vi } from 'vitest'
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

  it('should display error message and link with aria-describedby', () => {
    render(<ChampSaisie error="This field is required" />)
    const errorMessage = screen.getByText('This field is required')
    expect(errorMessage).toBeInTheDocument()

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('aria-invalid', 'true')
    expect(input).toHaveAttribute('aria-describedby', errorMessage.id)
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

  it('should render with right icon as button when interactive', () => {
    const onRightIconClick = vi.fn()
    render(
      <ChampSaisie
        rightIcon="visibility"
        onRightIconClick={onRightIconClick}
        rightIconLabel="Toggle visibility"
      />
    )

    const button = screen.getByRole('button', { name: 'Toggle visibility' })
    expect(button).toBeInTheDocument()

    // Check if icon is inside
    expect(button.querySelector('.material-symbols-outlined')).toHaveTextContent(
      'visibility'
    )
  })

  it('should render with right icon as div when not interactive', () => {
    const { container } = render(<ChampSaisie rightIcon="check" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    const icon = container.querySelector('.material-symbols-outlined')
    expect(icon).toHaveTextContent('check')
  })
})
