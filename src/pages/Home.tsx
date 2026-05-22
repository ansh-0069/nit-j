import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ChevronRight, Flame, Lock, MapPin, MessageCircle, Package, Plus, Users, Zap } from 'lucide-react'
import { toast } from 'sonner'
import { Logo, Wordmark } from '@/components/brand/logo'
import { TrustedCrewPanel } from '@/components/crew/trusted-crew-panel'
import { AppShell, SectionLabel } from '@/components/layout/app-shell'
import { InstallPrompt } from '@/components/pwa/install-prompt'
import { FadeIn, PageTransition } from '@/components/motion/page-transition'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useCreateRoom, useRooms } from '@/hooks/use-room'
import { useSellers } from '@/hooks/use-sellers'
import { useUser } from '@/hooks/use-user'
import { CopyCodeBadge } from '@/components/room/copy-code-badge'
import { HOSTEL_BLOCKS, VIBE_TAGS } from '@/lib/constants'
import { createRoomSchema, joinRoomSchema } from '@/lib/schemas'
import { getCountdown, isLiveSoon, formatActivityPulse, formatRelativeTime } from '@/lib/storage'
import { parseStoredTime } from '@/lib/time'
import { getRoomLastSeen } from '@/lib/trusted-crew'
import { cn } from '@/lib/cn'
import type { z } from 'zod'

type CreateForm = z.infer<typeof createRoomSchema>
type JoinForm = z.infer<typeof joinRoomSchema>

export default function Home() {
  const navigate = useNavigate()
  const { user, saveUser } = useUser()
  const [vibeFilter, setVibeFilter] = useState<string | undefined>()
  const { data: rooms = [], isLoading } = useRooms(vibeFilter)
  const { data: sellers = [] } = useSellers()
  const inStockCount = sellers.filter((s) => s.available).length
  const createMutation = useCreateRoom()
  const [mode, setMode] = useState<'create' | 'join'>('create')
  const [selectedBlock, setSelectedBlock] = useState('')
  const [selectedVibes, setSelectedVibes] = useState<string[]>([])
  const [joinPin, setJoinPin] = useState('')

  const createForm = useForm<CreateForm>({
    resolver: zodResolver(createRoomSchema),
    defaultValues: {
      hostName: user,
      title: '',
      location: '',
      description: '',
      scheduledAt: '',
    },
  })

  const joinForm = useForm<JoinForm>({
    resolver: zodResolver(joinRoomSchema),
    defaultValues: { name: user, code: '' },
  })

  function toggleVibe(tag: string) {
    setSelectedVibes((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    )
  }

  async function onCreate(data: CreateForm) {
    const hostName = user.trim() || data.hostName.trim()
    if (!hostName) {
      toast.error('Enter your name first')
      return
    }
    saveUser(hostName)
    try {
      const room = await createMutation.mutateAsync({
        title: data.title,
        hostName,
        location: data.location || selectedBlock || undefined,
        description: data.description,
        scheduledAt: data.scheduledAt || undefined,
        vibeTags: selectedVibes,
        joinPin: joinPin.trim() || undefined,
      })
      toast.success('Joint is open — ping the boys on WhatsApp')
      navigate(`/room/${room.code}`)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to create')
    }
  }

  async function onJoin(data: JoinForm) {
    const name = user.trim() || data.name.trim()
    if (!name) {
      toast.error('Enter your name first')
      return
    }
    saveUser(name)
    navigate(`/room/${data.code.toUpperCase()}`)
  }

  return (
    <AppShell showBrand={false}>
      <PageTransition>
        <section className="mb-8 text-center">
          <FadeIn>
            <div className="mx-auto mb-4 flex justify-center">
              <Logo size="lg" />
            </div>
            <Wordmark />
            <p className="mx-auto mt-3 max-w-md text-smoke">
              Where the boys link up. Pick a dorm, roll a sesh, figure out who&apos;s bringing what and who owes who. 🌿
            </p>
          </FadeIn>
        </section>

        <InstallPrompt />

        <FadeIn delay={0.04}>
          <Link to="/sellers" className="mb-6 block">
            <Card className="group transition hover:border-joint-green/40 hover:glow-green">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-joint-green/15 text-joint-green">
                    <Package size={22} />
                  </div>
                  <div>
                    <p className="heading-md group-hover:text-joint-green">The Plugs 🔌</p>
                    <p className="text-sm text-smoke">
                      {sellers.length === 0
                        ? 'Who\'s got the goods on campus'
                        : `${inStockCount} plug${inStockCount === 1 ? '' : 's'} stocked rn 💨`}
                    </p>
                  </div>
                </div>
                <ChevronRight className="text-smoke group-hover:text-joint-green" size={20} />
              </div>
            </Card>
          </Link>
        </FadeIn>

        <FadeIn delay={0.05}>
          <Card className="mb-6">
            <Label htmlFor="profile-name">Your name</Label>
            <Input
              id="profile-name"
              value={user}
              onChange={(e) => saveUser(e.target.value)}
              placeholder="What do the boys call you?"
              className="mt-2 text-lg font-medium"
            />
          </Card>
        </FadeIn>

        <FadeIn delay={0.08}>
          <div className="mb-6">
            <TrustedCrewPanel onSelect={(name) => saveUser(name)} />
          </div>
        </FadeIn>

        <FadeIn delay={0.1}>
          <div className="mb-6 grid grid-cols-2 gap-3">
            <motion.button
              type="button"
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode('create')}
              className={cn(
                'rounded-2xl border-2 p-5 text-left transition',
                mode === 'create'
                  ? 'border-joint-green/50 bg-joint-green/10 glow-green'
                  : 'border-border bg-surface hover:border-border/80',
              )}
            >
              <Plus className="mb-2 text-joint-green" size={24} />
              <p className="heading-md">Start a sesh</p>
              <p className="mt-1 text-xs text-smoke">Host at your crib</p>
            </motion.button>
            <motion.button
              type="button"
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode('join')}
              className={cn(
                'rounded-2xl border-2 p-5 text-left transition',
                mode === 'join'
                  ? 'border-joint-green/50 bg-joint-green/10 glow-green'
                  : 'border-border bg-surface hover:border-border/80',
              )}
            >
              <Zap className="mb-2 text-ember" size={24} />
              <p className="heading-md">Pull up</p>
              <p className="mt-1 text-xs text-smoke">Got the code?</p>
            </motion.button>
          </div>
        </FadeIn>

        <FadeIn delay={0.15}>
          {mode === 'create' ? (
            <Card className="mb-8">
              <h2 className="heading-lg mb-4 text-gradient">Spin up a sesh 🌿</h2>
              <form onSubmit={createForm.handleSubmit(onCreate)} className="space-y-4">
                <div>
                  <Label htmlFor="title">Session name</Label>
                  <Input id="title" placeholder="Friday night rip" {...createForm.register('title')} />
                  {createForm.formState.errors.title && (
                    <p className="mt-1 text-xs text-danger">{createForm.formState.errors.title.message}</p>
                  )}
                </div>

                <div>
                  <Label>Vibe</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {VIBE_TAGS.map((tag) => (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => toggleVibe(tag)}
                        className={cn(
                          'rounded-lg border px-3 py-1.5 text-xs font-semibold transition',
                          selectedVibes.includes(tag)
                            ? 'border-ember/50 bg-ember/15 text-ember'
                            : 'border-border bg-surface-2 text-smoke hover:text-white',
                        )}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <Label>Block / location</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {HOSTEL_BLOCKS.map((block) => (
                      <button
                        key={block}
                        type="button"
                        onClick={() => {
                          setSelectedBlock(block)
                          createForm.setValue('location', block)
                        }}
                        className={cn(
                          'rounded-lg border px-3 py-1.5 text-xs font-semibold transition',
                          selectedBlock === block || createForm.watch('location') === block
                            ? 'border-joint-green bg-joint-green/15 text-joint-green'
                            : 'border-border bg-surface-2 text-smoke hover:text-white',
                        )}
                      >
                        {block}
                      </button>
                    ))}
                  </div>
                  <Input
                    className="mt-2"
                    placeholder="Or type room — MBH A · 204"
                    {...createForm.register('location')}
                  />
                </div>

                <div>
                  <Label htmlFor="when">When</Label>
                  <Input id="when" type="datetime-local" {...createForm.register('scheduledAt')} />
                </div>

                <div>
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea
                    id="notes"
                    placeholder="No randos, bring your own, etc..."
                    {...createForm.register('description')}
                  />
                </div>

                <div>
                  <Label htmlFor="join-pin" className="flex items-center gap-1">
                    <Lock size={12} />
                    Join PIN (optional)
                  </Label>
                  <Input
                    id="join-pin"
                    value={joinPin}
                    onChange={(e) => setJoinPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                    placeholder="4 digits — keeps randos out"
                    className="mt-2 font-mono tracking-[0.5em]"
                    maxLength={4}
                    inputMode="numeric"
                  />
                </div>

                <Button type="submit" className="w-full" size="lg" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Loading...' : 'Let\'s go 🔥'}
                </Button>
              </form>
            </Card>
          ) : (
            <Card className="mb-8">
              <h2 className="heading-lg mb-4 text-haze">Enter the code 💨</h2>
              <form onSubmit={joinForm.handleSubmit(onJoin)} className="space-y-4">
                <div>
                  <Label htmlFor="code">Room code</Label>
                  <Input
                    id="code"
                    className="text-center font-mono text-2xl font-semibold tracking-[0.35em] uppercase"
                    placeholder="ABC123"
                    maxLength={6}
                    {...joinForm.register('code', {
                      onChange: (e) => {
                        e.target.value = e.target.value.toUpperCase()
                      },
                    })}
                  />
                  {joinForm.formState.errors.code && (
                    <p className="mt-1 text-xs text-danger">{joinForm.formState.errors.code.message}</p>
                  )}
                </div>
                <Button type="submit" className="w-full" size="lg">
                  Pull up
                </Button>
              </form>
            </Card>
          )}
        </FadeIn>

        <SectionLabel>Filter by vibe</SectionLabel>
        <div className="mb-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setVibeFilter(undefined)}
            className={cn(
              'rounded-full border px-3 py-1 text-xs font-semibold transition',
              !vibeFilter
                ? 'border-joint-green bg-joint-green/15 text-joint-green'
                : 'border-border text-smoke hover:text-white',
            )}
          >
            All
          </button>
          {VIBE_TAGS.map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={() => setVibeFilter(vibeFilter === tag ? undefined : tag)}
              className={cn(
                'rounded-full border px-3 py-1 text-xs font-semibold transition',
                vibeFilter === tag
                  ? 'border-ember bg-ember/15 text-ember'
                  : 'border-border text-smoke hover:text-white',
              )}
            >
              {tag}
            </button>
          ))}
        </div>

        <SectionLabel>
          {isLoading ? 'Loading...' : rooms.length > 0 ? 'Active seshes 🔥' : 'Nothing cooking yet'}
        </SectionLabel>

        <div className="space-y-3">
          {rooms.map((room, i) => {
            const liveSoon = isLiveSoon(room.scheduled_at)
            const countdown = getCountdown(room.scheduled_at)
            const activity = formatActivityPulse(room.last_activity_at)
            const hasNew =
              room.last_message_at &&
              getRoomLastSeen(room.code) &&
              parseStoredTime(room.last_message_at) > parseStoredTime(getRoomLastSeen(room.code)!)
            return (
              <FadeIn key={room.id} delay={0.05 * i}>
                <motion.div whileHover={{ y: -2 }}>
                  <Link to={`/room/${room.code}`}>
                    <Card className="group transition hover:border-joint-green/30 hover:glow-green">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <div className="mb-2 flex flex-wrap items-center gap-2">
                            {liveSoon && (
                              <Badge variant="live" className="gap-1">
                                <Flame size={10} />
                                Starting soon
                              </Badge>
                            )}
                            {hasNew && (
                              <Badge variant="live" className="gap-1 normal-case">
                                <MessageCircle size={10} />
                                New yap
                              </Badge>
                            )}
                            <CopyCodeBadge code={room.code} />
                            {room.has_pin && (
                              <Badge className="gap-1 normal-case">
                                <Lock size={10} />
                                PIN
                              </Badge>
                            )}
                            {room.vibe_tags?.map((tag) => (
                              <Badge key={tag} variant="host" className="normal-case">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          <h3 className="heading-md group-hover:text-joint-green">
                            {room.title}
                          </h3>
                          {room.location && (
                            <p className="mt-1 flex items-center gap-1 text-sm text-smoke">
                              <MapPin size={14} />
                              {room.location}
                            </p>
                          )}
                          {countdown && <p className="mt-1 text-xs text-ember">{countdown}</p>}
                          {activity && <p className="mt-1 text-xs text-joint-green">{activity}</p>}
                          {(room.message_count ?? 0) > 0 && room.last_message_at && (
                            <p className="mt-0.5 text-[10px] text-smoke">
                              Last yap {formatRelativeTime(room.last_message_at)}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="flex items-center justify-end gap-1 text-sm text-smoke">
                            <Users size={14} />
                            {room.member_count} in
                          </p>
                          <p className="mt-1 text-xs text-smoke">by {room.host_name}</p>
                        </div>
                      </div>
                    </Card>
                  </Link>
                </motion.div>
              </FadeIn>
            )
          })}
        </div>
      </PageTransition>
    </AppShell>
  )
}
