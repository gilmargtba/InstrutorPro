import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({selector:'app-root',imports:[RouterLink,RouterLinkActive,RouterOutlet],template:`
<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
<header class="topbar"><a routerLink="/" class="brand" aria-label="InstrutorProCNH — início"><img src="/logo-cnh.svg" alt="InstrutorProCNH — encontre instrutores para sua jornada CNH"></a><nav aria-label="Navegação principal"><a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">Início</a><a routerLink="/aluno/instrutores" routerLinkActive="active">Encontrar instrutor</a><a routerLink="/profissional/instrutor/entrada" routerLinkActive="active">Sou instrutor</a><a routerLink="/entrar" routerLinkActive="active">Entrar</a><a routerLink="/cadastro/aluno" routerLinkActive="active">Criar conta</a></nav></header>
<main id="conteudo"><router-outlet /></main><footer><strong>InstrutorProCNH</strong><span>A conexão que te move.</span><small>Consulte profissionais verificados e áreas públicas de atendimento.</small></footer>`,styleUrl:'./app.component.scss'})
export class AppComponent {}
