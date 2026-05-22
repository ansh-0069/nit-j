import { useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  addChecklistItem,
  addExpense,
  claimChecklistItem,
  createRoom,
  deleteChecklistItem,
  deleteExpense,
  endRoom,
  getRoom,
  joinRoom,
  listRooms,
  postMessage,
  subscribeGlobalEvents,
  subscribeRoomEvents,
  transferHost,
  updateMemberStatus,
  updateRoomPlaylist,
} from '@/api'
import { nowIst } from '@/lib/time'
import type { Room } from '@/types'

export function useRooms(vibe?: string) {
  const qc = useQueryClient()
  const query = useQuery({
    queryKey: ['rooms', vibe ?? 'all'],
    queryFn: () => listRooms(vibe),
    refetchInterval: 30_000,
  })

  useEffect(() => {
    return subscribeGlobalEvents(() => {
      qc.invalidateQueries({ queryKey: ['rooms'] })
    })
  }, [qc])

  return query
}

export function useRoom(code: string | undefined) {
  const qc = useQueryClient()
  const query = useQuery({
    queryKey: ['room', code],
    queryFn: () => getRoom(code!),
    enabled: !!code,
    refetchInterval: 15_000,
  })

  useEffect(() => {
    if (!code) return
    return subscribeRoomEvents(code, () => {
      qc.invalidateQueries({ queryKey: ['room', code] })
    })
  }, [code, qc])

  return query
}

export function useCreateRoom() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createRoom,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rooms'] }),
  })
}

export function useJoinRoom(code: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ name, pin, block }: { name: string; pin?: string; block?: string }) =>
      joinRoom(code, name, pin, block),
    onSuccess: (data) => {
      qc.setQueryData(['room', code], data)
      qc.invalidateQueries({ queryKey: ['rooms'] })
    },
  })
}

export function usePostMessage(code: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ author, content }: { author: string; content: string }) =>
      postMessage(code, author, content),
    onMutate: async ({ author, content }) => {
      await qc.cancelQueries({ queryKey: ['room', code] })
      const prev = qc.getQueryData<Room>(['room', code])
      if (prev) {
        qc.setQueryData<Room>(['room', code], {
          ...prev,
          messages: [
            ...prev.messages,
            {
              id: Date.now(),
              room_id: prev.id,
              author,
              content,
              type: 'user',
              created_at: nowIst(),
            },
          ],
        })
      }
      return { prev }
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev) qc.setQueryData(['room', code], ctx.prev)
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ['room', code] }),
  })
}

export function useChecklistMutations(code: string) {
  const qc = useQueryClient()
  const invalidate = () => qc.invalidateQueries({ queryKey: ['room', code] })

  return {
    add: useMutation({ mutationFn: (item: string) => addChecklistItem(code, item), onSuccess: invalidate }),
    claim: useMutation({
      mutationFn: ({ id, claimedBy }: { id: number; claimedBy: string | null }) =>
        claimChecklistItem(code, id, claimedBy),
      onSuccess: invalidate,
    }),
    remove: useMutation({
      mutationFn: (id: number) => deleteChecklistItem(code, id),
      onSuccess: invalidate,
    }),
  }
}

export function useExpenseMutations(code: string) {
  const qc = useQueryClient()
  const invalidate = () => qc.invalidateQueries({ queryKey: ['room', code] })

  return {
    add: useMutation({
      mutationFn: (data: { description: string; amount: number; paidBy: string }) =>
        addExpense(code, data),
      onSuccess: invalidate,
    }),
    remove: useMutation({
      mutationFn: (id: number) => deleteExpense(code, id),
      onSuccess: invalidate,
    }),
  }
}

export function useUpdatePlaylist(code: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (playlistUrl: string | null) => updateRoomPlaylist(code, playlistUrl),
    onSuccess: (data) => {
      qc.setQueryData(['room', code], data)
    },
  })
}

export function useEndRoom(code: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ actorName, permanent }: { actorName: string; permanent?: boolean }) =>
      endRoom(code, actorName, permanent),
    onSuccess: () => {
      qc.removeQueries({ queryKey: ['room', code] })
      qc.invalidateQueries({ queryKey: ['rooms'] })
    },
  })
}

export function useTransferHost(code: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ actorName, newHostName }: { actorName: string; newHostName: string }) =>
      transferHost(code, actorName, newHostName),
    onSuccess: (data) => {
      qc.setQueryData(['room', code], data)
      qc.invalidateQueries({ queryKey: ['rooms'] })
    },
  })
}

export function useMemberStatus(code: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ name, status }: { name: string; status: string }) =>
      updateMemberStatus(code, name, status),
    onSuccess: (data) => {
      qc.setQueryData(['room', code], data)
    },
  })
}
