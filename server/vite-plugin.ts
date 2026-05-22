import type { Plugin, PreviewServer, ViteDevServer } from 'vite'
import { createApp } from './app.js'

function attachApi(server: ViteDevServer | PreviewServer) {
  const app = createApp()
  server.middlewares.use(app)
  console.log('NIT Joint API embedded (/api)')
}

export function nitJointApiPlugin(): Plugin {
  return {
    name: 'nit-joint-api',
    configureServer(server) {
      attachApi(server)
    },
    configurePreviewServer(server) {
      attachApi(server)
    },
  }
}
