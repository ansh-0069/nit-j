import { useState, useEffect } from 'react'
import { getStoredUser, setStoredUser } from '@/lib/storage'

export function useUser() {
  const [user, setUser] = useState(getStoredUser)

  useEffect(() => {
    const stored = getStoredUser()
    if (stored) setUser(stored)
  }, [])

  function saveUser(name: string) {
    setStoredUser(name)
    setUser(name)
  }

  return { user, saveUser }
}
