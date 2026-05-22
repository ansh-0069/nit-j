import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import { OfflineBanner } from '@/components/layout/offline-banner'
import Home from '@/pages/Home'
import Room from '@/pages/Room'
import Sellers from '@/pages/Sellers'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2000,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <OfflineBanner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/sellers" element={<Sellers />} />
          <Route path="/room/:code" element={<Room />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster
        theme="dark"
        position="top-center"
        toastOptions={{
          classNames: {
            toast: 'glass border-border text-white font-body',
            success: 'border-joint-green/40',
            error: 'border-danger/40',
          },
        }}
      />
    </QueryClientProvider>
  )
}

export default App
