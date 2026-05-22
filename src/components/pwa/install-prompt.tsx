import { useEffect, useState } from 'react'
import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { hasJoinedBefore } from '@/lib/trusted-crew'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function InstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null)
  const [dismissed, setDismissed] = useState(() => localStorage.getItem('nit-pwa-dismiss') === '1')
  const [isStandalone, setIsStandalone] = useState(false)
  const [ready, setReady] = useState(hasJoinedBefore())

  useEffect(() => {
    setIsStandalone(window.matchMedia('(display-mode: standalone)').matches)

    function onPrompt(e: Event) {
      e.preventDefault()
      setDeferred(e as BeforeInstallPromptEvent)
    }

    window.addEventListener('beforeinstallprompt', onPrompt)
    return () => window.removeEventListener('beforeinstallprompt', onPrompt)
  }, [])

  useEffect(() => {
    if (hasJoinedBefore()) setReady(true)
    function onJoined() {
      setReady(true)
    }
    window.addEventListener('nit-joint-joined', onJoined)
    return () => window.removeEventListener('nit-joint-joined', onJoined)
  }, [])

  if (isStandalone || dismissed || !deferred || !ready) return null

  return (
    <div className="mb-6 flex items-center justify-between gap-3 rounded-xl border border-joint-green/30 bg-joint-green/10 p-4">
      <div className="flex items-center gap-3">
        <Download size={20} className="shrink-0 text-joint-green" />
        <div>
          <p className="heading-md text-sm">Install NIT-JOINT</p>
          <p className="text-xs text-smoke">You&apos;ve pulled up — add to home screen for quick access</p>
        </div>
      </div>
      <div className="flex gap-2">
        <Button
          size="sm"
          onClick={async () => {
            await deferred.prompt()
            setDeferred(null)
          }}
        >
          Install
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            localStorage.setItem('nit-pwa-dismiss', '1')
            setDismissed(true)
          }}
        >
          Later
        </Button>
      </div>
    </div>
  )
}
