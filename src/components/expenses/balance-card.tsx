import { motion } from 'framer-motion'
import { Copy, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { formatMoney, copySettleMessage } from '@/lib/storage'
import { cn } from '@/lib/cn'
import type { Balance, Expense } from '@/types'

export function BalanceCard({ balance, roomTitle }: { balance: Balance; roomTitle: string }) {
  const owes = balance.owes > 0
  const credit = balance.owes < 0

  return (
    <motion.div
      layout
      className={cn(
        'rounded-xl border p-4',
        owes && 'border-danger/30 bg-danger/5',
        credit && 'border-joint-green/30 bg-joint-green/5',
        !owes && !credit && 'border-border bg-surface-2',
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="heading-md">{balance.name}</p>
          <p className="mt-1 text-sm text-smoke">Paid {formatMoney(balance.paid)}</p>
          <p
            className={cn(
              'mt-0.5 text-sm font-semibold',
              owes && 'text-danger',
              credit && 'text-joint-green',
              !owes && !credit && 'text-smoke',
            )}
          >
            {owes && `Owes ${formatMoney(balance.owes)}`}
            {credit && `Gets back ${formatMoney(-balance.owes)}`}
            {!owes && !credit && 'All settled ✓'}
          </p>
        </div>
        {owes && (
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              copySettleMessage(balance.name, balance.owes, roomTitle).then(() =>
                toast.success('UPI reminder copied — send it in the group'),
              )
            }
          >
            <Copy size={14} />
            Remind
          </Button>
        )}
      </div>
    </motion.div>
  )
}

export function ExpenseRow({ expense, onRemove }: { expense: Expense; onRemove?: () => void }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-border py-3 last:border-0">
      <div>
        <p className="font-medium">{expense.description}</p>
        <p className="text-xs text-smoke">Paid by {expense.paid_by}</p>
      </div>
      <div className="flex items-center gap-2">
        <span className="font-mono font-bold text-joint-green">{formatMoney(expense.amount)}</span>
        {onRemove && (
        <Button variant="ghost" size="icon" onClick={onRemove}>
          <Trash2 size={14} />
        </Button>
        )}
      </div>
    </div>
  )
}
