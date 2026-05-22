import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '@/lib/cn'

export const Tabs = TabsPrimitive.Root

export function TabsList({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      className={cn(
        'grid w-full grid-cols-2 gap-1.5 rounded-full border-2 border-kush/40 bg-surface p-1.5 md:grid-cols-4',
        className,
      )}
      {...props}
    />
  )
}

export function TabsTrigger({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.Trigger>) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        'rounded-full px-3 py-2.5 font-body text-xs font-medium text-smoke transition-all data-[state=active]:border-2 data-[state=active]:border-joint-green/50 data-[state=active]:bg-gradient-to-r data-[state=active]:from-joint-green/25 data-[state=active]:to-kush/20 data-[state=active]:font-semibold data-[state=active]:text-joint-green data-[state=active]:shadow-md data-[state=active]:shadow-joint-green/20',
        className,
      )}
      {...props}
    />
  )
}

export function TabsContent({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.Content>) {
  return (
    <TabsPrimitive.Content
      className={cn('mt-4 focus-visible:outline-none', className)}
      {...props}
    />
  )
}
