import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '')

    return {
        plugins: [react(), tailwindcss()],
        resolve: {
            alias: {
                "@": path.resolve(__dirname, "./src"),
            },
        },
        server: {
            port: 3000,
            host: true,
            proxy: {
                // /static 요청을 백엔드로 프록시 — ngrok 인터스티셜 우회 헤더 포함
                '/static': {
                    target: env.VITE_API_URL,
                    changeOrigin: true,
                    headers: { 'ngrok-skip-browser-warning': 'true' },
                },
            },
        },
    }
})
