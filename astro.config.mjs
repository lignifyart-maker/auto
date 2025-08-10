import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  integrations: [mdx()],
  site: 'https://example.vercel.app',
  markdown: {
    shikiConfig: { themes: { light: 'github-light', dark: 'github-dark' } }
  }
});