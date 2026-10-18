import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

type CfcSummary = {
  id: string;
  display_name: string;
  declared_instructor_count: number;
  pre_registered_count: number;
  accepted_count: number;
};
type CfcLink = { id: string; display_name: string; email: string; status: 'PENDING' | 'ACCEPTED' };

@Component({
  selector: 'app-professional-landing',
  imports: [RouterLink],
  template: `<section class="page wide"><header class="page-head"><div><p class="eyebrow">Área profissional</p><h1>Como você atua na jornada?</h1><p>Escolha seu acesso.</p></div></header>
    <div class="cards"><article><i class="pi pi-car"></i><h2>Instrutor</h2><p>Crie sua própria conta e acompanhe a análise do seu perfil.</p><a class="button primary" routerLink="/cadastro/instrutor">Cadastrar instrutor</a></article>
    <article><i class="pi pi-building"></i><h2>CFC</h2><p>Informe quantos instrutores integram seu CFC e inicie o pré-cadastro individual de cada um. Cada instrutor ativa sua própria conta por e-mail.</p><a class="button secondary" routerLink="/cfc">Acessar painel do CFC</a><small>O acesso inicial do CFC é habilitado pelo administrador.</small></article></div>
    <p>Pré-cadastro e vínculo com CFC não equivalem a verificação, credenciamento oficial ou publicação na busca.</p></section>`,
  styles: [`.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.cards article{display:grid;gap:.7rem;align-content:start;padding:1.5rem;border:1px solid #c8dcd8;border-radius:1rem;background:#fff}.cards i{font-size:2rem;color:#0b8180}.cards small{display:block;color:#526b73}@media(max-width:700px){.cards{grid-template-columns:1fr}}`],
})
export class ProfessionalLandingComponent {}

@Component({
  selector: 'app-cfc-dashboard',
  imports: [FormsModule, RouterLink],
  template: `<section class="page wide"><header class="page-head"><div><p class="eyebrow">Painel privado do CFC</p><h1>Instrutores vinculados</h1></div><a routerLink="/profissional">Área profissional</a></header>
    @if(error()){<p role="alert">{{error()}}</p>}
    @if(memberships().length){<label>CFC <select name="selectedCfc" [ngModel]="selectedId()" (ngModelChange)="select($event)">@for(item of memberships();track item.id){<option [value]="item.id">{{item.display_name}}</option>}</select></label>}
    @if(cfc();as current){<div class="metrics"><article><strong>{{current.declared_instructor_count}}</strong><span>informados pelo CFC</span></article><article><strong>{{current.pre_registered_count}}</strong><span>pré-cadastrados</span></article><article><strong>{{current.accepted_count}}</strong><span>contas ativadas</span></article></div>
      <form class="box" (ngSubmit)="saveCount()"><h2>Quantos instrutores integram o CFC?</h2><label>Quantidade total <input type="number" name="count" [(ngModel)]="declaredCount" min="0" max="100000" required></label><button class="button secondary" [disabled]="busy()">Salvar quantidade</button></form>
      <form class="box" (ngSubmit)="invite()"><h2>Pré-cadastrar instrutor</h2><p>Informe somente nome e e-mail. A senha, os termos e o aceite do vínculo pertencem ao instrutor. O perfil não será publicado automaticamente.</p><label>Nome completo <input name="name" [(ngModel)]="instructorName" maxlength="120" required></label><label>E-mail do instrutor <input type="email" name="email" [(ngModel)]="instructorEmail" required></label><button class="button primary" [disabled]="busy()">Criar pré-cadastro e enviar convite</button></form>
      @if(message()){<p role="status">{{message()}}</p>}
      <h2>Cadastros deste CFC</h2><div class="links">@for(link of links();track link.id){<article><strong>{{link.display_name}}</strong><span>{{link.email}}</span><small>{{link.status==='ACCEPTED'?'Conta ativada pelo instrutor':'Aguardando ativação pelo instrutor'}}</small>@if(link.status==='PENDING'){<button class="button secondary" [disabled]="busy()" (click)="resend(link.id)">Reenviar convite</button>}</article>}@empty{<p>Nenhum instrutor pré-cadastrado.</p>}</div>
    }@else if(!error()){<p>Carregando painel…</p>}</section>`,
  styles: [`.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1rem 0}.metrics article,.box,.links article{padding:1.2rem;border:1px solid #c8dcd8;border-radius:.8rem;background:#fff}.metrics strong{display:block;font-size:2rem;color:#087f80}.metrics span,.links span,.links small{display:block}.box{display:grid;gap:.8rem;margin:1rem 0;max-width:650px}.box label{display:grid;gap:.3rem;font-weight:700}.box input,.page select{padding:.75rem;border:1px solid #aecbc7;border-radius:.5rem}.links{display:grid;gap:.6rem}@media(max-width:650px){.metrics{grid-template-columns:1fr}}`],
})
export class CFCDashboardComponent {
  private http = inject(HttpClient);
  memberships = signal<{id:string;display_name:string}[]>([]);
  selectedId = signal('');
  cfc = signal<CfcSummary | null>(null);
  links = signal<CfcLink[]>([]);
  error = signal('');
  message = signal('');
  busy = signal(false);
  declaredCount = 0;
  instructorName = '';
  instructorEmail = '';

  constructor() {
    this.http.get<{id:string;display_name:string}[]>('/cfc/memberships/').subscribe({
      next: rows => {this.memberships.set(rows); if(rows.length) this.select(rows[0].id); else this.error.set('Sua conta não possui vínculo ativo com um CFC. Peça ao administrador para habilitar o acesso.');},
      error: () => this.error.set('Entre com a conta vinculada ao CFC para acessar este painel.'),
    });
  }
  select(id:string) {this.selectedId.set(id);this.message.set('');this.load();}
  private load() {
    const id = this.selectedId();
    this.http.get<CfcSummary>(`/cfc/${id}/`).subscribe({next: row => {this.cfc.set(row);this.declaredCount=row.declared_instructor_count;},error:()=>this.error.set('Não foi possível carregar o CFC.')});
    this.http.get<CfcLink[]>(`/cfc/${id}/instructors/`).subscribe({next:rows=>this.links.set(rows),error:()=>this.error.set('Não foi possível carregar os instrutores.')});
  }
  saveCount() {
    if(!Number.isInteger(this.declaredCount)||this.declaredCount<0)return;
    this.busy.set(true);this.message.set('');
    this.http.patch(`/cfc/${this.selectedId()}/`,{declared_instructor_count:this.declaredCount}).subscribe({
      next:()=>{this.busy.set(false);this.message.set('Quantidade atualizada.');this.load();},
      error:()=>{this.busy.set(false);this.message.set('Não foi possível atualizar a quantidade.');},
    });
  }
  invite() {
    if(!this.instructorName.trim()||!this.instructorEmail.trim())return;
    this.busy.set(true);this.message.set('');
    this.http.post(`/cfc/${this.selectedId()}/instructors/`,{display_name:this.instructorName.trim(),email:this.instructorEmail.trim()}).subscribe({
      next:()=>{this.busy.set(false);this.instructorName='';this.instructorEmail='';this.message.set('Convite enviado. O instrutor precisa ativar a conta.');this.load();},
      error:e=>{this.busy.set(false);this.message.set(e?.error?.detail||'Não foi possível criar o pré-cadastro. Verifique o e-mail e a configuração de envio.');},
    });
  }
  resend(linkId:string) {
    this.busy.set(true);this.message.set('');
    this.http.post(`/cfc/${this.selectedId()}/instructors/${linkId}/resend/`,{}).subscribe({
      next:()=>{this.busy.set(false);this.message.set('Convite reenviado ao instrutor.');},
      error:()=>{this.busy.set(false);this.message.set('Não foi possível reenviar o convite.');},
    });
  }
}

@Component({
  selector: 'app-cfc-instructor-activation',
  imports: [FormsModule, RouterLink],
  template: `<section class="page narrow"><p class="eyebrow">Pré-cadastro pelo CFC</p><h1>Ative sua conta de instrutor</h1><p>Defina você mesmo a senha. O vínculo com o CFC não verifica nem publica seu perfil.</p>
    <form class="activation" (ngSubmit)="activate()"><label>Data de nascimento <input type="date" name="birth" [(ngModel)]="birthDate" required></label><label>Senha <input type="password" name="password" [(ngModel)]="password" minlength="10" required></label><label>Confirmar senha <input type="password" name="confirmation" [(ngModel)]="confirmation" minlength="10" required></label>
      <label class="check"><input type="checkbox" name="terms" [(ngModel)]="termsAccepted" required> Li e aceito os <a routerLink="/termos/instrutor" target="_blank">Termos do Instrutor</a>.</label>
      <label class="check"><input type="checkbox" name="privacy" [(ngModel)]="privacyAcknowledged" required> Li a <a routerLink="/privacidade" target="_blank">Política de Privacidade</a>.</label>
      <label class="check"><input type="checkbox" name="link" [(ngModel)]="linkAccepted" required> Aceito o vínculo de meu cadastro com o CFC que enviou este convite.</label>
      <button class="button primary" [disabled]="busy()||!termsVersion||!privacyVersion">Ativar minha conta</button>@if(message()){<p role="alert">{{message()}}</p>}</form></section>`,
  styles: [`.activation{display:grid;gap:1rem}.activation label{display:grid;gap:.35rem;font-weight:700}.activation input:not([type=checkbox]){padding:.75rem;border:1px solid #aecbc7;border-radius:.5rem}.activation .check{display:block;font-weight:400}.activation .check input{margin-right:.4rem}`],
})
export class CFCInstructorActivationComponent {
  private http=inject(HttpClient);private route=inject(ActivatedRoute);private router=inject(Router);
  birthDate='';password='';confirmation='';termsAccepted=false;privacyAcknowledged=false;linkAccepted=false;
  termsVersion='';privacyVersion='';busy=signal(false);message=signal('');
  constructor(){
    this.http.get<{version:string}>('/legal/documents/instructor/').subscribe({next:r=>this.termsVersion=r.version,error:()=>this.message.set('Termos do Instrutor indisponíveis.')});
    this.http.get<{version:string}>('/privacy/notice/').subscribe({next:r=>this.privacyVersion=r.version,error:()=>this.message.set('Política de Privacidade indisponível.')});
  }
  activate(){
    if(!this.birthDate||this.password.length<10||this.password!==this.confirmation||!this.termsAccepted||!this.privacyAcknowledged||!this.linkAccepted){this.message.set('Confira os dados e os aceites obrigatórios.');return;}
    this.busy.set(true);this.message.set('');
    this.http.post('/cfc/activate-instructor/',{
      uid:this.route.snapshot.queryParamMap.get('uid')||'',token:this.route.snapshot.queryParamMap.get('token')||'',
      birth_date:this.birthDate,password:this.password,password_confirmation:this.confirmation,
      terms_version:this.termsVersion,privacy_version:this.privacyVersion,
      terms_accepted:this.termsAccepted,privacy_acknowledged:this.privacyAcknowledged,cfc_link_accepted:this.linkAccepted,
    }).subscribe({next:()=>void this.router.navigateByUrl('/profissional/instrutor/onboarding'),error:()=>{this.busy.set(false);this.message.set('Não foi possível ativar a conta. Confira o convite, a senha e os aceites.');}});
  }
}
