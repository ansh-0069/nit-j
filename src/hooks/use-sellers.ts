import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { listSellers, registerSeller, removeSeller, updateSeller } from '@/api'

export function useSellers() {
  return useQuery({
    queryKey: ['sellers'],
    queryFn: listSellers,
    refetchInterval: 5000,
  })
}

export function useRegisterSeller() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: registerSeller,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sellers'] }),
  })
}

export function useUpdateSeller() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...data }: { id: number; actorName: string; block?: string; contact?: string; available?: boolean; note?: string }) =>
      updateSeller(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sellers'] }),
  })
}

export function useRemoveSeller() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, actorName }: { id: number; actorName: string }) => removeSeller(id, actorName),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sellers'] }),
  })
}
