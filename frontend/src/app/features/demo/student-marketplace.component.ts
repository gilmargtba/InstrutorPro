import { HttpClient } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

type Registration = {
  username: string;
  email: string;
  password: string;
  display_name: string;
  city: string;
  uf: string;
  intended_category: string;
  synthetic_data_confirmed: boolean;
};

@Component({
  selector: 'app-student-marketplace',
  imports: [FormsModule, RouterLink],
  template: `
    <section class="page narrow">
      <div class="demo-flag">DEMO · aceite somente identidades sintéticas</div>
      <header class="page-head"><div><p class="eyebrow">Marketplace M1</p><h1>Área do aluno demonstrativo</h1><p>Crie uma identidade terminada em <b>&#64;example.invalid</b>. Não informe dados reais.</p></div></header>
      @if (!registered) {
        <form class="market-form" (ngSubmit)="register()">
          <label>Nome demonstrativo<input name="name" [(ngModel)]="form.display_name" required></label>
          <label>Usuário<input name="username" [(ngModel)]="form.username" required></label>
          <label>E-mail sintético<input name="email" type="email" [(ngModel)]="form.email" required></label>
          <label>Senha da demonstração<input name="password" type="password" minlength="10" [(ngModel)]="form.password" required></label>
          <div class="two"><label>Cidade<input name="city" [(ngModel)]="form.city" required></label><label>UF<select name="uf" [(ngModel)]="form.uf"><option>RS</option><option>SC</option><option>SP</option><option>RJ</option><option>ES</option></select></label></div>
          <label class="check"><input name="synthetic" type="checkbox" [(ngModel)]="form.synthetic_data_confirmed"> Confirmo que todos os dados são sintéticos.</label>
          <button class="button primary" [disabled]="sending">{{sending ? 'Criando…' : 'Criar aluno DEMO'}}</button>
        </form>
      } @else {
        <form class="market-form" (ngSubmit)="createDemand()">
          <h2>O que você procura?</h2>
          <div class="two"><label>Categoria<select name="category" [(ngModel)]="demand.category"><option value="B">B</option></select></label><label>Transmissão<select name="transmission" [(ngModel)]="demand.transmission"><option value="MANUAL">Manual</option><option value="AUTOMATIC">Automática</option></select></label></div>
          <label>Região aproximada<input name="region" [(ngModel)]="demand.region" placeholder="Ex.: Centro"></label>
          <label>Disponibilidade<input name="availability" [(ngModel)]="demand.availability" placeholder="Ex.: noites"></label>
          <button class="button primary" [disabled]="sending">Registrar demanda sintética</button>
          <a class="button ghost" routerLink="/aluno/instrutores">Ver instrutores</a>
        </form>
      }
      @if (message) { <p class="result" [class.error]="failed">{{message}}</p> }
    </section>
  `,
  styles: [`
    .market-form{display:grid;gap:1rem;padding:1.5rem;border:1px solid #d6e5e3;border-radius:1.2rem;background:#fff}
    label{display:flex;flex-direction:column;gap:.4rem;font-weight:750}input,select{min-height:3rem;padding:.7rem;border:1px solid #bfd5d2;border-radius:.7rem}.two{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.check{flex-direction:row;align-items:center}.check input{min-height:auto}.result{padding:1rem;border-radius:.8rem;background:#e5f6ef;color:#087565}.result.error{background:#fff0ef;color:#9a302c}@media(max-width:600px){.two{grid-template-columns:1fr}}
  `],
})
export class StudentMarketplaceComponent {
  private readonly http = inject(HttpClient);
  registered = false;
  sending = false;
  failed = false;
  message = '';
  form: Registration = { username:'aluno_demo', email:'aluno@example.invalid', password:'DemoSeguro123!', display_name:'Aluno Demo', city:'Porto Alegre', uf:'RS', intended_category:'B', synthetic_data_confirmed:false };
  demand = { category:'B', city:'Porto Alegre', uf:'RS', region:'Centro', radius_km:10, transmission:'MANUAL', availability:'Noite' };

  register() {
    this.sending = true; this.message = '';
    this.http.post('/demo/marketplace/students/register/', this.form).subscribe({
      next: () => { this.registered = true; this.sending = false; this.failed = false; this.demand.city = this.form.city; this.demand.uf = this.form.uf; this.message = 'Aluno sintético criado. A sessão DEMO está ativa.'; },
      error: () => { this.sending = false; this.failed = true; this.message = 'Não foi possível criar. Use e-mail @example.invalid, senha com 10 caracteres e dados exclusivamente sintéticos.'; },
    });
  }

  createDemand() {
    this.sending = true; this.message = '';
    this.http.post('/demo/marketplace/demands/', this.demand).subscribe({
      next: () => { this.sending = false; this.failed = false; this.message = 'Demanda sintética registrada sem publicar localização individual.'; },
      error: () => { this.sending = false; this.failed = true; this.message = 'Não foi possível registrar a demanda demonstrativa.'; },
    });
  }
}
