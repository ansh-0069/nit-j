import { cn } from '@/lib/cn'

export function Logo({ className, size = 'md' }: { className?: string; size?: 'sm' | 'md' | 'lg' }) {
  const sizes = { sm: 'h-10 w-10 text-xl', md: 'h-14 w-14 text-2xl', lg: 'h-20 w-20 text-4xl' }

  return (
    <div
      className={cn(
        'relative flex items-center justify-center rounded-2xl border-2 border-joint-green/50 bg-gradient-to-br from-kush/40 via-surface to-nit-navy glow-green sticker',
        sizes[size],
        className,
      )}
      style={{ animation: 'pulse-glow 3s ease-in-out infinite' }}
    >
      <span className="drop-shadow-[0_0_8px_rgba(57,255,20,0.8)]">🌿</span>
      <span className="absolute -right-1 -top-1 text-sm">💨</span>
    </div>
  )
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <div className={cn('font-display', className)}>
      <h1 className="text-[2rem] font-semibold leading-tight tracking-tight md:text-[2.75rem]">
        <span className="text-white">NIT</span>
        <span className="text-gradient">-JOINT</span>
      </h1>
      <p className="mt-1.5 font-body text-xs font-normal tracking-[0.2em] text-smoke uppercase">
        no cap zone 🚬
      </p>
    </div>
  )
}
