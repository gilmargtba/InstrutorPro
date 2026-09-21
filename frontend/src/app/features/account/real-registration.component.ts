import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { BRAZIL_UFS } from '../../shared/brazil-ufs';

@Component({
  selector: 'app-real-registration',
  imports: [FormsModule, RouterLink],
  template: `<section class="page narrow"><p class="eyebrow">Piloto controlado</p><h1>Criar conta de {{role==='STUDENT'?'aluno':'instrutor'}}</h1>
  <form #registrationForm="ngForm" class="account-form" (ngSubmit)="submit(registrationForm.valid)">
    <label>Nome<input name="name" [(ngModel)]="form.display_name" required maxlength="120"></label>
    <label>Usuário<input name="username" [(ngModel)]="form.username" required></label>
    <label>E-mail<input name="email" [(ngModel)]="form.email" type="email" required></label>
    <label>Data de nascimento<input name="birth" [(ngModel)]="form.birth_date" type="date" required></label>
    @if(role==='STUDENT'){<label>Cidade<input name="city" [(ngModel)]="form.city" required></label><label>UF<select name="uf" [(ngModel)]="form.uf" required><option value="">Selecione</option>@for(uf of ufs; track uf){<option [value]="uf">{{uf}}</option>}</select></label>}
    <label>Senha<input name="password" [(ngModel)]="form.password" type="password" minlength="10" required><small>Mínimo de 10 caracteres.</small></label>
    <label>Confirmar senha<input name="confirmation" [(ngModel)]="form.password_confirmation" type="password" minlength="10" required></label>
    <label class="check"><input name="terms" [(ngModel)]="form.terms_accepted" type="checkbox" required> Li e aceito os <a [routerLink]="termsPath" target="_blank">Termos de Uso</a>.</label>
    <label class="check"><input name="privacy" [(ngModel)]="form.privacy_acknowledged" type="checkbox" required> Declaro que tive acesso à <a routerLink="/privacidade" target="_blank">Política de Privacidade</a>.</label>
    <button class="button primary" [disabled]="sending()||!versionsReady()||registrationForm.invalid">Criar conta</button>
    @if(message()){<p role="alert">{{message()}}</p>}
  </form></section>`,
  styles:[`.account-form{display:grid;gap:1rem}.account-form label{display:grid;gap:.35rem;font-weight:700}.account-form input{padding:.75rem;border:1px solid #bad4d1;border-radius:.7rem}.check{grid-template-columns:auto 1fr;align-items:start}.check input{margin-top:.25rem}`]
})
export class RealRegistrationComponent {
  readonly ufs = BRAZIL_UFS;
  private http=inject(HttpClient); private route=inject(ActivatedRoute); private router=inject(Router);
  role=this.route.snapshot.data['role'] as 'STUDENT'|'INSTRUCTOR';
  termsPath=this.role==='STUDENT'?'/termos/aluno':'/termos/instrutor';
  sending=signal(false); message=signal(''); versionsReady=signal(false);
  form:any={role:this.role,username:'',email:'',password:'',password_confirmation:'',display_name:'',birth_date:'',city:'',uf:'',terms_version:'',privacy_version:'',terms_accepted:false,privacy_acknowledged:false};
  constructor(){
    const audience=this.role.toLowerCase();
    this.http.get<any>(`/legal/documents/${audience}/`).subscribe(terms=>{this.form.terms_version=terms.version;this.ready()});
    this.http.get<any>('/privacy/notice/').subscribe(privacy=>{this.form.privacy_version=privacy.version;this.ready()});
  }
  private ready(){this.versionsReady.set(!!this.form.terms_version&&!!this.form.privacy_version)}
  submit(valid:boolean|null=true){if(!valid){this.message.set('Revise os campos: a senha deve ter pelo menos 10 caracteres.');return}this.sending.set(true);this.message.set('');this.http.post('/marketplace/accounts/register/',this.form).subscribe({next:()=>this.router.navigateByUrl(this.role==='INSTRUCTOR'?'/profissional/instrutor/onboarding':'/minha-conta'),error:e=>{this.sending.set(false);this.message.set(this.errorMessage(e))}})}
  private errorMessage(error:any){const payload=error?.error?.error;const details=payload?.details;if(details&&typeof details==='object'){const messages=Object.values(details).flat().filter(value=>typeof value==='string');if(messages.length)return messages.join(' ')}return payload?.message||error?.error?.detail||'Cadastro indisponível. Confira os dados e os aceites.'}
}
