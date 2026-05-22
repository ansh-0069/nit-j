import { useState } from 'react'
import { motion } from 'framer-motion'
import { MapPin, MessageCircle, Package, PackageX, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { AppShell, SectionLabel } from '@/components/layout/app-shell'
import { PageTransition, FadeIn } from '@/components/motion/page-transition'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useRegisterSeller, useRemoveSeller, useSellers, useUpdateSeller } from '@/hooks/use-sellers'
import { useUser } from '@/hooks/use-user'
import { HOSTEL_BLOCKS } from '@/lib/constants'
import { formatRelativeTime } from '@/lib/storage'
import { cn } from '@/lib/cn'
import type { Seller } from '@/types'

function SellerCard({
  seller,
  isOwn,
  user,
  onToggle,
  onRemove,
}: {
  seller: Seller
  isOwn: boolean
  user: string
  onToggle: (available: boolean) => void
  onRemove: () => void
}) {
  const [note, setNote] = useState(seller.note ?? '')
  const update = useUpdateSeller()

  function saveNote() {
    update.mutate(
      { id: seller.id, actorName: user, note },
      { onSuccess: () => toast.success('Note updated') },
    )
  }

  return (
    <motion.div layout initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <Card
        className={cn(
          'transition',
          seller.available ? 'border-joint-green/30 glow-green' : 'border-border opacity-90',
        )}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div
              className={cn(
                'mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full',
                seller.available ? 'bg-joint-green/20 text-joint-green' : 'bg-surface-3 text-smoke',
              )}
            >
              {seller.available ? <Package size={18} /> : <PackageX size={18} />}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="heading-md">{seller.name}</h3>
                <Badge variant={seller.available ? 'dank' : 'default'} className="normal-case">
                  {seller.available ? 'Stocked 💨' : 'Dry 😮‍💨'}
                </Badge>
                {seller.available && seller.stocked_at && (
                  <span className="text-[10px] text-joint-green">
                    stocked {formatRelativeTime(seller.stocked_at)}
                  </span>
                )}
                {isOwn && <Badge variant="host" className="normal-case">You</Badge>}
              </div>
              {seller.block && (
                <p className="mt-1 flex items-center gap-1 text-sm text-smoke">
                  <MapPin size={12} />
                  {seller.block}
                </p>
              )}
              {seller.note && !isOwn && (
                <p className="mt-2 text-sm text-white/90">{seller.note}</p>
              )}
              {seller.contact && (
                <p className="mt-1 flex items-center gap-1 text-xs text-joint-green">
                  <MessageCircle size={12} />
                  {seller.contact}
                </p>
              )}
              <p className="mt-2 text-[10px] text-smoke">Updated {formatRelativeTime(seller.updated_at)}</p>
            </div>
          </div>
        </div>

        {isOwn && (
          <div className="mt-4 space-y-3 border-t border-border pt-4">
            <div className="flex gap-2">
              <Button
                size="sm"
                className={seller.available ? '' : 'opacity-80'}
                onClick={() => onToggle(true)}
                disabled={seller.available}
              >
                Mark in stock
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onToggle(false)}
                disabled={!seller.available}
              >
                Mark dry
              </Button>
              <Button variant="ghost" size="sm" onClick={onRemove} className="ml-auto text-danger">
                <Trash2 size={14} />
                Remove
              </Button>
            </div>
            <div>
              <Label htmlFor={`note-${seller.id}`}>What&apos;s available?</Label>
              <Textarea
                id={`note-${seller.id}`}
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="e.g. papers, pre-rolls, dry till Friday..."
                rows={2}
                className="mt-1"
              />
              <Button size="sm" className="mt-2" onClick={saveNote} disabled={update.isPending}>
                Save note
              </Button>
            </div>
          </div>
        )}
      </Card>
    </motion.div>
  )
}

export default function Sellers() {
  const { user, saveUser } = useUser()
  const { data: sellers = [], isLoading } = useSellers()
  const register = useRegisterSeller()
  const update = useUpdateSeller()
  const remove = useRemoveSeller()

  const [showRegister, setShowRegister] = useState(false)
  const [name, setName] = useState(user)
  const [block, setBlock] = useState('')
  const [contact, setContact] = useState('')
  const [note, setNote] = useState('')
  const [available, setAvailable] = useState(true)

  const ownListing = sellers.find((s) => s.name.toLowerCase() === user.trim().toLowerCase())
  const inStock = sellers.filter((s) => s.available).length

  function handleRegister(e: React.FormEvent) {
    e.preventDefault()
    const sellerName = name.trim() || user.trim()
    if (!sellerName) {
      toast.error('Enter your name in the form')
      return
    }
    saveUser(sellerName)
    register.mutate(
      { name: sellerName, block: block || undefined, contact: contact || undefined, available, note: note || undefined },
      {
        onSuccess: () => {
          toast.success('You\'re on the board')
          setShowRegister(false)
        },
        onError: (err) => toast.error(err.message),
      },
    )
  }

  return (
    <AppShell backTo="/">
      <PageTransition>
        <FadeIn>
          <div className="mb-8">
            <h1 className="heading-xl">
              The <span className="text-gradient">Plugs</span> 🔌
            </h1>
            <p className="mt-2 max-w-lg text-smoke">
              Who&apos;s stocked, who&apos;s dry. Sellers flip their own status — boys know where to pull up.
            </p>
            {!isLoading && (
              <p className="mt-3 text-sm">
                <span className="font-semibold text-joint-green">{inStock}</span>
                <span className="text-smoke"> of {sellers.length} plugs on the board</span>
              </p>
            )}
          </div>
        </FadeIn>

        {!ownListing && !showRegister && (
          <FadeIn delay={0.05}>
            <Card className="mb-6 border-joint-green/25 bg-joint-green/5">
              <p className="heading-md text-joint-green">You a plug?</p>
              <p className="mt-1 text-sm text-smoke">Get on the board so the boys know if you&apos;re good</p>
              <Button className="mt-3" onClick={() => { setShowRegister(true); setName(user) }}>
                List me up 🌿
              </Button>
            </Card>
          </FadeIn>
        )}

        {showRegister && !ownListing && (
          <FadeIn delay={0.05}>
            <Card className="mb-6">
              <h2 className="heading-lg mb-4">Register as seller</h2>
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <Label htmlFor="seller-name">Your name</Label>
                  <Input id="seller-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="How people know you" />
                </div>
                <div>
                  <Label>Block</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {HOSTEL_BLOCKS.map((b) => (
                      <button
                        key={b}
                        type="button"
                        onClick={() => setBlock(b)}
                        className={cn(
                          'rounded-lg border px-3 py-1.5 text-xs font-semibold transition',
                          block === b
                            ? 'border-joint-green bg-joint-green/15 text-joint-green'
                            : 'border-border bg-surface-2 text-smoke',
                        )}
                      >
                        {b}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <Label htmlFor="contact">Contact (optional)</Label>
                  <Input id="contact" value={contact} onChange={(e) => setContact(e.target.value)} placeholder="WhatsApp / Telegram" />
                </div>
                <div>
                  <Label htmlFor="seller-note">Note</Label>
                  <Textarea id="seller-note" value={note} onChange={(e) => setNote(e.target.value)} placeholder="What's available..." rows={2} />
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={available ? 'default' : 'secondary'}
                    onClick={() => setAvailable(true)}
                  >
                    In stock
                  </Button>
                  <Button
                    type="button"
                    variant={!available ? 'default' : 'secondary'}
                    onClick={() => setAvailable(false)}
                  >
                    Dry
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={register.isPending}>
                    {register.isPending ? 'Adding...' : 'Go live on board'}
                  </Button>
                  <Button type="button" variant="ghost" onClick={() => setShowRegister(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </Card>
          </FadeIn>
        )}

        <SectionLabel>{isLoading ? 'Loading...' : 'Seller board'}</SectionLabel>

        <div className="space-y-3">
          {sellers.length === 0 && !isLoading ? (
            <Card className="text-center text-smoke">No sellers listed yet</Card>
          ) : (
            sellers.map((seller, i) => (
              <FadeIn key={seller.id} delay={0.03 * i}>
                <SellerCard
                  seller={seller}
                  isOwn={seller.name.toLowerCase() === user.trim().toLowerCase()}
                  user={user}
                  onToggle={(avail) =>
                    update.mutate(
                      { id: seller.id, actorName: user, available: avail },
                      { onSuccess: () => toast.success(avail ? 'Marked in stock' : 'Marked dry') },
                    )
                  }
                  onRemove={() =>
                    remove.mutate(
                      { id: seller.id, actorName: user },
                      { onSuccess: () => toast.success('Listing removed') },
                    )
                  }
                />
              </FadeIn>
            ))
          )}
        </div>
      </PageTransition>
    </AppShell>
  )
}
