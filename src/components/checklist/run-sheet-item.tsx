import { motion } from 'framer-motion'
import { Check, Trash2, User } from 'lucide-react'
import { cn } from '@/lib/cn'
import { Button } from '@/components/ui/button'
import type { ChecklistItem } from '@/types'

export function RunSheetItem({
  item,
  currentUser,
  onClaim,
  onRemove,
  readOnly,
}: {
  item: ChecklistItem
  currentUser: string
  onClaim: () => void
  onRemove: () => void
  readOnly?: boolean
}) {
  const isClaimed = !!item.claimed_by
  const isMine = item.claimed_by === currentUser

  return (
    <motion.li
      layout
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'flex items-center gap-3 rounded-xl border p-3 transition',
        isClaimed
          ? 'border-joint-green/20 bg-joint-green/5'
          : 'border-border bg-surface-2 ring-1 ring-joint-green/0 hover:ring-joint-green/20',
      )}
    >
      <motion.button
        type="button"
        whileTap={{ scale: 0.85 }}
        onClick={onClaim}
        disabled={readOnly}
        className={cn(
          'flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 transition',
          isClaimed
            ? 'border-joint-green bg-joint-green/20 text-joint-green'
            : 'border-border bg-surface-3 text-smoke hover:border-joint-green hover:text-joint-green',
        )}
      >
        {isClaimed ? <Check size={18} strokeWidth={3} /> : '○'}
      </motion.button>

      <div className="min-w-0 flex-1">
        <p className={cn('font-medium', isClaimed && 'text-smoke line-through')}>{item.item}</p>
        {isClaimed && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-0.5 flex items-center gap-1 text-xs text-joint-green"
          >
            <User size={12} />
            {isMine ? 'You got this' : item.claimed_by}
          </motion.p>
        )}
      </div>

      {!readOnly && (
      <Button variant="ghost" size="icon" onClick={onRemove} className="shrink-0 text-smoke hover:text-danger">
        <Trash2 size={16} />
      </Button>
      )}
    </motion.li>
  )
}
