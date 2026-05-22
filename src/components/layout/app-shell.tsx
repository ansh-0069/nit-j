import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Logo, Wordmark } from '@/components/brand/logo'
import { cn } from '@/lib/cn'

export function AppShell({
  children,
  showBrand = true,
  backTo,
}: {
  children: React.ReactNode
  showBrand?: boolean
  backTo?: string
}) {
  return (
    <div className="mx-auto min-h-screen max-w-5xl px-4 pb-24 pt-6 md:px-6 md:pt-8">
      <header className="mb-8 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          {showBrand && (
            <>
              <Logo size="sm" />
              <Wordmark className="hidden sm:block [&_span]:text-2xl" />
            </>
          )}
        </Link>
        {backTo && (
          <Link
            to={backTo}
            className="flex items-center gap-1.5 text-sm text-smoke transition hover:text-joint-green"
          >
            <ArrowLeft size={16} />
            Back
          </Link>
        )}
      </header>
      {children}
    </div>
  )
}

export function SectionLabel({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <p className={cn('label-caps mb-3', className)}>
      {children}
    </p>
  )
}
