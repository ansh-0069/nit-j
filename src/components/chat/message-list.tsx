import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { formatTime } from '@/lib/storage'
import { cn } from '@/lib/cn'
import type { Message } from '@/types'

function isSystemMessage(msg: Message) {
  return msg.type === 'system' || msg.author === 'System'
}

export function MessageList({ messages, currentUser }: { messages: Message[]; currentUser: string }) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  const hasUserMessages = messages.some((m) => !isSystemMessage(m))

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center py-16 text-center">
        <p className="heading-md text-gradient">Nobody&apos;s yapping yet</p>
        <p className="mt-1 text-sm text-smoke">Who got papers? Who got snacks? Who paying? 💨</p>
      </div>
    )
  }

  return (
    <div className="flex max-h-[420px] flex-1 flex-col gap-3 overflow-y-auto pr-1">
      {!hasUserMessages && (
        <p className="text-center text-xs text-smoke">Activity updates appear here automatically</p>
      )}
      <AnimatePresence initial={false}>
        {messages.map((msg) => {
          if (isSystemMessage(msg)) {
            return (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex justify-center"
              >
                <div className="max-w-[90%] rounded-full border border-border/60 bg-surface-3/80 px-4 py-1.5 text-center">
                  <p className="text-[11px] text-smoke">
                    <span className="mr-2 text-joint-green/70">●</span>
                    {msg.content}
                    <time className="ml-2 text-[10px] text-smoke/60">{formatTime(msg.created_at)}</time>
                  </p>
                </div>
              </motion.div>
            )
          }

          const isOwn = msg.author === currentUser
          return (
            <motion.article
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn('flex', isOwn ? 'justify-end' : 'justify-start')}
            >
              <div
                className={cn(
                  'max-w-[85%] rounded-2xl px-4 py-3',
                  isOwn
                    ? 'rounded-br-md border-2 border-joint-green/40 bg-gradient-to-br from-joint-green/30 via-kush/20 to-haze/10'
                    : 'rounded-bl-md border-2 border-kush/30 bg-surface-2',
                )}
              >
                <header className="mb-1 flex items-center justify-between gap-3">
                  <strong className={cn('text-xs', isOwn ? 'text-joint-green' : 'text-white')}>
                    {isOwn ? 'You' : msg.author}
                  </strong>
                  <time className="text-[10px] text-smoke">{formatTime(msg.created_at)}</time>
                </header>
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
              </div>
            </motion.article>
          )
        })}
      </AnimatePresence>
      <div ref={bottomRef} />
    </div>
  )
}
