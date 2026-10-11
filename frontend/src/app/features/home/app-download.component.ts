import { Component, OnInit, signal } from '@angular/core';

const APK_PATH = '/downloads/InstrutorProCNH-android.apk';
const APK_SHA256 = 'D23707AF7B05E2C2E9C164C14434785036DC713D7DD6B695C3E35F993B43900E';

@Component({
  selector: 'app-download',
  template: `
    <section class="download-page">
      <p class="eyebrow">App do aluno</p>
      <h1>InstrutorProCNH para Android</h1>
      <p>Busque instrutores, consulte perfis públicos e escolha se deseja conversar pelo WhatsApp.</p>
      @if (status() === 'available') {
        <a class="button primary" [href]="apkPath" download="InstrutorProCNH-android.apk">Baixar APK para Android</a>
        <p class="checksum">Versão 1.0.1 · SHA-256: <code>{{ sha256 }}</code></p>
        <p class="notice">Instale apenas o arquivo baixado deste site. O Android pode pedir sua autorização para instalar um aplicativo fora da loja.</p>
      } @else if (status() === 'unavailable') {
        <p class="notice" role="status">O download do Android ainda não está disponível. Estamos preparando a versão assinada para instalação.</p>
      } @else {
        <p class="notice" role="status">Verificando a disponibilidade do aplicativo…</p>
      }
      <p>O aplicativo é para alunos. Cadastro e gestão de instrutores continuam disponíveis no site.</p>
    </section>
  `,
  styles: [`.download-page{max-width:48rem;min-height:60vh;margin:auto;padding:clamp(3rem,8vw,6rem) 1.5rem;color:#143f66}.download-page h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.1}.download-page p{line-height:1.6}.download-page .eyebrow{color:#087f8e;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.download-page .button{display:inline-block;margin:1rem 0}.download-page .notice{padding:1rem;border-radius:1rem;background:#e9f6f5}.checksum code{overflow-wrap:anywhere}`],
})
export class AppDownloadComponent implements OnInit {
  readonly apkPath = APK_PATH;
  readonly sha256 = APK_SHA256;
  readonly status = signal<'checking' | 'available' | 'unavailable'>('checking');

  async ngOnInit(): Promise<void> {
    try {
      const response = await fetch(APK_PATH, { method: 'HEAD', cache: 'no-store' });
      this.status.set(response.ok && response.headers.get('content-type')?.includes('application/vnd.android.package-archive') === true ? 'available' : 'unavailable');
    } catch {
      this.status.set('unavailable');
    }
  }
}
