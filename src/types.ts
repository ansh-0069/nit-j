export type MemberStatus = 'on_my_way' | 'here' | 'running_late'

export interface Member {
  name: string
  joined_at: string
  status?: MemberStatus
  block?: string | null
}

export type MessageType = 'user' | 'system'

export interface Message {
  id: number
  room_id: string
  author: string
  content: string
  type?: MessageType
  created_at: string
}

export interface ChecklistItem {
  id: number
  room_id: string
  item: string
  claimed_by: string | null
  created_at: string
}

export interface Expense {
  id: number
  room_id: string
  description: string
  amount: number
  paid_by: string
  created_at: string
}

export interface Balance {
  name: string
  paid: number
  owes: number
}

export interface SettleTransfer {
  from: string
  to: string
  amount: number
}

export interface SplitSummary {
  total: number
  perPerson: number
  memberCount: number
  balances: Balance[]
  settleUp: SettleTransfer[]
}

export interface Room {
  id: string
  code: string
  title: string
  host_name: string
  location: string | null
  description: string | null
  max_capacity: number
  scheduled_at: string | null
  playlist_url: string | null
  vibe_tags: string[]
  has_pin?: boolean
  is_archived?: boolean
  archived_at?: string | null
  last_activity_at?: string | null
  last_message_at?: string | null
  created_at: string
  members: Member[]
  messages: Message[]
  checklist: ChecklistItem[]
  expenses: Expense[]
  split: SplitSummary
}

export interface RoomListItem {
  id: string
  code: string
  title: string
  host_name: string
  location: string | null
  scheduled_at: string | null
  playlist_url: string | null
  vibe_tags: string[]
  member_count: number
  message_count?: number
  last_activity_at?: string | null
  last_message_at?: string | null
  has_pin?: boolean
  created_at: string
}

export interface Seller {
  id: number
  name: string
  block: string | null
  contact: string | null
  available: boolean
  note: string | null
  updated_at: string
  stocked_at: string | null
}

export interface CrewMember {
  name: string
  block?: string
}
