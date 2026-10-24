import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Meta, Title } from '@angular/platform-browser';
import { publicMediaUrl } from '../../core/api-url';
import { WhatsappLinkService } from '../../core/whatsapp-link.service';

interface LessonOption { category: string; price_amount: number; duration_minutes: number; }
interface LessonPackage { id: string; name: string; category: string; categories: string[]; lesson_count: number; price_amount: number; price_per_lesson: number; vehicle_included: boolean; description: string; }
interface PublicProfile {
  id: string; display_name: string; bio: string; categories: string[]; transmission_options: string[];
  vehicle_available: boolean; availability_summary: string; profile_photo_url: string | null;
  verified_claims: string[]; service_area: { city: string; uf: string; radius_km: number }; synthetic: boolean;
  price_amount: number; offer_category: string; price_from: boolean; duration_minutes: number;
  vehicle: { make: string; model: string; year: number; transmission: string } | null;
  lesson_options: LessonOption[];
  lesson_packages?: LessonPackage[];
}

@Component({
  selector: 'app-public-instructor-profile',
  imports: [RouterLink],
  template: `
    <section class="page narrow">
      @if (loading) { <p>Carregando perfil…</p> }
      @else if (error) { <h1>Perfil indisponível</h1><a routerLink="/aluno/instrutores">Voltar à busca</a> }
      @else if (profile) {
        @if (profile.synthetic) { <div class="demo-flag">DEV/TEST · perfil sintético</div> }
        <a class="back" routerLink="/aluno/instrutores/mapa">← Voltar ao mapa</a>
        <div class="profile">
          <div class="avatar large">
            @if (profile.profile_photo_url) { <img [src]="photoUrl(profile.profile_photo_url)" alt="Foto aprovada de {{profile.display_name}}"> }
            @else { <i class="pi pi-user"></i> }
          </div>
          <div><p class="eyebrow">Instrutor disponível</p><h1>{{profile.display_name}}</h1>
            <p>Atende em {{profile.service_area.city}}/{{profile.service_area.uf}} · até {{profile.service_area.radius_km}} km</p>
            @if (profile.verified_claims.includes('CREDENTIAL_VERIFIED')) { <p>✓ Credenciamento verificado</p> }
          </div>
        </div>
        <article>
          <h2>Sobre</h2><p>{{profile.bio || 'O profissional ainda não adicionou uma apresentação pública.'}}</p>
          <h2>Informações das aulas</h2>
          <p>Categoria {{profile.categories.join(', ')}} · {{profile.transmission_options.join(' / ')}}</p>
          @if (profile.vehicle) { <p>Veículo informado: {{profile.vehicle.make}} {{profile.vehicle.model}} {{profile.vehicle.year}} · {{profile.vehicle.transmission}}</p> }
          <p>{{profile.availability_summary}}</p>
          <h2>Planos e valores</h2>
          <p class="muted">Valores informados pelo instrutor por aula. Combine detalhes, contratação e pagamento diretamente com ele.</p>
          <div class="lesson-options">
            @for (option of profile.lesson_options; track option.category) {
              <section class="lesson-option" [class.selected]="option.category === profile.offer_category">
                <p class="eyebrow">Categoria {{option.category}}</p><h3>Aula de direção</h3>
                <p class="option-price">{{formatPrice(option.price_amount)}} <small>por aula</small></p>
                <p>{{option.duration_minutes}} minutos por aula</p>
                <button class="button primary" type="button" (click)="contact(option.category)">
                  <i class="pi pi-whatsapp"></i> Consultar pelo WhatsApp
                </button>
              </section>
            }
          </div>
          @if (profile.lesson_packages?.length) {
            <h2>Pacotes de aulas</h2>
            <p class="muted">Preço total informado pelo instrutor. Aulas, contratação e pagamento são combinados diretamente; o pacote não comprova aulas realizadas.</p>
            <div class="lesson-options">
              @for (packageItem of profile.lesson_packages; track packageItem.id) {
                <section class="lesson-option">
                  <p class="eyebrow">Categorias {{packageItem.categories.join(', ')}}</p><h3>{{packageItem.name}}</h3>
                  <p>{{packageItem.lesson_count}} aulas · {{packageItem.vehicle_included?'Com veículo':'Sem veículo'}}</p>
                  <p class="option-price">{{formatPrice(packageItem.price_amount)}} <small>no total</small></p>
                  <p>{{formatPrice(packageItem.price_per_lesson)}} por aula</p>
                  @if(packageItem.description){<p>{{packageItem.description}}</p>}
                  @for(category of packageItem.categories; track category){<button class="button primary" type="button" (click)="contact(category, 'public-package')"><i class="pi pi-whatsapp"></i> Consultar pacote {{category}} pelo WhatsApp</button>}
                </section>
              }
            </div>
          }
          @if (contactError) { <p role="alert">{{contactError}}</p> }
          <h2>Verificações aprovadas</h2>
          @if (!profile.verified_claims.length) { <p>Nenhuma verificação pública disponível.</p> }
          @for (claim of profile.verified_claims; track claim) { <p>✓ {{claimLabel(claim)}}</p> }
          <p class="muted">Documentos, telefone bruto, endereço residencial e placa nunca são exibidos.</p>
        </article>
      }
    </section>
  `,
  styles: [`
    .lesson-options { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin: 1rem 0 2rem; }
    .lesson-option { border: 1px solid #cbdedc; border-radius: 1rem; padding: 1.25rem; background: #fff; }
    .lesson-option.selected { border-color: #008486; box-shadow: 0 0 0 2px #d8f1ef; }
    .lesson-option h3 { margin: .25rem 0 1rem; }
    .option-price { font-size: 1.65rem; font-weight: 800; color: #123f5f; margin-bottom: .5rem; }
    .option-price small { font-size: .9rem; font-weight: 400; }
    .lesson-option .button { margin-top: .75rem; }
  `],
})
export class PublicInstructorProfileComponent {
  private readonly http = inject(HttpClient);
  private readonly changeDetector = inject(ChangeDetectorRef);
  private readonly title = inject(Title);
  private readonly meta = inject(Meta);
  private readonly whatsapp = inject(WhatsappLinkService);
  private readonly route = inject(ActivatedRoute);
  private readonly id = this.route.snapshot.paramMap.get('id');
  profile?: PublicProfile;
  loading = true;
  error = false;
  contactError = '';

  constructor() {
    const category = this.route.snapshot.queryParamMap.get('categoria');
    const options = category && ['A', 'B', 'C', 'D', 'E'].includes(category) ? { params: { category } } : {};
    this.http.get<PublicProfile>(`/instructors/${this.id}/`, options).subscribe({
      next: profile => {
        this.profile = profile;
        this.loading = false;
        this.title.setTitle(`Instrutor de direção em ${profile.service_area.city} - ${profile.display_name} | InstrutorProCNH`);
        this.meta.updateTag({ name: 'description', content: `Conheça ${profile.display_name}, instrutor de direção em ${profile.service_area.city}. Consulte categorias, veículo, preço e área de atendimento.` });
        this.changeDetector.detectChanges();
      },
      error: () => { this.error = true; this.loading = false; this.changeDetector.detectChanges(); },
    });
  }

  contact(category: string, source = 'public-profile') {
    if (!this.profile) return;
    this.contactError = '';
    this.http.post<{ destination_url: string }>(`/instructors/${this.id}/whatsapp-contact/`, { category, source }).subscribe({
      next: result => { void this.whatsapp.open(result.destination_url).catch(() => { this.contactError = 'Não foi possível abrir o WhatsApp agora.'; this.changeDetector.detectChanges(); }); },
      error: () => { this.contactError = 'Não foi possível abrir o WhatsApp agora.'; this.changeDetector.detectChanges(); },
    });
  }

  formatPrice(value: number): string { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value); }
  photoUrl(path: string): string { return publicMediaUrl(path) ?? ''; }
  claimLabel(claim: string) { return ({ CREDENTIAL_VERIFIED: 'Credenciamento verificado', COURSE_VERIFIED: 'Curso de instrutor verificado', VEHICLE_VERIFIED: 'Veículo/documentação verificada' } as Record<string, string>)[claim] || claim; }
}
