import { describe, it, expect } from 'vitest'
import { loginSchema, forgotPasswordSchema } from '../validators'

describe('Login Schema', () => {
  it('should validate a correct login form', () => {
    const validData = {
      email: 'test@example.com',
      password: 'password123',
      rememberMe: false,
    }

    const result = loginSchema.safeParse(validData)
    expect(result.success).toBe(true)
  })

  it('should reject invalid email', () => {
    const invalidData = {
      email: 'not-an-email',
      password: 'password123',
    }

    const result = loginSchema.safeParse(invalidData)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('email')
    }
  })

  it('should reject password shorter than 8 characters', () => {
    const invalidData = {
      email: 'test@example.com',
      password: 'short',
    }

    const result = loginSchema.safeParse(invalidData)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('password')
    }
  })

  it('should require email', () => {
    const invalidData = {
      password: 'password123',
    }

    const result = loginSchema.safeParse(invalidData)
    expect(result.success).toBe(false)
  })

  it('should require password', () => {
    const invalidData = {
      email: 'test@example.com',
    }

    const result = loginSchema.safeParse(invalidData)
    expect(result.success).toBe(false)
  })
})

describe('Forgot Password Schema', () => {
  it('should validate a correct email', () => {
    const validData = {
      email: 'test@example.com',
    }

    const result = forgotPasswordSchema.safeParse(validData)
    expect(result.success).toBe(true)
  })

  it('should reject invalid email', () => {
    const invalidData = {
      email: 'not-an-email',
    }

    const result = forgotPasswordSchema.safeParse(invalidData)
    expect(result.success).toBe(false)
  })

  it('should require email', () => {
    const invalidData = {}

    const result = forgotPasswordSchema.safeParse(invalidData)
    expect(result.success).toBe(false)
  })
})

