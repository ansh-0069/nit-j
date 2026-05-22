import { IST_TIMEZONE, parseStoredTime } from '@/lib/time'

const USER_KEY = 'nit-joint-user'

export function getStoredUser(): string {
  return localStorage.getItem(USER_KEY) ?? ''
}

export function setStoredUser(name: string) {
  localStorage.setItem(USER_KEY, name)
}

export function formatTime(iso: string) {
  const date = parseStoredTime(iso)
  return date.toLocaleString('en-IN', {
    timeZone: IST_TIMEZONE,
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function formatMoney(amount: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function getCountdown(scheduledAt: string | null): string | null {
  if (!scheduledAt) return null
  const target = parseStoredTime(scheduledAt)
  const diff = target.getTime() - Date.now()
  if (diff <= 0) return 'Live now'
  const hours = Math.floor(diff / 3_600_000)
  const mins = Math.floor((diff % 3_600_000) / 60_000)
  if (hours > 24) return `In ${Math.floor(hours / 24)}d ${hours % 24}h`
  if (hours > 0) return `In ${hours}h ${mins}m`
  return `In ${mins}m`
}

export function isLiveSoon(scheduledAt: string | null): boolean {
  if (!scheduledAt) return false
  const target = parseStoredTime(scheduledAt)
  const diff = target.getTime() - Date.now()
  return diff > 0 && diff < 2 * 3_600_000
}

export function copySettleMessage(name: string, amount: number, roomTitle: string) {
  const msg = `Bro ${name}, you owe ${formatMoney(amount)} for ${roomTitle} 🌿 — settle on UPI pls`
  return navigator.clipboard.writeText(msg)
}

export function formatRelativeTime(iso: string | null | undefined): string | null {
  if (!iso) return null
  const date = parseStoredTime(iso)
  const diffMs = Date.now() - date.getTime()
  if (diffMs < 0) return 'just now'
  const mins = Math.floor(diffMs / 60_000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins} min ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export function formatActivityPulse(lastActivityAt: string | null | undefined): string | null {
  if (!lastActivityAt) return null
  const rel = formatRelativeTime(lastActivityAt)
  return rel ? `Active ${rel}` : null
}
