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
  template: `<section class="page narrow"><div class="demo-flag">DEMO · contas sintéticas</div><header class="page-head"><div><p class="eyebrow">Acesso</p><h1>Entrar no InstrutorProCNH</h1></div></header><form class="login" (ngSubmit)="submit()"><label>E-mail<input type="email" name="email" [(ngModel)]="email" required></label><label>Senha<input type="password" name="password" [(ngModel)]="password" required></label><button class="button primary" [disabled]="sending">Entrar</button><a href="#" (click)="$event.preventDefault()">Esqueci minha senha</a><a routerLink="/aluno">Criar conta</a>@if(error){<p>{{error}}</p>}</form></section>`,
  styles: [`.login{display:grid;gap:1rem;padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.login label{display:grid;gap:.4rem;font-weight:750}.login input{min-height:3rem;padding:.7rem;border:1px solid #bfd5d2;border-radius:.7rem}.login p{color:#9a302c}`]
})
export class LoginComponent {
  private http=inject(HttpClient); private router=inject(Router);
  email=''; password=''; sending=false; error='';
  submit(){this.sending=true;this.http.post<{roles:string[];is_staff:boolean}>('/demo/marketplace/session/login/',{email:this.email,password:this.password}).subscribe({next:r=>{this.sending=false;const target=r.is_staff?'/admin/':r.roles.includes('INSTRUCTOR')?'/profissional/instrutor':r.roles.includes('STUDENT')?'/aluno/painel':'/';if(target==='/admin/')window.location.assign(target);else void this.router.navigate([target])},error:()=>{this.sending=false;this.error='E-mail ou senha inválidos.'}})}
}

type StudentSession={display_name:string;city:string;uf:string;intended_category:string;preferred_transmission:string;request_count:number;upcoming_lesson_count:number};
@Component({selector:'app-student-dashboard',imports:[RouterLink],template:`<section class="page wide"><header class="page-head"><div><p class="eyebrow">Área do aluno</p><h1>Olá, {{student()?.display_name}}</h1><p>{{student()?.city}}/{{student()?.uf}}</p></div><a class="button primary" routerLink="/aluno/instrutores">Encontrar instrutor</a></header>@if(student();as s){<div class="portal-grid"><article><h2>Minhas solicitações</h2><strong>{{s.request_count}}</strong><p>{{s.request_count?'Acompanhe suas solicitações.':'Você ainda não possui solicitações.'}}</p></article><article><h2>Próximas aulas</h2><strong>{{s.upcoming_lesson_count}}</strong><p>{{s.upcoming_lesson_count?'Veja seus próximos compromissos.':'Nenhuma aula agendada.'}}</p></article><article><h2>Histórico</h2><p>Seu histórico aparecerá aqui após a primeira aula registrada na plataforma.</p></article><article><h2>Meu perfil</h2><p>Categoria {{s.intended_category}} · {{label(s.preferred_transmission)}}</p><small>{{s.city}}/{{s.uf}}</small></article></div>}@else{<p>Carregando seu painel…</p>}</section>`,styles:[`.portal-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}.portal-grid article{padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.portal-grid strong{font-size:2rem;color:#0c807e}@media(max-width:650px){.portal-grid{grid-template-columns:1fr}}`]})
export class StudentDashboardComponent{private http=inject(HttpClient);student=signal<StudentSession|undefined>(undefined);constructor(){this.http.get<{student?:StudentSession}>('/demo/marketplace/session/me/').subscribe(r=>this.student.set(r.student))}label(v:string){return v==='MANUAL'?'Manual':v==='AUTOMATIC'?'Automática':'Transmissão indiferente'}}

@Component({
  selector:'app-instructor-status', imports:[RouterLink],
  template:`<section class="page narrow"><header class="page-head"><div><p class="eyebrow">Área do instrutor</p><h1>Status do cadastro</h1></div></header>@if(profile();as current){<article class="notice"><h2>{{current.display_name}}</h2><strong>{{current.profile_status==='SUBMITTED'?'EM ANÁLISE':current.profile_status}}</strong><p>O cadastro está salvo e não será publicado automaticamente.</p><ol><li>✓ Conta criada</li><li>✓ Perfil preenchido</li><li>{{current.document_count>0?'✓':'○'}} Documentos enviados</li><li>{{current.profile_status==='SUBMITTED'?'✓':'○'}} Enviado para análise</li><li>{{current.verification_status==='VERIFIED'?'✓':'○'}} Verificação</li><li>{{current.profile_status==='APPROVED'?'✓':'○'}} Aprovação</li><li>{{current.publication_status==='APPROVED'?'✓':'○'}} Publicação</li></ol><a class="button secondary" routerLink="/profissional/instrutor">Abrir painel</a></article>}@else{<p>Carregando cadastro…</p>}</section>`,
  styles:[`.notice{padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.notice>strong{display:inline-block;padding:.5rem .8rem;border-radius:999px;color:#8a5a00;background:#fff1c9}.notice ol{display:grid;gap:.6rem;list-style:none;padding:0}`]
})
export class InstructorStatusComponent {
  private http=inject(HttpClient); profile=signal<any>(undefined);
  constructor(){this.http.get<{instructor?:any}>('/demo/marketplace/session/me/').subscribe(r=>this.profile.set(r.instructor))}
}

@Component({selector:'app-instructor-portal',imports:[RouterLink],template:`<section class="page wide"><header class="page-head"><div><p class="eyebrow">Área do instrutor</p><h1>Olá, {{profile()?.display_name}}</h1></div><a class="button secondary" routerLink="/profissional/instrutor/status">Ver status completo</a></header>@if(profile();as p){<div class="portal-grid"><article><h2>Status do perfil</h2><strong>{{p.profile_status}}</strong><p>Publicação: {{p.publication_status}}</p></article><article><h2>Credenciamento</h2><strong>{{p.verification_status}}</strong><p>{{p.document_count}} documento(s) privado(s).</p></article><article><h2>Veículo</h2><p>{{p.vehicle?p.vehicle.make+' '+p.vehicle.model:'Nenhum veículo cadastrado.'}}</p></article><article><h2>Área de atendimento</h2><p>{{p.service_area?p.service_area.city+'/'+p.service_area.uf+' · '+p.service_area.radius_km+' km':'Área não cadastrada.'}}</p></article><article><h2>Novas solicitações</h2><strong>{{p.pending_requests}}</strong><p>{{p.pending_requests?'Há solicitações aguardando ação.':'Nenhuma solicitação nova.'}}</p></article><article><h2>Agenda</h2><p>Nenhuma aula agendada.</p></article></div>}@else{<p>Carregando seu painel…</p>}</section>`,styles:[`.portal-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.portal-grid article{padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.portal-grid strong{color:#0c807e}@media(max-width:800px){.portal-grid{grid-template-columns:1fr}}`]})
export class InstructorPortalComponent{private http=inject(HttpClient);profile=signal<any>(undefined);constructor(){this.http.get<{instructor?:any}>('/demo/marketplace/session/me/').subscribe(r=>this.profile.set(r.instructor))}}
