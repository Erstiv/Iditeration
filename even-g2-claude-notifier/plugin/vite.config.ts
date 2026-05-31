import { defineConfig } from "vite";

// Even Hub plugins are served from a relative base so they work when packaged
// into an .ehpk and loaded inside the phone-app WebView.
export default defineConfig({
  base: "./",
  build: {
    outDir: "dist",
    target: "es2020",
  },
});
