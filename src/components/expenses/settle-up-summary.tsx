import { ArrowRight } from 'lucide-react'
import { formatMoney } from '@/lib/storage'
import type { SettleTransfer } from '@/types'

export function SettleUpSummary({ transfers }: { transfers: SettleTransfer[] }) {
  if (transfers.length === 0) {
    return (
      <p className="rounded-xl border border-joint-green/30 bg-joint-green/5 p-4 text-sm text-joint-green">
        Everyone&apos;s square — no transfers needed ✓
      </p>
    )
  }

  return (
    <div>
      <p className="label-caps mb-3">Settle up (min transfers)</p>
      <ul className="space-y-2">
        {transfers.map((t, i) => (
          <li
            key={`${t.from}-${t.to}-${i}`}
            className="flex items-center gap-2 rounded-xl border border-border bg-surface-2 px-4 py-3 text-sm"
          >
            <span className="font-semibold">{t.from}</span>
            <ArrowRight size={14} className="text-smoke" />
            <span className="font-semibold text-joint-green">{t.to}</span>
            <span className="ml-auto font-mono font-bold text-ember">{formatMoney(t.amount)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
