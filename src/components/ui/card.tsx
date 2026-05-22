import { cn } from '@/lib/cn'

export function Card({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      className={cn(
        'glass-fun rounded-3xl p-5 shadow-xl shadow-kush/10 sticker',
        className,
      )}
      {...props}
    />
  )
}

export function CardHeader({ className, ...props }: React.ComponentProps<'div'>) {
  return <div className={cn('mb-4 space-y-1', className)} {...props} />
}

export function CardTitle({ className, ...props }: React.ComponentProps<'h3'>) {
  return (
    <h3
      className={cn('font-display text-lg font-semibold tracking-tight text-joint-green', className)}
      {...props}
    />
  )
}

export function CardDescription({ className, ...props }: React.ComponentProps<'p'>) {
  return <p className={cn('text-sm text-smoke/90', className)} {...props} />
}
