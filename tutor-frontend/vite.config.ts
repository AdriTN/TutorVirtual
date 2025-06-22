import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";
import path from "node:path";


export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [
      react(),
      svgr(),
    ],

    resolve: {
      alias: [
        { find: "@",           replacement: path.resolve(__dirname, "src") },
        { find: "@app",        replacement: path.resolve(__dirname, "src/app") },
        { find: "@services",   replacement: path.resolve(__dirname, "src/services") },
        { find: "@components", replacement: path.resolve(__dirname, "src/components") },
        { find: "@context",    replacement: path.resolve(__dirname, "src/context") },
        { find: "@hooks",      replacement: path.resolve(__dirname, "src/hooks") },
        { find: "@assets",     replacement: path.resolve(__dirname, "src/assets") },
        { find: "@utils",      replacement: path.resolve(__dirname, "src/utils") },
        { find: "@styles",     replacement: path.resolve(__dirname, "src/styles") },
        { find: "@features",   replacement: path.resolve(__dirname, "src/features") },
        { find: "@types",      replacement: path.resolve(__dirname, "src/types") },
      ],
    },

    css: {
      modules: {
        generateScopedName:
          process.env.NODE_ENV === "production"
            ? "[hash:base64:6]"
            : "[name]__[local]__[hash:base64:3]",
      },
    },

    server: {
      port: 5173,
      open: true,
      proxy: {
        "/api": {
          target: env.VITE_BACKEND_URL,
          changeOrigin: true,
          secure: false,
        },
      },
    },

    build: {
      outDir: "dist",
      sourcemap: true,
    },
  };
});
