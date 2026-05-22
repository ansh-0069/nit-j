import { z } from 'zod'

export const profileSchema = z.object({
  name: z.string().trim().min(1, 'Name is required').max(30),
})

export const createRoomSchema = z.object({
  title: z.string().trim().min(1, 'Give the session a name').max(60),
  hostName: z.string().trim().min(1, 'Your name is required').max(30),
  location: z.string().trim().max(80).optional(),
  description: z.string().trim().max(300).optional(),
  scheduledAt: z.string().optional(),
  vibeTags: z.array(z.string()).optional(),
})

export const joinRoomSchema = z.object({
  name: z.string().trim().min(1, 'Your name is required').max(30),
  code: z.string().trim().length(6, 'Code must be 6 characters'),
  pin: z.string().trim().length(4, 'PIN must be 4 digits').optional().or(z.literal('')),
})

export const messageSchema = z.object({
  content: z.string().trim().min(1, 'Say something').max(500),
})

export const checklistSchema = z.object({
  item: z.string().trim().min(1, 'Item required').max(80),
})

export const expenseSchema = z.object({
  description: z.string().trim().min(1, 'Description required').max(80),
  amount: z
    .string()
    .min(1, 'Enter amount')
    .refine((v) => !Number.isNaN(Number(v)) && Number(v) > 0, 'Enter a valid amount'),
})
