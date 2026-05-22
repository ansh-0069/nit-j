import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/cn'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-semibold tracking-normal transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-joint-green/50 disabled:pointer-events-none disabled:opacity-50 active:scale-95',
  {
    variants: {
      variant: {
        default:
          'border-2 border-joint-green/60 bg-gradient-to-r from-joint-green via-joint-dim to-lime-400 text-nit-deep shadow-lg shadow-joint-green/30 hover:brightness-110 hover:shadow-joint-green/50',
        secondary:
          'border-2 border-kush/50 bg-surface-2 text-white hover:border-haze/50 hover:bg-surface-3',
        ghost: 'text-smoke hover:bg-surface-2 hover:text-joint-green',
        danger: 'border-2 border-danger/50 bg-danger/15 text-danger hover:bg-danger/25',
        outline:
          'border-2 border-haze/60 bg-transparent text-haze hover:bg-haze/10 hover:glow-haze',
      },
      size: {
        default: 'h-11 px-6 py-2',
        sm: 'h-9 rounded-full px-4 text-xs',
        lg: 'h-12 rounded-full px-10 text-base',
        icon: 'h-11 w-11 rounded-full',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : 'button'
  return <Comp className={cn(buttonVariants({ variant, size, className }))} {...props} />
}
