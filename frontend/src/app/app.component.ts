import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { environment } from '../environments/environment';

@Component({selector:'app-root',imports:[RouterLink,RouterLinkActive,RouterOutlet],template:`
<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
@if(mobile){<header class="mobile-topbar"><a routerLink="/" aria-label="InstrutorProCNH — início"><img src="/logo-cnh.svg" alt="InstrutorProCNH"></a></header>}@else{<header class="topbar"><a routerLink="/" class="brand" aria-label="InstrutorProCNH — início"><img src="/logo-cnh.svg" alt="InstrutorProCNH — encontre instrutores para sua jornada CNH"></a><nav aria-label="Navegação principal"><a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">Início</a><a routerLink="/aluno/instrutores" routerLinkActive="active">Encontrar instrutor</a><a [routerLink]="instructorSignupPath" routerLinkActive="active">Sou instrutor</a><a routerLink="/entrar" routerLinkActive="active">Entrar</a>@if(studentRegistrationVisible){<a routerLink="/cadastro/aluno" routerLinkActive="active">Criar conta</a>}</nav></header>}
<main id="conteudo"><router-outlet /></main>@if(mobile){<nav class="mobile-bottom-nav" aria-label="Navegação do aluno"><a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}"><i class="pi pi-home"></i> Início</a><a routerLink="/aluno/instrutores/mapa" routerLinkActive="active"><i class="pi pi-search"></i> Buscar</a><a routerLink="/privacidade" routerLinkActive="active"><i class="pi pi-lock"></i> Privacidade</a></nav>}@else{<footer><strong>InstrutorProCNH</strong><span>A conexão que te move.</span><small>Consulte profissionais verificados e áreas públicas de atendimento.</small><a routerLink="/privacidade">Política de Privacidade</a></footer>}`,styleUrl:'./app.component.scss'})
export class AppComponent {
  readonly mobile = environment.mobile;
  readonly instructorSignupPath = environment.production
    ? '/cadastro/instrutor'
    : '/profissional/instrutor/entrada';
  readonly studentRegistrationVisible = !environment.production;
}
