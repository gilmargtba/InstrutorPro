import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({selector:'app-root',imports:[RouterLink,RouterLinkActive,RouterOutlet],template:`
<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
<header class="topbar"><a routerLink="/" class="brand" aria-label="InstrutorProcnh — início"><img src="/logo-cnh.svg" alt="InstrutorProcnh — conectando instrutores ao seu sucesso CNH"></a><nav aria-label="Navegação principal"><a routerLink="/aluno/instrutores" routerLinkActive="active">Encontrar instrutor</a><a routerLink="/entrar" routerLinkActive="active">Entrar</a><a routerLink="/aluno" routerLinkActive="active">Criar conta</a><a routerLink="/aluno" routerLinkActive="active">Sou aluno</a><a routerLink="/profissional" routerLinkActive="active">Sou profissional</a></nav></header>
<main id="conteudo"><router-outlet /></main><footer><strong>InstrutorProcnh</strong><span>A conexão que te move.</span><small>Experiência demonstrativa · dados 100% sintéticos</small></footer>`,styleUrl:'./app.component.scss'})
export class AppComponent {}
