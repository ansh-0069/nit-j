import { useState } from 'react'
import { UserPlus, X, Users } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { HOSTEL_BLOCKS } from '@/lib/constants'
import { addToCrew, getTrustedCrew, removeFromCrew } from '@/lib/trusted-crew'
import { cn } from '@/lib/cn'
import type { CrewMember } from '@/types'

export function TrustedCrewPanel({ onSelect }: { onSelect?: (name: string) => void }) {
  const [crew, setCrew] = useState(getTrustedCrew)
  const [newName, setNewName] = useState('')
  const [newBlock, setNewBlock] = useState('')

  function handleAdd() {
    if (!newName.trim()) return
    setCrew(addToCrew(newName, newBlock || undefined))
    setNewName('')
    setNewBlock('')
    toast.success('Added to the usual boys')
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users size={18} className="text-joint-green" />
          The usual boys 👊
        </CardTitle>
        <CardDescription>Your day-ones — block auto-fills when they join</CardDescription>
      </CardHeader>

      <div className="mb-3 space-y-2">
        <Input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Add a name"
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAdd())}
        />
        <div>
          <Label className="text-xs text-smoke">Block (optional)</Label>
          <div className="mt-1 flex flex-wrap gap-1">
            {HOSTEL_BLOCKS.map((block) => (
              <button
                key={block}
                type="button"
                onClick={() => setNewBlock(block)}
                className={cn(
                  'rounded-lg border px-2 py-1 text-[10px] font-semibold transition',
                  newBlock === block
                    ? 'border-joint-green bg-joint-green/15 text-joint-green'
                    : 'border-border bg-surface-2 text-smoke',
                )}
              >
                {block}
              </button>
            ))}
          </div>
        </div>
        <Button type="button" variant="secondary" size="sm" onClick={handleAdd}>
          <UserPlus size={16} />
          Add to crew
        </Button>
      </div>

      {crew.length === 0 ? (
        <p className="text-sm text-smoke">No crew saved yet — add your regulars</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {crew.map((member: CrewMember) => (
            <div
              key={member.name}
              className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-2 pl-3 pr-1.5 py-1.5 text-sm font-medium"
            >
              <button type="button" onClick={() => onSelect?.(member.name)} className="hover:text-joint-green">
                {member.name}
                {member.block && <span className="ml-1 text-[10px] text-smoke">· {member.block}</span>}
              </button>
              <button
                type="button"
                onClick={() => setCrew(removeFromCrew(member.name))}
                className="rounded-full p-0.5 text-smoke hover:bg-danger/20 hover:text-danger"
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

export function useTrustedCrew() {
  return getTrustedCrew()
}
