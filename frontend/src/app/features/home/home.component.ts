import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [RouterLink, FormsModule],
  styleUrl: './home.component.scss',
  template: `
    <section class="home-hero" aria-labelledby="home-title">
      <div class="home-hero-inner">
        <p class="section-label">Sua jornada começa aqui</p>
        <h1 id="home-title">Encontre o <span>instrutor certo</span> perto de você.</h1>
        <p class="hero-lead">Busque por cidade, conheça profissionais verificados pela plataforma e converse diretamente para combinar suas aulas de direção.</p>
        <form class="hero-search" (ngSubmit)="search()">
          <label for="home-place">Em qual cidade você procura?</label>
          <div class="search-control">
            <i class="pi pi-map-marker" aria-hidden="true"></i>
            <input id="home-place" name="place" [(ngModel)]="place" autocomplete="address-level2" placeholder="Digite cidade, bairro ou CEP" required>
            <button type="submit" aria-label="Buscar instrutores"><span>Buscar instrutores</span><i class="pi pi-arrow-right" aria-hidden="true"></i></button>
          </div>
        </form>
        <div class="hero-links">
          <button type="button" class="location-link" (click)="useLocation()"><i class="pi pi-crosshairs" aria-hidden="true"></i> Usar minha localização</button>
          <a routerLink="/aluno/instrutores">Ver cidades com instrutores <i class="pi pi-arrow-right" aria-hidden="true"></i></a>
        </div>
        @if (locationError) { <p class="location-error" role="alert">{{ locationError }}</p> }
      </div>
      <div class="hero-stage" aria-hidden="true">
        <div class="stage-road road-one"></div><div class="stage-road road-two"></div>
        <div class="stage-pin pin-one"><i class="pi pi-map-marker"></i></div><div class="stage-pin pin-two"><i class="pi pi-map-marker"></i></div>
        <div class="stage-card"><span class="stage-icon"><i class="pi pi-car"></i></span><span><small>Próxima parada</small><strong>Aprender a dirigir</strong></span><i class="pi pi-arrow-up-right"></i></div>
        <div class="stage-badge"><i class="pi pi-check-circle"></i> Perfis analisados antes da publicação</div>
      </div>
    </section>

    <section class="home-path home-section" id="como-funciona" aria-labelledby="path-title">
      <div class="section-intro"><p class="section-label">01 / Como funciona</p><h2 id="path-title">Da busca à primeira aula, sem complicação.</h2><p>Você escolhe com quem conversar. A plataforma mostra os perfis e facilita o contato.</p></div>
      <div class="path-grid">
        <article><span class="step-index">01</span><span class="step-icon"><i class="pi pi-search"></i></span><h3>Encontre</h3><p>Informe a cidade e explore os instrutores que atendem sua região.</p></article>
        <article><span class="step-index">02</span><span class="step-icon"><i class="pi pi-id-card"></i></span><h3>Compare</h3><p>Veja categorias, veículo, preço informado e área pública de atendimento.</p></article>
        <article><span class="step-index">03</span><span class="step-icon"><i class="pi pi-comments"></i></span><h3>Converse</h3><p>Abra o contato profissional e combine os detalhes diretamente com o instrutor.</p></article>
      </div>
      <a class="home-cta dark" routerLink="/aluno/instrutores">Explorar instrutores <i class="pi pi-arrow-right" aria-hidden="true"></i></a>
    </section>

    <section class="home-feature home-section" aria-labelledby="feature-title">
      <div class="feature-visual" aria-hidden="true"><div class="feature-circle"></div><div class="feature-phone"><div class="phone-top"></div><div class="phone-map"><span class="map-line one"></span><span class="map-line two"></span><span class="map-point a">A</span><span class="map-point b">B</span><span class="map-point c">C</span></div><div class="phone-result"><span class="result-avatar"><i class="pi pi-user"></i></span><span><b>Instrutores na região</b><small>Escolha e veja o perfil</small></span></div></div><span class="feature-spark spark-a">✦</span><span class="feature-spark spark-b">✦</span></div>
      <div class="feature-copy"><p class="section-label">Busca por cidade</p><h2 id="feature-title">A sua região no centro da busca.</h2><p>Escolha uma UF e uma cidade com instrutores disponíveis. No mapa, você vê áreas aproximadas de atendimento e pode abrir cada perfil para conhecer a oferta e o contato.</p><ul><li><i class="pi pi-check-circle" aria-hidden="true"></i> Lista de cidades com perfis publicados</li><li><i class="pi pi-check-circle" aria-hidden="true"></i> Mapa com pontos públicos aproximados</li><li><i class="pi pi-check-circle" aria-hidden="true"></i> Contato direto no perfil do instrutor</li></ul><a class="home-cta yellow" routerLink="/aluno/instrutores">Buscar na minha cidade <i class="pi pi-arrow-right" aria-hidden="true"></i></a></div>
    </section>

    <section class="trust-section home-section" aria-labelledby="trust-title"><div class="section-intro"><p class="section-label">02 / Segurança e transparência</p><h2 id="trust-title">Saiba o que foi conferido.</h2><p>Os documentos do instrutor passam por análise humana antes da decisão de publicar o perfil.</p></div><div class="trust-grid"><article><i class="pi pi-file-check" aria-hidden="true"></i><h3>Documentos privados</h3><p>CNH e comprovante profissional ficam em área restrita para análise da equipe.</p></article><article><i class="pi pi-user-edit" aria-hidden="true"></i><h3>Revisão humana</h3><p>Uma pessoa confere a documentação e decide sobre a verificação interna.</p></article><article><i class="pi pi-map-marker" aria-hidden="true"></i><h3>Localização aproximada</h3><p>O mapa mostra a área pública de atendimento, sem revelar endereço residencial.</p></article></div><p class="trust-note">A verificação da plataforma não substitui a consulta aos órgãos oficiais de trânsito.</p></section>

    <section class="instructor-band home-section" aria-labelledby="instructor-title"><div><p class="section-label">Para instrutores</p><h2 id="instructor-title">Seus próximos alunos podem encontrar você aqui.</h2><p>Crie seu perfil, informe as categorias que atende e envie os documentos para análise. Após a aprovação e publicação, os alunos poderão conhecer sua oferta e entrar em contato.</p><a class="home-cta yellow" routerLink="/cadastro/instrutor">Criar perfil de instrutor <i class="pi pi-arrow-right" aria-hidden="true"></i></a></div><div class="instructor-decoration" aria-hidden="true"><i class="pi pi-directions"></i><span>Seu caminho<br>começa aqui.</span></div></section>

    <section class="faq-section home-section" aria-labelledby="faq-title"><div class="section-intro"><p class="section-label">Dúvidas frequentes</p><h2 id="faq-title">Antes de começar</h2></div><div class="faq-list"><details><summary>Como encontro um instrutor na minha cidade?</summary><p>Use a busca por cidade ou abra a lista de UFs. Ao selecionar uma cidade com perfis publicados, o mapa mostra as áreas de atendimento.</p></details><details><summary>Como entro em contato com o instrutor?</summary><p>Abra o perfil desejado e use o contato profissional disponibilizado por ele. Você decide se quer iniciar a conversa.</p></details><details><summary>O mapa mostra o endereço residencial?</summary><p>Não. Os pontos exibidos representam áreas públicas aproximadas de atendimento informadas pelo instrutor.</p></details><details><summary>O cadastro do instrutor aparece imediatamente?</summary><p>Não. A equipe analisa os documentos e a verificação profissional antes de decidir sobre a publicação do perfil.</p></details></div></section>
  `,
})
export class HomeComponent {
  place = '';
  locationError = '';

  constructor(private readonly router: Router) {}

  search(): void {
    const value = this.place.trim();
    if (value) void this.router.navigate(['/aluno/instrutores/mapa'], { queryParams: { local: value } });
  }

  useLocation(): void {
    this.locationError = '';
    if (!navigator.geolocation) {
      this.locationError = 'Seu navegador não oferece geolocalização.';
      return;
    }
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => void this.router.navigate(['/aluno/instrutores/mapa'], { queryParams: { latitude: coords.latitude, longitude: coords.longitude, source: 'user' } }),
      () => this.locationError = 'Não foi possível acessar sua localização. Pesquise por cidade, bairro ou CEP.',
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  }
}
