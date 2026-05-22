import { Send } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { messageSchema } from '@/lib/schemas'
import type { z } from 'zod'

type MessageForm = z.infer<typeof messageSchema>

export function ChatInput({ onSend, disabled }: { onSend: (content: string) => void; disabled?: boolean }) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<MessageForm>({
    resolver: zodResolver(messageSchema),
  })

  return (
    <form
      className="mt-4 flex gap-2"
      onSubmit={handleSubmit((data) => {
        onSend(data.content)
        reset()
      })}
    >
      <Input
        placeholder="Send it to the boys..."
        disabled={disabled}
        {...register('content')}
      />
      <Button type="submit" size="icon" disabled={disabled}>
        <Send size={18} />
      </Button>
      {errors.content && <span className="sr-only">{errors.content.message}</span>}
    </form>
  )
}
