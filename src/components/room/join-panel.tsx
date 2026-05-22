import { motion } from 'framer-motion'
import { Lock, Sparkles } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { joinRoomSchema } from '@/lib/schemas'
import { getCrewBlock, isTrustedCrew } from '@/lib/trusted-crew'
import type { z } from 'zod'
import type { Room } from '@/types'

type JoinForm = z.infer<typeof joinRoomSchema>

export function JoinPanel({
  room,
  defaultName,
  onJoin,
  loading,
}: {
  room: Room
  defaultName?: string
  onJoin: (data: { name: string; pin?: string; block?: string }) => void
  loading: boolean
}) {
  const crewBlock = defaultName ? getCrewBlock(defaultName) : undefined
  const trusted = defaultName ? isTrustedCrew(defaultName) : false

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<JoinForm>({
    resolver: zodResolver(joinRoomSchema),
    defaultValues: { code: room.code, name: defaultName ?? '', pin: '' },
  })

  return (
    <Card className="mx-auto max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles size={20} className="text-joint-green" />
          Pull up to the sesh 🌿
        </CardTitle>
        <CardDescription>
          {room.members.length}/{room.max_capacity} deep · hosted by {room.host_name}
          {trusted && ' · you\'re on the crew 👊'}
        </CardDescription>
      </CardHeader>

      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        onSubmit={handleSubmit((data) => {
          onJoin({
            name: data.name,
            pin: data.pin || undefined,
            block: crewBlock,
          })
        })}
        className="space-y-4"
      >
        <input type="hidden" {...register('code')} />
        <div>
          <Label htmlFor="join-name">Your name</Label>
          <Input id="join-name" placeholder="What do the boys call you?" {...register('name')} />
          {errors.name && <p className="mt-1 text-xs text-danger">{errors.name.message}</p>}
        </div>
        {room.has_pin && (
          <div>
            <Label htmlFor="join-pin" className="flex items-center gap-1">
              <Lock size={12} />
              Room PIN
            </Label>
            <Input
              id="join-pin"
              className="font-mono tracking-[0.5em]"
              placeholder="••••"
              maxLength={4}
              inputMode="numeric"
              {...register('pin')}
            />
            {errors.pin && <p className="mt-1 text-xs text-danger">{errors.pin.message}</p>}
          </div>
        )}
        {crewBlock && (
          <p className="text-xs text-joint-green">Block from crew list: {crewBlock}</p>
        )}
        <Button type="submit" className="w-full" size="lg" disabled={loading}>
          {loading ? 'Pulling up...' : 'I\'m in 👊'}
        </Button>
      </motion.form>
    </Card>
  )
}
