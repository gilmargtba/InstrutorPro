import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { InstructorSearchProvider, AvailabilityInterestPolicy } from '../../demo/instructor-search.provider';
import { BRAZIL_UFS } from '../../shared/brazil-ufs';

@Component({
  selector: 'app-no-instructor',
  imports: [FormsModule, RouterLink],
  template: `
    <section class="interest-page">
      <div class="interest-hero">
        <p class="eyebrow">Para alunos</p>
        <h1>Sem instrutor na sua região?</h1>
        <p>Procure na sua cidade ou deixe um pedido de aviso para quando houver instrutor disponível.</p>
        <a routerLink="/aluno/instrutores/mapa">Buscar instrutores novamente</a>
      </div>
      <div class="interest-content">
        <div class="steps">
          <h2>Como funciona</h2>
          <p><strong>1. Informe a localidade.</strong> Escolha UF, cidade ou região, sem endereço residencial.</p>
          <p><strong>2. Deixe seu contato.</strong> Informe nome, WhatsApp e confirme o aviso de privacidade.</p>
          <p><strong>3. Aguarde o contato.</strong> Nossa equipe poderá avisar manualmente quando houver disponibilidade.</p>
        </div>
        <div class="interest-card">
          @if (loading) {<p role="status">Verificando disponibilidade do cadastro…</p>}
          @else if (saved) {
            <h2>Pedido recebido</h2>
            <p>Protocolo: <strong>{{reference}}</strong>. Guarde este número para solicitar retirada do pedido.</p>
            <p>A equipe poderá entrar em contato pelo WhatsApp dentro do prazo informado.</p>
            <a href="mailto:focusgtba@gmail.com?subject=Retirada%20de%20interesse%20em%20instrutor">Contatar privacidade</a>
          } @else if (!policy?.enabled) {
            <h2>Cadastro de interesse indisponível</h2>
            <p>O formulário será liberado quando o aviso de privacidade e o atendimento manual estiverem ativos.</p>
            <a routerLink="/aluno/instrutores/mapa">Voltar à busca</a>
          } @else {
            <h2>Quero ser avisado</h2>
            <form (ngSubmit)="submit()">
              <label>Área de interesse<select name="scope" [(ngModel)]="scope"><option value="UF">Toda a UF</option><option value="CITY">Cidade</option><option value="REGION">Região da cidade</option></select></label>
              <label>UF<select name="uf" [(ngModel)]="uf" required><option value="">Selecione a UF</option>@for(item of ufs;track item){<option [value]="item">{{item}}</option>}</select></label>
              @if(scope !== 'UF'){<label>Cidade<input name="city" [(ngModel)]="city" required maxlength="120" /></label>}
              @if(scope === 'REGION'){<label>Bairro ou região<input name="region" [(ngModel)]="region" required maxlength="120" /></label>}
              <label>Nome completo<input name="name" [(ngModel)]="name" required maxlength="120" autocomplete="name" /></label>
              <label>WhatsApp com DDD<input name="phone" [(ngModel)]="phone" required maxlength="24" inputmode="tel" autocomplete="tel" /></label>
              <label>Data de nascimento<input name="birthDate" [(ngModel)]="birthDate" required type="date" autocomplete="bday" /></label>
              <p>Dados guardados por até {{policy.retention_days}} dias. O aviso é manual e não há garantia de disponibilidade.</p>
              <label class="consent"><input name="consent" [(ngModel)]="consent" required type="checkbox" /> {{policy.consent_text}} <a routerLink="/privacidade" target="_blank" rel="noopener">Política de Privacidade</a></label>
              @if(error){<p role="alert">{{error}}</p>}
              <button type="submit" [disabled]="submitting">{{submitting ? 'Enviando…' : 'Quero receber o aviso'}}</button>
            </form>
          }
        </div>
      </div>
    </section>
  `,
  styles: [`
    .interest-page{color:#173c55;background:#f6faf9;min-height:70vh}
    .interest-hero{text-align:center;background:#e7f3f0;padding:3.5rem 1rem}
    .interest-hero h1{font-size:clamp(2rem,5vw,3.4rem);margin:.3rem 0}
    .interest-hero p{max-width:40rem;margin:0 auto 1.4rem;line-height:1.5}
    .interest-hero a,.interest-card button{display:inline-block;background:#087f83;color:white;border:0;border-radius:.5rem;padding:.8rem 1.1rem;text-decoration:none;font:inherit;cursor:pointer}
    .interest-content{max-width:68rem;margin:auto;padding:2rem 1rem;display:grid;grid-template-columns:1fr 1fr;gap:2rem}
    .steps p,.interest-card p{line-height:1.5}
    .interest-card{background:white;border:1px solid #cadbdc;border-radius:1rem;padding:1.4rem}
    form{display:grid;gap:.85rem}form label{display:grid;gap:.3rem;font-weight:600}
    input:not([type=checkbox]),select{width:100%;padding:.7rem;border:1px solid #a9bec5;border-radius:.45rem;font:inherit}
    .consent{display:block;font-weight:400}.consent input{margin-right:.4rem}
    button:disabled{opacity:.6;cursor:wait}@media(max-width:760px){.interest-content{grid-template-columns:1fr}}
  `],
})
export class NoInstructorComponent implements OnInit {
  private readonly api = inject(InstructorSearchProvider);
  private readonly route = inject(ActivatedRoute);
  readonly ufs = BRAZIL_UFS;
  policy: AvailabilityInterestPolicy | null = null;
  loading = true;
  saved = false;
  submitting = false;
  error = '';
  reference = '';
  scope: 'UF'|'CITY'|'REGION' = 'CITY';
  uf = '';
  city = '';
  region = '';
  name = '';
  phone = '';
  birthDate = '';
  consent = false;
  private idempotencyKey = crypto.randomUUID();

  ngOnInit(): void {
    const query = this.route.snapshot.queryParamMap;
    const uf = query.get('uf')?.toUpperCase() ?? '';
    if (this.ufs.includes(uf as typeof BRAZIL_UFS[number])) this.uf = uf;
    this.city = query.get('cidade')?.slice(0, 120) ?? '';
    this.region = query.get('regiao')?.slice(0, 120) ?? '';
    this.scope = this.region && this.city ? 'REGION' : this.city ? 'CITY' : 'UF';
    this.api.availabilityInterestPolicy().subscribe({
      next: policy => { this.policy = policy; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  submit(): void {
    if (!this.policy?.enabled || !this.uf || (this.scope !== 'UF' && !this.city.trim()) ||
        (this.scope === 'REGION' && !this.region.trim()) || !this.consent || this.submitting) return;
    this.submitting = true;
    this.error = '';
    this.api.submitAvailabilityInterest({
      scope: this.scope, city: this.city, region: this.region, uf: this.uf,
      name: this.name, phone: this.phone, birth_date: this.birthDate,
      privacy_notice_version: this.policy.privacy_notice_version ?? '',
      consent_version: this.policy.consent_version ?? '', consent_granted: true,
      idempotency_key: this.idempotencyKey,
    }).subscribe({
      next: result => { this.submitting = false; this.saved = true; this.reference = result.id; this.name = this.phone = this.birthDate = ''; this.idempotencyKey = crypto.randomUUID(); },
      error: (response: HttpErrorResponse) => {
        this.submitting = false;
        this.error = typeof response.error?.detail === 'string' ? response.error.detail : 'Não foi possível salvar. Confira os dados e tente novamente.';
      },
    });
  }
}
