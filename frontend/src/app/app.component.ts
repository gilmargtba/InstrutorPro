import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({selector:'app-root',imports:[RouterLink,RouterLinkActive,RouterOutlet],template:`
<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
<header class="topbar"><a routerLink="/" class="brand" aria-label="InstrutorPro — início"><img src="/logo.jpg" alt="InstrutorPro — conectando instrutores ao seu sucesso CNH"></a><nav aria-label="Navegação principal"><a routerLink="/aluno/jornada" routerLinkActive="active">Aluno</a><a routerLink="/profissional" routerLinkActive="active">Profissional</a></nav></header>
<main id="conteudo"><router-outlet /></main><footer><strong>InstrutorPro</strong><span>A conexão que te move.</span><small>Experiência demonstrativa · dados 100% sintéticos</small></footer>`,styleUrl:'./app.component.scss'})
export class AppComponent {}
