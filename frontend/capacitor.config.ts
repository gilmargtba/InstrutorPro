import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'br.com.instrutorprocnh.app',
  appName: 'InstrutorProCNH',
  webDir: 'dist/instrutorpro/browser',
  plugins: { CapacitorHttp: { enabled: true } },
};

export default config;
