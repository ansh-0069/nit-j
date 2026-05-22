import { useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Plus } from 'lucide-react'
import { toast } from 'sonner'
import { RunSheetItem } from '@/components/checklist/run-sheet-item'
import { ProgressRing } from '@/components/checklist/progress-ring'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getCategory } from '@/lib/constants'
import { checklistSchema } from '@/lib/schemas'
import type { z } from 'zod'
import type { ChecklistItem } from '@/types'

type ItemForm = z.infer<typeof checklistSchema>

export function RunSheet({
  items,
  currentUser,
  onClaim,
  onAdd,
  onRemove,
  readOnly,
}: {
  items: ChecklistItem[]
  currentUser: string
  onClaim: (id: number, claimedBy: string | null) => void
  onAdd: (item: string) => void
  onRemove: (id: number) => void
  readOnly?: boolean
}) {
  const { register, handleSubmit, reset } = useForm<ItemForm>({
    resolver: zodResolver(checklistSchema),
  })

  const grouped = useMemo(() => {
    const map = new Map<string, ChecklistItem[]>()
    for (const item of items) {
      const cat = getCategory(item.item)
      if (!map.has(cat)) map.set(cat, [])
      map.get(cat)!.push(item)
    }
    return map
  }, [items])

  const claimed = items.filter((i) => i.claimed_by).length

  if (items.length === 0) {
    return (
      <div className="space-y-5">
        <div className="rounded-xl border border-dashed border-border bg-surface-2/50 p-8 text-center">
          <p className="heading-md text-gradient">Grab list is empty</p>
          <p className="mt-1 text-sm text-smoke">Who&apos;s grabbing papers? Snacks? Add it below 🛒</p>
        </div>
        {!readOnly && (
          <form
            className="flex gap-2"
            onSubmit={handleSubmit((data) => {
              onAdd(data.item)
              reset()
              toast.success('Added to run sheet')
            })}
          >
            <div className="flex-1">
              <Label htmlFor="new-item" className="sr-only">
                New item
              </Label>
              <Input id="new-item" placeholder="Add something else..." {...register('item')} />
            </div>
            <Button type="submit">
              <Plus size={18} />
              Add
            </Button>
          </form>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between rounded-xl border border-border bg-surface-2 p-4">
        <div>
          <p className="text-xs uppercase tracking-wider text-smoke">Run sheet progress</p>
          <p className="heading-md">
            {claimed === items.length && items.length > 0 ? 'All locked in 🔥' : 'Claim your shit'}
          </p>
        </div>
        <ProgressRing claimed={claimed} total={items.length} />
      </div>

      {[...grouped.entries()].map(([category, catItems]) => (
        <div key={category}>
          <p className="label-caps mb-2 text-joint-green/80">
            {category}
          </p>
          <ul className="space-y-2">
            {catItems.map((item) => (
              <RunSheetItem
                key={item.id}
                item={item}
                currentUser={currentUser}
                readOnly={readOnly}
                onClaim={() =>
                  onClaim(item.id, item.claimed_by === currentUser ? null : currentUser)
                }
                onRemove={() => onRemove(item.id)}
              />
            ))}
          </ul>
        </div>
      ))}

      {!readOnly && (
      <form
        className="flex gap-2"
        onSubmit={handleSubmit((data) => {
          onAdd(data.item)
          reset()
          toast.success('Added to run sheet')
        })}
      >
        <div className="flex-1">
          <Label htmlFor="new-item" className="sr-only">
            New item
          </Label>
          <Input id="new-item" placeholder="Add something else..." {...register('item')} />
        </div>
        <Button type="submit">
          <Plus size={18} />
          Add
        </Button>
      </form>
      )}
    </div>
  )
}
