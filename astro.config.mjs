import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://garagetoolsdb.com',
  compressHTML: true,
  integrations: [sitemap()],
  build: {
    format: 'file'
  },
  server: {
    host: '0.0.0.0',
    port: 8082
  },
  devToolbar: { enabled: false },
  allowedHosts: ['garagetoolsdb.com', 'www.garagetoolsdb.com']
});