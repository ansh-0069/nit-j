import { useEffect, useState } from 'react'
import { WifiOff } from 'lucide-react'

export function OfflineBanner() {
  const [offline, setOffline] = useState(!navigator.onLine)

  useEffect(() => {
    function onOffline() {
      setOffline(true)
    }
    function onOnline() {
      setOffline(false)
    }
    window.addEventListener('offline', onOffline)
    window.addEventListener('online', onOnline)
    return () => {
      window.removeEventListener('offline', onOffline)
      window.removeEventListener('online', onOnline)
    }
  }, [])

  if (!offline) return null

  return (
    <div className="fixed inset-x-0 top-0 z-50 flex items-center justify-center gap-2 bg-danger/90 px-4 py-2 text-sm font-medium text-white">
      <WifiOff size={16} />
      You&apos;re offline — changes will sync when you&apos;re back
    </div>
  )
}
