import { motion } from 'framer-motion'
import { Copy, Check } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { cn } from '@/lib/cn'
import { Badge } from '@/components/ui/badge'

export function RoomCodePill({ code, className }: { code: string; className?: string }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    toast.success('Code copied — spam it in the gc 🔥')
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.button
      type="button"
      whileTap={{ scale: 0.95 }}
      onClick={handleCopy}
      className={cn(
        'group inline-flex items-center gap-2 rounded-full border-2 border-joint-green/50 bg-kush/30 px-5 py-2 font-mono text-lg font-semibold tracking-[0.3em] text-joint-green transition hover:glow-green sticker',
        className,
      )}
    >
      <Badge variant="code" className="border-0 bg-transparent p-0 text-lg tracking-[0.35em]">
        {code}
      </Badge>
      {copied ? (
        <Check size={16} className="text-joint-green" />
      ) : (
        <Copy size={16} className="text-smoke group-hover:text-joint-green" />
      )}
    </motion.button>
  )
}
