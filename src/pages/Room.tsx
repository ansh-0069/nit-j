import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { MessageList } from '@/components/chat/message-list'
import { ChatInput } from '@/components/chat/chat-input'
import { RunSheet } from '@/components/checklist/run-sheet'
import { KittyPanel } from '@/components/expenses/kitty-panel'
import { AppShell } from '@/components/layout/app-shell'
import { PageTransition } from '@/components/motion/page-transition'
import { JoinPanel } from '@/components/room/join-panel'
import { MemberList } from '@/components/room/member-list'
import { RoomHeader } from '@/components/room/room-header'
import { PlaylistBar } from '@/components/room/playlist-bar'
import { PullUpStatus } from '@/components/room/pull-up-status'
import { SessionEndedOverlay } from '@/components/room/session-ended-overlay'
import { Card } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  useChecklistMutations,
  useExpenseMutations,
  useJoinRoom,
  usePostMessage,
  useRoom,
  useEndRoom,
  useUpdatePlaylist,
  useTransferHost,
  useMemberStatus,
} from '@/hooks/use-room'
import { useUser } from '@/hooks/use-user'
import { namesMatch } from '@/lib/names'
import { addToCrew, markFirstJoin, markRoomSeen } from '@/lib/trusted-crew'
import type { MemberStatus } from '@/types'

export default function Room() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const { user, saveUser } = useUser()
  const { data: room, isLoading, error } = useRoom(code)
  const joinMutation = useJoinRoom(code ?? '')
  const messageMutation = usePostMessage(code ?? '')
  const checklist = useChecklistMutations(code ?? '')
  const expenses = useExpenseMutations(code ?? '')
  const playlistMutation = useUpdatePlaylist(code ?? '')
  const endMutation = useEndRoom(code ?? '')
  const transferMutation = useTransferHost(code ?? '')
  const statusMutation = useMemberStatus(code ?? '')
  const [showEnded, setShowEnded] = useState(false)

  const isMember = room?.members.some((m) => namesMatch(m.name, user)) ?? false
  const isHost = room ? namesMatch(room.host_name, user) : false
  const isArchived = room?.is_archived ?? false
  const myMember = room?.members.find((m) => namesMatch(m.name, user))
  const myStatus = (myMember?.status ?? 'here') as MemberStatus

  useEffect(() => {
    if (room && code) {
      markRoomSeen(code, room.last_message_at)
    }
  }, [room?.last_message_at, code, room])

  function handleEndSesh(permanent: boolean) {
    const name = user.trim()
    if (!code) {
      toast.error('Invalid room')
      return
    }
    if (!name) {
      toast.error('Set your name first')
      return
    }
    setShowEnded(true)
    endMutation.mutate(
      { actorName: name, permanent },
      {
        onSuccess: () => {
          toast.success(permanent ? 'Sesh deleted' : 'Sesh wrapped up')
          setTimeout(() => navigate('/'), permanent ? 1200 : 1800)
        },
        onError: (err) => {
          setShowEnded(false)
          toast.error(err.message)
        },
      },
    )
  }

  function handleJoin(data: { name: string; pin?: string; block?: string }) {
    saveUser(data.name)
    addToCrew(data.name, data.block)
    joinMutation.mutate(data, {
      onSuccess: () => {
        markFirstJoin()
        window.dispatchEvent(new Event('nit-joint-joined'))
        toast.success("You're in — let's plan")
      },
      onError: (err) => toast.error(err.message),
    })
  }

  if (isLoading) {
    return (
      <AppShell backTo="/">
        <div className="flex min-h-[50vh] items-center justify-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
            className="h-10 w-10 rounded-full border-2 border-joint-green border-t-transparent"
          />
        </div>
      </AppShell>
    )
  }

  if (!room) {
    return (
      <AppShell backTo="/">
        <Card className="text-center">
          <p className="text-danger">{error?.message ?? 'Room not found'}</p>
        </Card>
      </AppShell>
    )
  }

  if (!isMember) {
    return (
      <AppShell backTo="/">
        <PageTransition>
          <SessionEndedOverlay show={showEnded} />
          <div className="mb-6">
            <RoomHeader room={room} isHost={isHost} />
          </div>
          <JoinPanel room={room} defaultName={user} loading={joinMutation.isPending} onJoin={handleJoin} />
        </PageTransition>
      </AppShell>
    )
  }

  return (
    <AppShell backTo="/">
      <PageTransition>
        <SessionEndedOverlay show={showEnded} />
        <div className="mb-6">
          <RoomHeader
            room={room}
            isHost={isHost}
            onEnd={handleEndSesh}
            onTransferHost={(newHost) =>
              transferMutation.mutate(
                { actorName: user, newHostName: newHost },
                {
                  onSuccess: () => toast.success(`Host passed to ${newHost}`),
                  onError: (err) => toast.error(err.message),
                },
              )
            }
            ending={endMutation.isPending}
            transferring={transferMutation.isPending}
          />
        </div>

        {!isArchived && (
          <div className="mb-6">
            <Card className="p-4">
              <p className="label-caps mb-2">Your status</p>
              <PullUpStatus
                currentStatus={myStatus}
                loading={statusMutation.isPending}
                onUpdate={(status) =>
                  statusMutation.mutate(
                    { name: user, status },
                    { onError: (err) => toast.error(err.message) },
                  )
                }
              />
            </Card>
          </div>
        )}

        <div className="mb-6">
          <PlaylistBar
            room={room}
            saving={playlistMutation.isPending}
            disabled={isArchived}
            onSave={(url) =>
              playlistMutation.mutate(url, {
                onSuccess: () => toast.success(url ? 'Playlist saved' : 'Playlist removed'),
                onError: (err) => toast.error(err.message),
              })
            }
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <Card className="hidden lg:block">
            <p className="label-caps mb-3 text-haze">The boys 👊</p>
            <MemberList members={room.members} hostName={room.host_name} />
          </Card>

          <div>
            <Tabs defaultValue="chat">
              <TabsList>
                <TabsTrigger value="chat">Yap 💬</TabsTrigger>
                <TabsTrigger value="checklist">Grab list 🛒</TabsTrigger>
                <TabsTrigger value="expenses">The tab 💸</TabsTrigger>
                <TabsTrigger value="members" className="lg:hidden">
                  Boys 👊
                </TabsTrigger>
              </TabsList>

              <AnimatePresence mode="wait">
                <TabsContent value="chat" forceMount>
                  <Card className="flex min-h-[480px] flex-col">
                    <MessageList messages={room.messages} currentUser={user} />
                    {!isArchived && (
                      <ChatInput
                        disabled={messageMutation.isPending}
                        onSend={(content) =>
                          messageMutation.mutate(
                            { author: user, content },
                            { onError: (err) => toast.error(err.message) },
                          )
                        }
                      />
                    )}
                  </Card>
                </TabsContent>

                <TabsContent value="checklist">
                  <Card>
                    <RunSheet
                      items={room.checklist}
                      currentUser={user}
                      readOnly={isArchived}
                      onClaim={(id, claimedBy) =>
                        checklist.claim.mutate(
                          { id, claimedBy },
                          {
                            onSuccess: () =>
                              toast.success(claimedBy ? 'Locked in — you got this' : 'Unclaimed'),
                            onError: (err) => toast.error(err.message),
                          },
                        )
                      }
                      onAdd={(item) => checklist.add.mutate(item, { onError: (err) => toast.error(err.message) })}
                      onRemove={(id) => checklist.remove.mutate(id)}
                    />
                  </Card>
                </TabsContent>

                <TabsContent value="expenses">
                  <Card>
                    <KittyPanel
                      room={room}
                      currentUser={user}
                      readOnly={isArchived}
                      onAdd={(data) => expenses.add.mutate(data, { onError: (err) => toast.error(err.message) })}
                      onRemove={(id) => expenses.remove.mutate(id)}
                    />
                  </Card>
                </TabsContent>

                <TabsContent value="members" className="lg:hidden">
                  <Card>
                    <MemberList members={room.members} hostName={room.host_name} />
                  </Card>
                </TabsContent>
              </AnimatePresence>
            </Tabs>
          </div>
        </div>
      </PageTransition>
    </AppShell>
  )
}
