import { cn } from '@/lib/cn'

export function Textarea({ className, ...props }: React.ComponentProps<'textarea'>) {
  return (
    <textarea
      className={cn(
        'flex min-h-[88px] w-full rounded-2xl border-2 border-kush/40 bg-surface-2 px-4 py-3 text-sm text-white placeholder:text-smoke/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-joint-green/50 focus-visible:border-joint-green/50',
        className,
      )}
      {...props}
    />
  )
}
