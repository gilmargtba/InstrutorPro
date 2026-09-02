import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-student-entry', imports: [RouterLink],
  template: `<section class="page narrow"><div class="demo-flag">DEMO · dados sintéticos</div><header class="page-head"><div><p class="eyebrow">Aluno</p><h1>Comece sua jornada</h1><p>Encontre instrutores ou crie uma conta demonstrativa persistente.</p></div></header><div class="entry"><a class="button primary" routerLink="/aluno/instrutores">Encontrar instrutor</a><a class="button secondary" routerLink="/cadastro/aluno">Criar minha conta</a><a class="button ghost" routerLink="/entrar">Já tenho conta — Entrar</a></div></section>`,
  styles: [`.entry{display:grid;gap:1rem;padding:2rem;border:1px solid #d6e5e3;border-radius:1.2rem;background:#fff}`]
})
export class StudentEntryComponent {}

@Component({
  selector: 'app-instructor-entry', imports: [RouterLink, FormsModule],
  template: `<section class="page narrow"><div class="demo-flag">DEMO · dados sintéticos</div><header class="page-head"><div><p class="eyebrow">Instrutor</p><h1>Quero atuar como instrutor</h1><p>O cadastro será analisado e não produz publicação automática.</p></div></header><article class="notice"><h2>Antes de continuar</h2><p>Cadastro não significa aprovação. As informações serão analisadas e o profissional deve atender aos requisitos aplicáveis.</p><label><input type="checkbox" [(ngModel)]="accepted"> Declaro que as informações fornecidas são verdadeiras e estou ciente de que meu cadastro será analisado antes da publicação.</label><a class="button primary" [class.disabled]="!accepted" [routerLink]="accepted?'/profissional/instrutor/onboarding':null">Continuar</a></article><div class="entry"><a routerLink="/entrar">Já tenho cadastro — Entrar</a><a routerLink="/profissional/demanda">Ver onde há alunos procurando instrutor</a></div></section>`,
  styles: [`.notice,.entry{display:grid;gap:1rem;padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.entry{margin-top:1rem}.notice label{display:flex;gap:.7rem}.disabled{pointer-events:none;opacity:.45}`]
})
export class InstructorEntryComponent { accepted=false; }

@Component({
  selector: 'app-login', imports: [FormsModule, RouterLink],
  template: `<section class="page narrow"><div class="demo-flag">DEMO · contas sintéticas</div><header class="page-head"><div><p class="eyebrow">Acesso</p><h1>Entrar no InstrutorProcnh</h1></div></header><form class="login" (ngSubmit)="submit()"><label>E-mail<input type="email" name="email" [(ngModel)]="email" required></label><label>Senha<input type="password" name="password" [(ngModel)]="password" required></label><button class="button primary" [disabled]="sending">Entrar</button><a href="#" (click)="$event.preventDefault()">Esqueci minha senha</a><a routerLink="/aluno">Criar conta</a>@if(error){<p>{{error}}</p>}</form></section>`,
  styles: [`.login{display:grid;gap:1rem;padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.login label{display:grid;gap:.4rem;font-weight:750}.login input{min-height:3rem;padding:.7rem;border:1px solid #bfd5d2;border-radius:.7rem}.login p{color:#9a302c}`]
})
export class LoginComponent {
  private http=inject(HttpClient); private router=inject(Router);
  email=''; password=''; sending=false; error='';
  submit(){this.sending=true;this.http.post<{roles:string[]}>('/demo/marketplace/session/login/',{email:this.email,password:this.password}).subscribe({next:r=>{this.sending=false;void this.router.navigate([r.roles.includes('INSTRUCTOR')?'/profissional/instrutor/status':'/aluno/jornada'])},error:()=>{this.sending=false;this.error='E-mail ou senha inválidos.'}})}
}

@Component({
  selector:'app-instructor-status', imports:[RouterLink],
  template:`<section class="page narrow"><div class="demo-flag">DEMO · perfil sintético</div><header class="page-head"><div><p class="eyebrow">Área do instrutor</p><h1>Status do cadastro</h1></div></header>@if(profile();as current){<article class="notice"><h2>{{current.display_name}}</h2><strong>EM ANÁLISE</strong><p>Perfil salvo e enviado. Não está publicado.</p><ol><li>✓ Cadastro criado</li><li>✓ Perfil preenchido</li><li>✓ Enviado para análise</li><li>○ Verificação</li><li>○ Aprovação</li><li>○ Publicação</li></ol><a class="button secondary" routerLink="/profissional/instrutor">Abrir painel DEMO</a></article>}@else{<p>Carregando cadastro…</p>}</section>`,
  styles:[`.notice{padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.notice>strong{display:inline-block;padding:.5rem .8rem;border-radius:999px;color:#8a5a00;background:#fff1c9}.notice ol{display:grid;gap:.6rem;list-style:none;padding:0}`]
})
export class InstructorStatusComponent {
  private http=inject(HttpClient); profile=signal<{display_name:string;profile_status:string;publication_status:string}|undefined>(undefined);
  constructor(){this.http.get<{instructor?:{display_name:string;profile_status:string;publication_status:string}}>('/demo/marketplace/session/me/').subscribe(r=>this.profile.set(r.instructor))}
}
