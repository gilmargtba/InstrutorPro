import { Component, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import type { DemoDemandState } from '../../demo/demo-data.providers';
import { InstructorSearchProvider } from '../../demo/instructor-search.provider';
import { BrazilDemandMapComponent } from './brazil-demand-map.component';

@Component({
  selector: 'app-instructor-national-map',
  imports: [BrazilDemandMapComponent],
  template: `
    <section class="national-search">
      <div class="demo-flag">DEMO · profissionais e quantidades sintéticos</div>
      <header>
        <p class="eyebrow">Busca nacional</p>
        <h1>Encontre instrutores em todo o Brasil</h1>
        <p>Os estados destacados possuem instrutores disponíveis na demonstração. Selecione uma UF para abrir o mapa local.</p>
      </header>

      @if (loading()) {
        <div class="state-message"><i class="pi pi-spin pi-spinner"></i> Carregando estados ativos…</div>
      } @else if (error()) {
        <div class="state-message error">Não foi possível carregar as quantidades. <button (click)="load()">Tentar novamente</button></div>
      } @else {
        <div class="national-grid">
          <app-brazil-demand-map
            [states]="states()"
            [selectedUf]="''"
            activeLabel="Estado com instrutores"
            inactiveLabel="Ainda sem instrutor disponível"
            countLabel="instrutores"
            (stateSelected)="openState($event)"
          />
          <aside>
            <small>ESTADOS ATIVOS</small>
            <h2>{{ total() }} instrutores disponíveis</h2>
            <p>Contagem por área pública de atendimento. Nenhum endereço residencial é exibido.</p>
            @for (state of states(); track state.uf) {
              <button type="button" (click)="openState(state.uf)">
                <span><strong>{{ state.uf }}</strong><small>{{ state.searchLocation }}</small></span>
                <b>{{ state.total }}</b>
                <i class="pi pi-arrow-right"></i>
              </button>
            }
            <p class="hint"><i class="pi pi-info-circle"></i> Estados sem número permanecem visíveis, mas ainda não têm instrutores publicados.</p>
          </aside>
        </div>
      }
    </section>
  `,
  styles: [`
    .national-search{max-width:82rem;margin:auto;padding:2rem 1.25rem 4rem}.national-search>header{max-width:48rem;margin-bottom:1.5rem}.national-search h1{margin:.25rem 0;font-size:clamp(2.2rem,5vw,4.6rem);line-height:1;color:#103f63}.national-search header p:last-child{font-size:1.1rem;color:#527083}.national-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(18rem,.8fr);overflow:hidden;border:1px solid #cee0de;border-radius:1.4rem;background:#fff}.national-grid aside{padding:2rem}.national-grid aside>small{color:#0b7d82;font-weight:800;letter-spacing:.08em}.national-grid aside h2{margin:.5rem 0;color:#103f63}.national-grid aside>p{color:#587181}.national-grid aside button{display:grid;grid-template-columns:1fr auto auto;align-items:center;width:100%;margin:.65rem 0;padding:.8rem 1rem;border:1px solid #d5e5e2;border-radius:.8rem;background:#fff;color:#103f63;text-align:left;cursor:pointer}.national-grid aside button:hover,.national-grid aside button:focus{border-color:#07888d;background:#eef9f7}.national-grid aside button span{display:flex;flex-direction:column}.national-grid aside button small{color:#68808b}.national-grid aside button b{margin-right:1rem;color:#07888d;font-size:1.2rem}.hint{padding-top:.7rem;border-top:1px solid #e4eeec;font-size:.82rem}.state-message{padding:3rem;border-radius:1rem;background:#eef8f6;text-align:center}.state-message.error{background:#fff0ed;color:#933}.state-message button{margin-left:.5rem}.demo-flag{display:inline-flex;margin-bottom:1rem;padding:.4rem .7rem;border-radius:2rem;background:#fff0e7;color:#b64b12;font-size:.75rem;font-weight:800}@media(max-width:900px){.national-grid{grid-template-columns:1fr}.national-grid aside{padding:1.25rem}} 
  `],
})
export class InstructorNationalMapComponent {
  private readonly api = inject(InstructorSearchProvider);
  private readonly router = inject(Router);
  readonly states = signal<DemoDemandState[]>([]);
  readonly loading = signal(true);
  readonly error = signal(false);
  readonly total = computed(() => this.states().reduce((sum, state) => sum + state.total, 0));

  constructor() { this.load(); }

  load() {
    this.loading.set(true);
    this.error.set(false);
    this.api.states().subscribe({
      next: response => {
        this.states.set(response.states.map(state => ({
          uf: state.uf,
          total: state.count,
          searchLocation: state.search_location,
          cities: [],
        })));
        this.loading.set(false);
      },
      error: () => { this.loading.set(false); this.error.set(true); },
    });
  }

  openState(uf: string) {
    const state = this.states().find(item => item.uf === uf);
    if (!state) return;
    void this.router.navigate(['/aluno/instrutores/mapa'], {
      queryParams: { uf: state.uf, local: state.searchLocation },
    });
  }
}
