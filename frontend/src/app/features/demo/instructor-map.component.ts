import { HttpErrorResponse } from '@angular/common/http';
import { AfterViewInit, ChangeDetectorRef, Component, ElementRef, OnDestroy, ViewChild, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute,RouterLink } from '@angular/router';

import {
  InstructorSearchProvider,
  SearchFilters,
  SearchInstructor,
} from '../../demo/instructor-search.provider';
import { LeafletMapProvider } from '../../demo/map.provider';

@Component({
  selector: 'app-instructor-map',
  imports: [FormsModule, RouterLink],
  template: `
    <section class="search-experience" [class.results-open]="searched">
      <div class="demo-ribbon">
        <i class="pi pi-sparkles"></i>
        Experiência demonstrativa · profissionais e avaliações sintéticos
      </div>

      <div class="search-hero">
        <p class="eyebrow">Encontre seu instrutor</p>
        <h1>Aprenda no seu ritmo, <span>perto de você.</span></h1>
        <p class="hero-copy">
          Compare áreas de atendimento, veículos e disponibilidade em uma busca simples e segura.
        </p>

        <div class="trust-points" aria-label="Diferenciais da busca">
          <span><i class="pi pi-shield"></i> Verificação interna</span>
          <span><i class="pi pi-map-marker"></i> Área de atendimento</span>
          <span><i class="pi pi-lock"></i> Sem GPS automático</span>
        </div>

        <form class="hero-search" (ngSubmit)="search()">
          <label>
            <span>Onde você procura?</span>
            <div class="location-field">
              <i class="pi pi-map-marker"></i>
              <input
                name="location"
                [(ngModel)]="filters.location"
                placeholder="Cidade, bairro ou CEP"
                autocomplete="postal-code"
                required
              />
            </div>
          </label>
          <button type="submit" [disabled]="loading">
            @if (loading) {
              <i class="pi pi-spin pi-spinner"></i>
            } @else {
              <i class="pi pi-search"></i>
            }
            Buscar instrutores
          </button>
        </form>
        <p class="privacy-note">
          <i class="pi pi-info-circle"></i>
          Você informa a região. Sua localização precisa não é solicitada nem armazenada.
        </p>
      </div>

      <div class="map-workspace" id="resultado-busca">
        <form class="map-toolbar" (ngSubmit)="search()">
          <button class="back-to-intro" type="button" (click)="backToIntro()" aria-label="Voltar">
            <i class="pi pi-arrow-left"></i>
          </button>
          <label class="toolbar-location">
            <i class="pi pi-map-marker"></i>
            <input
              name="toolbarLocation"
              [(ngModel)]="filters.location"
              placeholder="Informe sua cidade"
              required
            />
          </label>
          <button class="toolbar-search" type="submit" [disabled]="loading">
            <i class="pi pi-search"></i><span>Buscar</span>
          </button>
          <button
            class="filter-toggle"
            type="button"
            [class.active]="filtersOpen"
            (click)="filtersOpen = !filtersOpen"
          >
            <i class="pi pi-sliders-h"></i><span>Filtros</span>
          </button>
        </form>

        @if (filtersOpen) {
          <div class="filter-panel">
            <label>
              Categoria
              <select name="category" [(ngModel)]="filters.category">
                <option value="B">Categoria B</option>
              </select>
            </label>
            <label>
              Transmissão
              <select name="transmission" [(ngModel)]="filters.transmission">
                <option value="">Manual ou automático</option>
                <option value="MANUAL">Manual</option>
                <option value="AUTOMATIC">Automático</option>
              </select>
            </label>
            <label>
              Raio de busca
              <select name="radius" [(ngModel)]="filters.radius">
                <option [ngValue]="5">5 km</option>
                <option [ngValue]="10">10 km</option>
                <option [ngValue]="20">20 km</option>
                <option [ngValue]="50">50 km</option>
              </select>
            </label>
            <button type="button" (click)="search()">Aplicar filtros</button>
          </div>
        }

        @if (loading) {
          <div class="map-message"><i class="pi pi-spin pi-spinner"></i> Buscando na região…</div>
        } @else if (error) {
          <div class="map-message error">
            <span>Não foi possível consultar o mapa agora.</span>
            <button type="button" (click)="search()">Tentar novamente</button>
          </div>
        } @else if (searched && !items.length) {
          <div class="map-message empty">
            <span>Nenhum instrutor demonstrativo neste raio.</span>
            <button type="button" (click)="increaseRadius()">Aumentar raio</button>
            <a routerLink="/aluno/demanda">Informar minha necessidade</a>
          </div>
        }

        <div class="mobile-tabs" aria-label="Visualização dos resultados">
          <button [class.active]="view === 'map'" (click)="setView('map')">
            <i class="pi pi-map"></i> Mapa
          </button>
          <button [class.active]="view === 'list'" (click)="setView('list')">
            <i class="pi pi-list"></i> Lista ({{ items.length }})
          </button>
        </div>

        <div class="map-stage" [class.list-view]="view === 'list'">
          <div class="leaflet-map" #map></div>

          <section class="results-drawer" aria-live="polite">
            <header>
              <span class="drawer-handle" aria-hidden="true"></span>
              <div>
                <strong>{{ items.length }} instrutores na região</strong>
                <small>Ordenados por distância · dados sintéticos</small>
              </div>
              <button type="button" (click)="drawerOpen = !drawerOpen" [attr.aria-expanded]="drawerOpen">
                <i class="pi" [class.pi-chevron-up]="!drawerOpen" [class.pi-chevron-down]="drawerOpen"></i>
              </button>
            </header>

            @if (drawerOpen || view === 'list') {
              <div class="result-cards">
                @for (instructor of items; track instructor.id) {
                  <article
                    tabindex="0"
                    [class.selected]="selected?.id === instructor.id"
                    (click)="select(instructor)"
                    (keydown.enter)="select(instructor)"
                  >
                    <div class="result-avatar" aria-hidden="true">
                      @if(instructor.profile_photo_url){<img [src]="instructor.profile_photo_url" alt="">}@else { {{ initials(instructor.display_name) }} }
                    </div>
                    <div class="result-copy">
                      <strong>{{ instructor.display_name }}</strong>
                      @if(instructor.verified_claims.includes('CREDENTIAL_VERIFIED')){<em class="verified"><i class="pi pi-verified"></i> Credenciamento verificado</em>}
                      <span>
                        <i class="pi pi-star-fill"></i> {{ instructor.demo_rating }}
                        <b>·</b> {{ instructor.distance_km }} km
                      </span>
                      <small>
                        Categoria {{ instructor.categories.join(', ') }} ·
                        {{ instructor.transmission === 'MANUAL' ? 'Manual' : 'Automático' }}
                      </small>
                    </div>
                    <div class="result-action">
                      <strong>R$ {{ instructor.demo_price }}</strong>
                      <small>por aula</small>
                      <a
                        [routerLink]="['/aluno/instrutores', 'marina-demo']"
                        (click)="$event.stopPropagation()"
                      >Ver perfil</a>
                    </div>
                  </article>
                }
              </div>
            }
          </section>
        </div>

        <p class="map-credit">
          © OpenStreetMap · coordenadas representam regiões sintéticas de atendimento.
        </p>
      </div>
    </section>
  `,
  styleUrl: './instructor-map.component.scss',
})
export class InstructorMapComponent implements AfterViewInit, OnDestroy {
  @ViewChild('map') mapElement!: ElementRef<HTMLElement>;

  private readonly api = inject(InstructorSearchProvider);
  private readonly map = inject(LeafletMapProvider);
  private readonly route = inject(ActivatedRoute);
  private readonly changeDetector = inject(ChangeDetectorRef);

  filters: SearchFilters = {
    location: 'Porto Alegre',
    radius: 10,
    category: 'B',
    transmission: '',
    vehicleAvailable: true,
  };
  items: SearchInstructor[] = [];
  selected: SearchInstructor | null = null;
  loading = false;
  searched = false;
  error = false;
  filtersOpen = false;
  drawerOpen = true;
  view: 'map' | 'list' = 'map';

  ngAfterViewInit() {
    this.map.mount(this.mapElement.nativeElement, (id) => {
      const item = this.items.find((candidate) => candidate.id === id);
      if (item) this.select(item);
    });
    const routedLocation = this.route.snapshot.queryParamMap.get('local');
    if (routedLocation) {
      this.filters.location = routedLocation;
      this.search();
    }
  }

  search() {
    if (!this.filters.location.trim()) return;
    this.searched = true;
    this.loading = true;
    this.error = false;
    this.filtersOpen = false;
    this.scrollToResults();

    this.api.geocode(this.filters.location).subscribe({
      next: (geocoding) => {
        const point = geocoding.results[0];
        this.api.search(point.latitude, point.longitude, this.filters).subscribe({
          next: (response) => {
            this.items = response.results;
            this.selected = null;
            this.loading = false;
            this.drawerOpen = true;
            this.map.render(this.items, null);
            this.changeDetector.detectChanges();
          },
          error: () => this.fail(),
        });
      },
      error: (response: HttpErrorResponse) => {
        this.items = [];
        this.loading = false;
        this.error = response.status !== 404;
        this.map.render([], null);
        this.changeDetector.detectChanges();
      },
    });
  }

  select(item: SearchInstructor) {
    this.selected = item;
    this.map.select(item.id);
  }

  setView(view: 'map' | 'list') {
    this.view = view;
    this.drawerOpen = view === 'list';
    if (view === 'map') this.map.refresh();
  }

  increaseRadius() {
    this.filters.radius = this.filters.radius === 50 ? 50 : Math.min(50, this.filters.radius * 2);
    this.search();
  }

  backToIntro() {
    this.searched = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  initials(name: string) {
    return name
      .split(' ')
      .slice(0, 2)
      .map((part) => part[0])
      .join('');
  }

  private scrollToResults() {
    setTimeout(() => document.getElementById('resultado-busca')?.scrollIntoView({ behavior: 'smooth' }));
  }

  private fail() {
    this.loading = false;
    this.error = true;
    this.items = [];
    this.map.render([], null);
    this.changeDetector.detectChanges();
  }

  ngOnDestroy() {
    this.map.destroy();
  }
}
