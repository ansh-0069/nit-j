import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { IndianRupee, Plus } from 'lucide-react'
import { toast } from 'sonner'
import { BalanceCard, ExpenseRow } from '@/components/expenses/balance-card'
import { SettleUpSummary } from '@/components/expenses/settle-up-summary'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { expenseSchema } from '@/lib/schemas'
import { formatMoney } from '@/lib/storage'
import type { z } from 'zod'
import type { Room } from '@/types'

type ExpenseForm = z.infer<typeof expenseSchema>

export function KittyPanel({
  room,
  currentUser,
  onAdd,
  onRemove,
  readOnly,
}: {
  room: Room
  currentUser: string
  onAdd: (data: { description: string; amount: number; paidBy: string }) => void
  onRemove: (id: number) => void
  readOnly?: boolean
}) {
  const { register, handleSubmit, reset } = useForm<ExpenseForm>({
    resolver: zodResolver(expenseSchema),
  })

  return (
    <div className="space-y-6">
      {room.expenses.length === 0 && (
        <div className="rounded-xl border border-dashed border-border bg-surface-2/50 p-8 text-center">
          <p className="heading-md text-gradient-wild">The tab is empty</p>
          <p className="mt-1 text-sm text-smoke">Log what was bought — we&apos;ll split it fair</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-2xl border border-border bg-surface-2 p-5">
          <p className="text-xs uppercase tracking-wider text-smoke">Total spent</p>
          <p className="font-display text-2xl font-semibold tracking-tight text-gradient-wild md:text-3xl">{formatMoney(room.split.total)}</p>
        </div>
        <div className="rounded-2xl border border-joint-green/30 bg-joint-green/5 p-5">
          <p className="text-xs uppercase tracking-wider text-smoke">Per head</p>
          <p className="font-display text-2xl font-semibold tracking-tight text-joint-green md:text-3xl">
            {formatMoney(room.split.perPerson)}
          </p>
        </div>
      </div>

      <SettleUpSummary transfers={room.split.settleUp} />

      <div>
        <p className="label-caps mb-3">Who owes what</p>
        <div className="grid gap-3 sm:grid-cols-2">
          {room.split.balances.map((b) => (
            <BalanceCard key={b.name} balance={b} roomTitle={room.title} />
          ))}
        </div>
      </div>

      {room.expenses.length > 0 && (
        <div>
          <p className="label-caps mb-2">Receipts</p>
          <div className="rounded-xl border border-border bg-surface-2 px-4">
            {room.expenses.map((exp) => (
              <ExpenseRow key={exp.id} expense={exp} onRemove={readOnly ? undefined : () => onRemove(exp.id)} />
            ))}
          </div>
        </div>
      )}

      {!readOnly && (
      <form
        className="grid gap-3 rounded-xl border border-border bg-surface-2 p-4 sm:grid-cols-[1fr_120px_auto]"
        onSubmit={handleSubmit((data) => {
          onAdd({ description: data.description, amount: Number(data.amount), paidBy: currentUser })
          reset()
          toast.success('Expense logged')
        })}
      >
        <div>
          <Label htmlFor="exp-desc">What was bought?</Label>
          <Input id="exp-desc" placeholder="Papers, snacks, etc." {...register('description')} />
        </div>
        <div>
          <Label htmlFor="exp-amt">Amount</Label>
          <div className="relative">
            <IndianRupee size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-smoke" />
            <Input id="exp-amt" type="number" className="pl-8" placeholder="500" {...register('amount')} />
          </div>
        </div>
        <div className="flex items-end">
          <Button type="submit" className="w-full sm:w-auto">
            <Plus size={16} />
            Log it
          </Button>
        </div>
      </form>
      )}
    </div>
  )
}
