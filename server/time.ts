export const IST_TIMEZONE = 'Asia/Kolkata'

/** SQLite expression for current time in IST (UTC+5:30). */
export const SQL_NOW_IST = "datetime('now', '+5 hours', '+30 minutes')"

/** Current time as `YYYY-MM-DD HH:MM:SS` in IST. */
export function nowIst(): string {
  return new Date().toLocaleString('sv-SE', { timeZone: IST_TIMEZONE })
}
