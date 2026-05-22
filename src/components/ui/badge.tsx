import { cn } from '@/lib/cn'

const variants = {
  default: 'border-kush/50 bg-surface-2 text-smoke',
  live: 'border-ember/60 bg-ember/15 text-ember glow-ember animate-pulse',
  code: 'border-joint-green/50 bg-joint-green/15 font-mono text-joint-green tracking-[0.25em] glow-green',
  host: 'border-haze/50 bg-haze/15 text-haze',
  dank: 'border-joint-green/60 bg-gradient-to-r from-joint-green/20 to-kush/20 text-joint-green',
} as const

export function Badge({
  className,
  variant = 'default',
  ...props
}: React.ComponentProps<'span'> & { variant?: keyof typeof variants }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border-2 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider sticker',
        variants[variant],
        className,
      )}
      {...props}
    />
  )
}
