import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from '@/App'
import '@/index.css'

if (import.meta.env.PROD) {
  import('virtual:pwa-register').then(({ registerSW }) => {
    registerSW({ immediate: true })
  })
} else if ('serviceWorker' in navigator) {
  // Stale SW from earlier builds can break API POSTs in dev — clear it
  navigator.serviceWorker.getRegistrations().then((regs) => {
    for (const reg of regs) reg.unregister()
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
