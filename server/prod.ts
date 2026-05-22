import express from 'express'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createApp } from './app.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const PORT = Number(process.env.PORT) || 3001
const dist = path.join(__dirname, '..', 'dist')

const app = createApp()
app.use(express.static(dist))
app.use((req, res, next) => {
  if (req.path.startsWith('/api')) return next()
  res.sendFile(path.join(dist, 'index.html'))
})

app.listen(PORT, () => {
  console.log(`NIT Joint running on http://localhost:${PORT}`)
})
