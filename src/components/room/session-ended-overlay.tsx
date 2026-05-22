import { motion } from 'framer-motion'

export function SessionEndedOverlay({ show }: { show: boolean }) {
  if (!show) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-[#07050f]/90 backdrop-blur-sm"
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', damping: 14 }}
        className="text-center"
      >
        <motion.p
          animate={{ rotate: [0, -5, 5, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="text-6xl"
        >
          🌿
        </motion.p>
        <p className="heading-xl mt-4 text-gradient">Sesh wrapped</p>
        <p className="mt-2 text-smoke">See you at the next one...</p>
      </motion.div>
    </motion.div>
  )
}
