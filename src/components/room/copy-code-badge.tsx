import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/cn'

export function CopyCodeBadge({ code, className }: { code: string; className?: string }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy(e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    await navigator.clipboard.writeText(code)
    setCopied(true)
    toast.success('Code copied')
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={cn('inline-flex items-center gap-1', className)}
    >
      <Badge variant="code" className="gap-1">
        {code}
        {copied ? <Check size={10} /> : <Copy size={10} className="opacity-60" />}
      </Badge>
    </button>
  )
}
