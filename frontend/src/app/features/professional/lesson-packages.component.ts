import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ProfessionalNavComponent } from './saas-pages.component';

interface LessonPackage {
  id: string; name: string; category: string; lesson_count: number;
  price_amount: number; price_per_lesson: number; vehicle_included: boolean;
  description: string; is_active: boolean; visible: boolean;
}
interface PackageList {
  plan_code: string; active_count: number; active_limit: number | null;
  packages: LessonPackage[];
}

@Component({
  selector: 'app-lesson-packages',
  imports: [FormsModule, RouterLink, ProfessionalNavComponent],
  template: `<section class="page wide"><app-professional-nav/>
    <header class="page-head"><div><p class="eyebrow">Aulas práticas</p><h1>Meus pacotes</h1></div></header>
    @if(data();as current){
      <p role="status">Plano {{current.plan_code}}: @if(current.active_limit===null){pacotes ilimitados disponíveis.}@else{você está utilizando {{current.active_count}} de {{current.active_limit}} pacote(s) ativo(s).}</p>
      @if(current.active_limit!==null && current.active_count>=current.active_limit){<p>O limite de pacotes ativos foi atingido. Você pode cadastrar um pacote inativo ou <a routerLink="/instrutor/plano">conhecer os planos superiores</a>. Não há upgrade automático.</p>}
      <p>Pacotes são ofertas comerciais; contratação e pagamento são combinados diretamente com o aluno. Não representam aulas oficialmente concluídas.</p>
      <div class="package-grid">@for(item of current.packages;track item.id){
        <article class="package-card"><h2>{{item.name}}</h2><p>Categoria {{item.category}} · {{item.lesson_count}} aulas · {{item.vehicle_included?'Com veículo':'Sem veículo'}}</p>
          <p><strong>{{formatPrice(item.price_amount)}}</strong> no total · {{formatPrice(item.price_per_lesson)}} por aula</p>
          @if(item.description){<p>{{item.description}}</p>}
          <p>{{item.is_active?(item.visible?'Ativo e visível':'Ativo, oculto pelo limite do plano ou categoria'): 'Inativo'}}</p>
          <button type="button" class="button secondary" (click)="edit(item)">Editar</button>
          <button type="button" class="button secondary" [disabled]="saving()" (click)="toggle(item)">{{item.is_active?'Desativar':'Ativar'}}</button>
        </article>
      }@empty{<p>Você ainda não cadastrou pacotes.</p>}</div>
      <h2>{{editingId()?'Editar pacote':'Cadastrar pacote'}}</h2>
      <form #packageForm="ngForm" class="package-form" (ngSubmit)="save(packageForm.valid)">
        <label>Nome do pacote<input name="name" [(ngModel)]="draft.name" maxlength="120" required></label>
        <label>Categoria<select name="category" [(ngModel)]="draft.category" required>@for(category of categories;track category){<option [value]="category">{{category}}</option>}</select></label>
        <label>Quantidade de aulas<select name="lessonCount" [(ngModel)]="draft.lesson_count" required><option [ngValue]="2">2</option><option [ngValue]="5">5</option><option [ngValue]="10">10</option></select></label>
        <label>Preço total (R$)<input name="price" type="number" step="0.01" min="0.01" [(ngModel)]="draft.price_amount" required></label>
        @if(draft.price_amount && draft.lesson_count){<p>Valor aproximado por aula: {{formatPrice(draft.price_amount/draft.lesson_count)}}</p>}
        <label class="check"><input name="vehicle" type="checkbox" [(ngModel)]="draft.vehicle_included"> Veículo incluído</label>
        <label>Descrição (opcional)<textarea name="description" [(ngModel)]="draft.description" maxlength="500"></textarea></label>
        <label class="check"><input name="active" type="checkbox" [(ngModel)]="draft.is_active"> Pacote ativo</label>
        <div class="actions"><button class="button primary" [disabled]="saving()">{{saving()?'Salvando…':'Salvar pacote'}}</button>@if(editingId()){<button type="button" class="button secondary" (click)="reset()">Cancelar edição</button>}</div>
      </form>
    }@else if(loading()){<p>Carregando pacotes…</p>}
    @if(error()){<p role="alert">{{error()}}</p>}
  </section>`,
  styles: [`.package-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin:1rem 0 2rem}.package-card,.package-form{padding:1.2rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.package-card button{margin:.3rem}.package-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;max-width:800px}.package-form label{display:grid;gap:.3rem;font-weight:700}.package-form input,.package-form select,.package-form textarea{padding:.7rem;border:1px solid #bad4d1;border-radius:.6rem}.package-form textarea{min-height:5rem}.package-form .check{display:flex;align-items:center}.actions{grid-column:1/-1;display:flex;gap:.6rem}@media(max-width:650px){.package-form{grid-template-columns:1fr}}`],
})
export class LessonPackagesComponent {
  private readonly http = inject(HttpClient);
  readonly categories = ['A', 'B', 'C', 'D', 'E'];
  readonly data = signal<PackageList | null>(null);
  readonly error = signal('');
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly editingId = signal<string | null>(null);
  draft = this.emptyDraft();

  constructor() { this.reload(); }

  private emptyDraft() { return { name: '', category: 'B', lesson_count: 2, price_amount: null as number | null, vehicle_included: false, description: '', is_active: true }; }
  reload() { this.loading.set(true); this.http.get<PackageList>('/marketplace/instructor/packages/').subscribe({ next: value => { this.data.set(value); this.loading.set(false); }, error: () => { this.loading.set(false); this.error.set('Não foi possível carregar os pacotes.'); } }); }
  edit(item: LessonPackage) { this.editingId.set(item.id); this.draft = { name: item.name, category: item.category, lesson_count: item.lesson_count, price_amount: item.price_amount, vehicle_included: item.vehicle_included, description: item.description, is_active: item.is_active }; this.error.set(''); }
  reset() { this.editingId.set(null); this.draft = this.emptyDraft(); this.error.set(''); }
  toggle(item: LessonPackage) { this.update(item.id, { is_active: !item.is_active }); }
  save(valid: boolean | null) {
    if (!valid || !this.draft.price_amount || this.draft.price_amount <= 0) { this.error.set('Preencha o nome e um preço total positivo.'); return; }
    const id = this.editingId();
    this.update(id, this.draft);
  }
  private update(id: string | null, payload: object) {
    this.saving.set(true); this.error.set('');
    const request = id ? this.http.patch(`/marketplace/instructor/packages/${id}/`, payload) : this.http.post('/marketplace/instructor/packages/', payload);
    request.subscribe({ next: () => { this.saving.set(false); this.reset(); this.reload(); }, error: response => { this.saving.set(false); this.error.set(response?.error?.detail || 'Não foi possível salvar o pacote.'); } });
  }
  formatPrice(value: number) { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value); }
}
