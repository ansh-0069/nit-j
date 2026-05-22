import { motion } from 'framer-motion'
import { cn } from '@/lib/cn'

export function PageTransition({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}

export function FadeIn({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
    >
      {children}
    </motion.div>
  )
}

export function ScaleTap({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div whileTap={{ scale: 0.97 }} className={className}>
      {children}
    </motion.div>
  )
}
