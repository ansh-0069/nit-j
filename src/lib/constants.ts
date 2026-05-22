export const HOSTEL_BLOCKS = ['MBH A', 'MBH B', 'MBH F', '7E', 'BH 6'] as const

/** App timezone — all timestamps are stored and displayed in IST (UTC+5:30). */
export const APP_TIMEZONE = 'Asia/Kolkata' as const

export const VIBE_TAGS = ['Chill', 'Movie', 'Birthday', 'Pre-game', 'Late night', 'Exam break'] as const

export type VibeTag = (typeof VIBE_TAGS)[number]

export const CHECKLIST_CATEGORIES: Record<string, string> = {
  'Papers / rolls': 'Papers',
  Grinder: 'Gear',
  Lighter: 'Gear',
  'Snacks & drinks': 'Food',
  'Music / speaker': 'Vibes',
}

export function getCategory(item: string): string {
  return CHECKLIST_CATEGORIES[item] ?? 'Other'
}
