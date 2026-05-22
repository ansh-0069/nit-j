export const IST_TIMEZONE = 'Asia/Kolkata'
const IST_OFFSET = '+05:30'

/** Parse stored timestamps — naive DB strings are treated as IST. */
export function parseStoredTime(value: string): Date {
  if (value.includes('T')) {
    if (value.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(value)) {
      return new Date(value)
    }
    return new Date(`${value.length === 16 ? `${value}:00` : value}${IST_OFFSET}`)
  }
  return new Date(`${value.replace(' ', 'T')}${IST_OFFSET}`)
}

/** Current time as `YYYY-MM-DD HH:MM:SS` in IST. */
export function nowIst(): string {
  return new Date().toLocaleString('sv-SE', { timeZone: IST_TIMEZONE })
}
