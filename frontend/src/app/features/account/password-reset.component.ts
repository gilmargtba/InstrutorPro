import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

@Component({
  selector:'app-password-reset-request', imports:[FormsModule,RouterLink],
  template:`<section class="page narrow"><p class="eyebrow">Segurança da conta</p><h1>Recuperar senha</h1><p>Informe o e-mail usado no cadastro. Se houver uma conta ativa, enviaremos um link seguro.</p><form class="reset" (ngSubmit)="submit()"><label>E-mail<input type="email" name="email" [(ngModel)]="email" required></label><button class="button primary" [disabled]="sending()">Enviar instruções</button>@if(message()){<p role="status">{{message()}}</p>}<a routerLink="/entrar">Voltar para entrar</a></form></section>`,
  styles:[`.reset{display:grid;gap:1rem}.reset label{display:grid;gap:.35rem;font-weight:700}.reset input{padding:.75rem;border:1px solid #bad4d1;border-radius:.7rem}`]
})
export class PasswordResetRequestComponent{
  private http=inject(HttpClient);email='';sending=signal(false);message=signal('');
  submit(){this.sending.set(true);this.http.post<any>('/marketplace/password-reset/request/',{email:this.email}).subscribe({next:r=>{this.sending.set(false);this.message.set(r.detail)},error:()=>{this.sending.set(false);this.message.set('Não foi possível enviar as instruções agora. Tente novamente.')}})}
}

@Component({
  selector:'app-password-reset-confirm', imports:[FormsModule,RouterLink],
  template:`<section class="page narrow"><p class="eyebrow">Segurança da conta</p><h1>Definir nova senha</h1><form class="reset" (ngSubmit)="submit()"><label>Nova senha<input type="password" name="password" [(ngModel)]="password" minlength="10" required><small>Mínimo de 10 caracteres.</small></label><label>Confirmar nova senha<input type="password" name="confirmation" [(ngModel)]="confirmation" minlength="10" required></label><button class="button primary" [disabled]="sending()">Redefinir senha</button>@if(message()){<p role="alert">{{message()}}</p>}@if(done()){<a routerLink="/entrar">Entrar com a nova senha</a>}</form></section>`,
  styles:[`.reset{display:grid;gap:1rem}.reset label{display:grid;gap:.35rem;font-weight:700}.reset input{padding:.75rem;border:1px solid #bad4d1;border-radius:.7rem}`]
})
export class PasswordResetConfirmComponent{
  private http=inject(HttpClient);private route=inject(ActivatedRoute);password='';confirmation='';sending=signal(false);done=signal(false);message=signal('');
  submit(){if(this.password.length<10||this.password!==this.confirmation){this.message.set('A senha deve ter pelo menos 10 caracteres e as confirmações devem coincidir.');return}this.sending.set(true);this.http.post<any>('/marketplace/password-reset/confirm/',{uid:this.route.snapshot.queryParamMap.get('uid')||'',token:this.route.snapshot.queryParamMap.get('token')||'',password:this.password,password_confirmation:this.confirmation}).subscribe({next:r=>{this.sending.set(false);this.done.set(true);this.message.set(r.detail)},error:e=>{this.sending.set(false);this.message.set(e?.error?.error?.message||'Link inválido ou expirado. Solicite uma nova recuperação.')}})}
}
