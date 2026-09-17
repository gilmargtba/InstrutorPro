import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

type LegalDocument = {
  title: string;
  audience: 'STUDENT' | 'INSTRUCTOR';
  version: string;
  effective_at: string;
  content: string;
  content_sha256: string;
  contact: string;
};

@Component({
  selector: 'app-legal-terms',
  template: `<article class="page narrow policy">
    @if (document(); as doc) {
      <p class="eyebrow">Versão {{ doc.version }} · vigência {{ effectiveDate(doc.effective_at) }}</p>
      <h1>{{ doc.title }}</h1>
      <div class="legal-content">{{ doc.content }}</div>
      <p><strong>Canal de contato:</strong> <a [href]="'mailto:' + doc.contact">{{ doc.contact }}</a></p>
    } @else if (failed()) {
      <h1>Termos temporariamente indisponíveis</h1>
      <p>Não prossiga com cadastro ou aceite enquanto o documento vigente não estiver disponível.</p>
    } @else {
      <p>Carregando documento vigente…</p>
    }
  </article>`,
  styles: [`.legal-content{white-space:pre-line;line-height:1.65}`],
})
export class LegalTermsComponent {
  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);
  document = signal<LegalDocument | undefined>(undefined);
  failed = signal(false);

  constructor() {
    const audience = this.route.snapshot.data['audience'] as string;
    this.http.get<LegalDocument>(`/legal/documents/${audience}/`).subscribe({
      next: value => this.document.set(value),
      error: () => this.failed.set(true),
    });
  }

  effectiveDate(value: string) {
    return new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Sao_Paulo' }).format(new Date(value));
  }
}
