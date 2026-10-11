import { HttpErrorResponse } from '@angular/common/http';
import { AfterViewInit, ChangeDetectorRef, Component, ElementRef, OnDestroy, ViewChild, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, switchMap } from 'rxjs';

import {
  InstructorSearchProvider,
  SearchFilters,
  SearchInstructor,
  GeocodingResult,
} from '../../demo/instructor-search.provider';
import { LeafletMapProvider } from '../../demo/map.provider';
import { BRAZIL_UFS } from '../../shared/brazil-ufs';
import { environment } from '../../../environments/environment';
import { publicMediaUrl } from '../../core/api-url';
import { StudentLocationService } from '../../core/student-location.service';
import { WhatsappLinkService } from '../../core/whatsapp-link.service';

@Component({
  selector: 'app-instructor-map',
  imports: [FormsModule, RouterLink],
  template: `
    <section class="search-experience" [class.results-open]="searched">
      @if (!production) {<div class="demo-ribbon">
        <i class="pi pi-sparkles"></i>
        Experiência demonstrativa · profissionais e ofertas sintéticos
      </div>}

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
                (input)="suggest(filters.location)"
              />
            </div>
            @if (suggestions.length) {<div class="suggestions" role="listbox">@for (place of suggestions; track place.id) {<button type="button" (click)="choose(place)">{{place.label}}</button>}</div>}
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
        <button class="use-location" type="button" (click)="useMyLocation()"><i class="pi pi-crosshairs"></i> Usar minha localização</button>
        @if(locationMessage){<p class="location-message" role="status">{{locationMessage}}</p>}
        @if(pendingLocation){<label>Confirme a UF desta localidade
          <select name="confirmedUf" [(ngModel)]="confirmedUf"><option value="">Selecione a UF</option>@for(uf of brazilUfs;track uf){<option [value]="uf">{{uf}}</option>}</select>
        </label><button type="button" [disabled]="!confirmedUf" (click)="confirmLocationUf()">Confirmar UF</button>}
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
                <option value="">Todas as categorias</option>
                <option value="A">Categoria A</option>
                <option value="B">Categoria B</option>
                <option value="C">Categoria C</option>
                <option value="D">Categoria D</option>
                <option value="E">Categoria E</option>
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
              Veículo do instrutor
              <select name="vehicleAvailable" [(ngModel)]="filters.vehicleAvailable">
                <option [ngValue]="null">Qualquer opção</option>
                <option [ngValue]="true">Disponível</option>
                <option [ngValue]="false">Não disponível</option>
              </select>
            </label>
            <label>
              Raio de busca
              <input name="radius" type="number" min="1" max="5000" step="1"
                [disabled]="filters.radius === null" [(ngModel)]="filters.radius" />
            </label>
            <label class="check"><input name="anyDistance" type="checkbox"
              [ngModel]="anyDistance" (ngModelChange)="setAnyDistance($event)" />
              Qualquer distância (Brasil)</label>
            <label>
              Preço máximo
              <select name="maxPrice" [(ngModel)]="filters.maxPrice">
                <option [ngValue]="null">Qualquer preço</option>
                <option [ngValue]="80">Até R$ 80</option>
                <option [ngValue]="100">Até R$ 100</option>
                <option [ngValue]="150">Até R$ 150</option>
              </select>
            </label>
            <label>
              Ordenar
              <select name="ordering" [(ngModel)]="filters.ordering">
                <option value="distance">Mais próximos</option>
                <option value="price">Menor preço</option>
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
            <span>Nenhum instrutor encontrado com os filtros atuais.</span>
            @if (filters.category) {<button type="button" (click)="showAllCategories()">Ver todas as categorias</button>}
            @if (!anyDistance) {<button type="button" (click)="increaseRadius()">Aumentar raio</button>}
            <button type="button" (click)="filtersOpen=true">Alterar filtros</button>
            <button type="button" (click)="backToIntro()">Buscar outra região</button>
            @if (!mobile) {<a routerLink="/aluno/demanda">Informar minha necessidade</a>}
          </div>
        }
        @if(contactError){<p class="contact-error" role="alert">{{contactError}}</p>}

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
                <small>{{filters.ordering==='price'?'Ordenados por menor preço':'Ordenados por distância'}}</small>
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
                      @if(instructor.profile_photo_url){<img [src]="photoUrl(instructor.profile_photo_url)" alt="">}@else { {{ initials(instructor.display_name) }} }
                    </div>
                    <div class="result-copy">
                      <strong>{{ instructor.display_name }}</strong>
                      @if(instructor.verified_claims.includes('CREDENTIAL_VERIFIED')){<em class="verified"><i class="pi pi-verified"></i> Credenciamento verificado</em>}
                      <span>{{ instructor.distance_km }} km de você</span>
                      <small>
                        Categoria {{ instructor.categories.join(', ') }} ·
                        {{ instructor.transmission === 'MANUAL' ? 'Manual' : 'Automático' }}
                      </small>
                      @if(instructor.vehicle){<small>{{instructor.vehicle.make}} {{instructor.vehicle.model}} {{instructor.vehicle.year}}</small>}
                    </div>
                    <div class="result-action">
                      @if(instructor.price_from){<small>A partir de</small>}
                      <strong>R$ {{ instructor.price_amount }}</strong>
                      <small>{{instructor.duration_minutes}} min por aula</small>
                      <a
                        [routerLink]="['/aluno/instrutores', instructor.id]"
                        [queryParams]="{categoria: instructor.offer_category}"
                        (click)="$event.stopPropagation()"
                      >Ver perfil</a>
                      <button type="button" class="whatsapp" (click)="$event.stopPropagation(); contact(instructor)"><i class="pi pi-whatsapp"></i> Chamar no WhatsApp</button>
                    </div>
                  </article>
                }
              </div>
            }
          </section>
        </div>

        <p class="map-credit">
          © OpenStreetMap · coordenadas representam áreas aproximadas de atendimento.
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
  private readonly router = inject(Router);
  private readonly changeDetector = inject(ChangeDetectorRef);
  private readonly location = inject(StudentLocationService);
  private readonly whatsapp = inject(WhatsappLinkService);
  readonly production = environment.production;
  readonly mobile = environment.mobile;

  filters: SearchFilters = {
    location: '',
    radius: null,
    category: '',
    transmission: '',
    vehicleAvailable: null,
    maxPrice: null,
    ordering: 'distance',
  };
  items: SearchInstructor[] = [];
  selected: SearchInstructor | null = null;
  loading = false;
  searched = false;
  error = false;
  filtersOpen = false;
  drawerOpen = true;
  anyDistance = true;
  view: 'map' | 'list' = 'map';
  suggestions: GeocodingResult[] = [];
  locationMessage = '';
  readonly brazilUfs = BRAZIL_UFS;
  pendingLocation: GeocodingResult | null = null;
  confirmedUf = '';
  contactError = '';
  private readonly locationQueries = new Subject<string>();

  constructor() {
    this.locationQueries.pipe(
      debounceTime(350), distinctUntilChanged(), switchMap(query => this.api.geocode(query, 5))
    ).subscribe({next: response => this.suggestions=response.results, error:()=>this.suggestions=[]});
  }

  ngAfterViewInit() {
    this.map.mount(this.mapElement.nativeElement, (id) => {
      const item = this.items.find((candidate) => candidate.id === id);
      if (item) this.select(item);
    });
    const routedCategory = this.route.snapshot.queryParamMap.get('categoria');
    if (routedCategory && ['A', 'B', 'C', 'D', 'E'].includes(routedCategory)) {
      this.filters.category = routedCategory;
    }
    const routedRadius = this.route.snapshot.queryParamMap.get('raio');
    if (routedRadius === 'todos') {
      this.setAnyDistance(true);
    } else if (routedRadius !== null) {
      const radius = Number(routedRadius);
      if (Number.isInteger(radius) && radius >= 1 && radius <= 5000) {
        this.filters.radius = radius;
        this.anyDistance = false;
      }
    }
    const routedLocation = this.route.snapshot.queryParamMap.get('local');
    if (routedLocation) {
      this.filters.location = routedLocation;
      this.search();
    } else if (this.mobile) {
      const position = this.location.takePending();
      if (position) this.searchFromCoordinates(position.latitude, position.longitude);
    }
  }

  search() {
    if (!this.filters.location.trim()) return;
    if (!this.anyDistance && (this.filters.radius === null || !Number.isInteger(this.filters.radius) || this.filters.radius < 1 || this.filters.radius > 5000)) {
      this.locationMessage = 'Informe um raio inteiro entre 1 e 5000 km ou selecione qualquer distância.';
      return;
    }
    this.searched = true;
    this.loading = true;
    this.error = false;
    this.filtersOpen = false;
    this.pendingLocation = null;
    this.confirmedUf = '';
    this.locationMessage = '';
    this.scrollToResults();

    this.api.geocode(this.filters.location).subscribe({
      next: (geocoding) => {
        const point = geocoding.results[0];
        if (!point) { this.fail(); return; }
        this.acceptPoint(point);
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

  private acceptPoint(point:GeocodingResult) {
    if (!point.uf) {
      this.pendingLocation = point;
      this.loading = false;
      this.locationMessage = 'A UF não foi determinada. Selecione e confirme a UF antes de continuar.';
      this.backToIntro();
      this.changeDetector.detectChanges();
      return;
    }
    this.searchFromPoint(point);
  }

  confirmLocationUf() {
    if (!this.pendingLocation || !this.brazilUfs.includes(this.confirmedUf as typeof BRAZIL_UFS[number])) return;
    const point = {...this.pendingLocation, uf:this.confirmedUf};
    this.pendingLocation = null;
    this.locationMessage = `UF ${this.confirmedUf} confirmada por você para esta busca.`;
    this.loading = true;
    this.searched = true;
    this.scrollToResults();
    this.searchFromPoint(point);
  }

  private searchFromPoint(point:GeocodingResult) {
        this.map.focus(point.latitude, point.longitude, 12);
        this.suggestions = [];
        void this.router.navigate([], {queryParams:{local:point.label,uf:point.uf,categoria:this.filters.category || null,raio:this.filters.radius ?? 'todos'},replaceUrl:true});
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
  }

  suggest(query:string) { if(query.trim().length >= 3) this.locationQueries.next(query.trim()); else this.suggestions=[]; }
  choose(place:GeocodingResult) {
    this.filters.location=place.label;
    this.suggestions=[];
    this.searched=true;
    this.loading=true;
    this.error=false;
    this.scrollToResults();
    this.acceptPoint(place);
  }
  useMyLocation() {
    this.locationMessage='Localizando…';
    void this.location.currentPosition().then(position => {
      this.searchFromCoordinates(position.latitude, position.longitude);
    }).catch(() => {
      this.locationMessage='Localização não autorizada. Você pode continuar pela busca manual.';
      this.changeDetector.detectChanges();
    });
  }

  private searchFromCoordinates(latitude:number, longitude:number) {
    this.locationMessage='Buscando instrutores próximos à localização autorizada.';
    this.searched=true;this.loading=true;this.error=false;this.scrollToResults();
    this.map.focus(latitude,longitude,12);
    this.api.search(latitude,longitude,this.filters).subscribe({
      next:response=>{this.items=response.results;this.loading=false;this.map.render(this.items,null);this.changeDetector.detectChanges()},
      error:()=>this.fail(),
    });
  }

  select(item: SearchInstructor) {
    this.selected = item;
    this.map.select(item.id);
  }

  contact(item: SearchInstructor) {
    this.contactError='';
    this.api.whatsapp(item.id,item.offer_category,'search-card').subscribe({
      next: response => { void this.whatsapp.open(response.destination_url).catch(() => {
        this.contactError='Não foi possível abrir o WhatsApp agora.';this.changeDetector.detectChanges();
      }); },
      error: () => {this.contactError='Não foi possível abrir o WhatsApp agora.';this.changeDetector.detectChanges();},
    });
  }

  showAllCategories() {
    this.filters.category = '';
    this.search();
  }

  setView(view: 'map' | 'list') {
    this.view = view;
    this.drawerOpen = view === 'list';
    if (view === 'map') this.map.refresh();
  }

  increaseRadius() {
    if (this.filters.radius === null || this.filters.radius >= 5000) {
      this.setAnyDistance(true);
    } else {
      this.filters.radius = Math.min(5000, this.filters.radius * 2);
    }
    this.search();
  }

  setAnyDistance(enabled: boolean) {
    this.anyDistance = enabled;
    this.filters.radius = enabled ? null : 10;
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

  photoUrl(path:string):string { return publicMediaUrl(path) ?? ''; }

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
