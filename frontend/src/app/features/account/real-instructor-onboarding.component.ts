import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { BRAZIL_UFS } from '../../shared/brazil-ufs';

@Component({
  selector: 'app-real-instructor-onboarding',
  imports: [FormsModule],
  template: `<section class="page narrow"><p class="eyebrow">Piloto controlado</p><h1>Complete seu cadastro profissional</h1><p>Seu perfil ficará <strong>não verificado e não publicado</strong> até análise. Não solicitamos documentos nesta etapa.</p>
  <form class="onboarding" (ngSubmit)="submit()">
    <label>Nome público<input name="displayName" [(ngModel)]="form.instructor_display_name" required maxlength="120"></label>
    <label>Apresentação<textarea name="bio" [(ngModel)]="form.bio" required maxlength="2000"></textarea></label>
    <label>Categoria<select name="category" [(ngModel)]="category" required><option value="B">B</option></select></label>
    <label>Transmissão<select name="transmission" [(ngModel)]="transmission" required><option value="MANUAL">Manual</option><option value="AUTOMATIC">Automática</option></select></label>
    <label>WhatsApp profissional<input name="whatsapp" [(ngModel)]="form.whatsapp" placeholder="+5551999999999" required></label>
    <label>Preço por aula<input name="price" [(ngModel)]="form.price_amount" type="number" min="1" step="0.01" required></label>
    <label>Duração em minutos<input name="duration" [(ngModel)]="form.duration_minutes" type="number" min="30" max="240" required></label>
    <fieldset><legend>Veículo</legend><label>Marca<input name="make" [(ngModel)]="form.vehicle.make" required></label><label>Modelo<input name="model" [(ngModel)]="form.vehicle.model" required></label><label>Ano<input name="year" [(ngModel)]="form.vehicle.year" type="number" min="1990" required></label></fieldset>
    <fieldset><legend>Área pública de atendimento</legend><p>Informe o centro aproximado da área onde atende. Não informe sua residência.</p><label>Cidade<input name="city" [(ngModel)]="form.instructor_city" required></label><label>UF<select name="uf" [(ngModel)]="form.instructor_uf" required><option value="">Selecione</option>@for(uf of ufs;track uf){<option [value]="uf">{{uf}}</option>}</select></label><label>Latitude pública<input name="latitude" [(ngModel)]="form.service_latitude" type="number" min="-90" max="90" step="any" required></label><label>Longitude pública<input name="longitude" [(ngModel)]="form.service_longitude" type="number" min="-180" max="180" step="any" required></label><label>Raio<select name="radius" [(ngModel)]="form.service_radius_km"><option [ngValue]="5">5 km</option><option [ngValue]="10">10 km</option><option [ngValue]="20">20 km</option><option [ngValue]="50">50 km</option></select></label><label class="check"><input name="locationAuthorization" [(ngModel)]="form.service_location_authorized" type="checkbox" required> Autorizo a publicação desta área aproximada de atendimento.</label></fieldset>
    <button class="button primary" [disabled]="sending()">Concluir cadastro</button>@if(message()){<p role="alert">{{message()}}</p>}
  </form></section>`,
  styles: [`.onboarding{display:grid;gap:1rem}.onboarding label{display:grid;gap:.35rem;font-weight:700}.onboarding input,.onboarding select,.onboarding textarea{padding:.75rem;border:1px solid #bad4d1;border-radius:.7rem}.onboarding textarea{min-height:7rem}.onboarding fieldset{display:grid;grid-template-columns:1fr 1fr;gap:1rem;padding:1.2rem;border:1px solid #d6e5e3;border-radius:1rem}.onboarding fieldset p,.onboarding fieldset legend,.check{grid-column:1/-1}.check{grid-template-columns:auto 1fr!important}@media(max-width:650px){.onboarding fieldset{grid-template-columns:1fr}}`],
})
export class RealInstructorOnboardingComponent {
  readonly ufs = BRAZIL_UFS;
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  sending = signal(false);
  message = signal('');
  category = 'B';
  transmission = 'MANUAL';
  form: any = {instructor_display_name:'',bio:'',whatsapp:'',price_amount:null,duration_minutes:60,instructor_city:'',instructor_uf:'',service_latitude:null,service_longitude:null,service_radius_km:10,service_location_authorized:false,vehicle:{category:'B',make:'',model:'',year:new Date().getFullYear(),transmission:'MANUAL'}};
  constructor(){this.http.get<any>('/account/me/').subscribe({next:r=>{if(!r.instructor){void this.router.navigateByUrl('/cadastro/instrutor');return}this.form.instructor_display_name=r.instructor.display_name||''},error:()=>void this.router.navigateByUrl('/entrar')})}
  submit(){this.sending.set(true);this.message.set('');this.form.categories=[this.category];this.form.transmission_options=[this.transmission];this.form.vehicle.category=this.category;this.form.vehicle.transmission=this.transmission;this.http.patch('/account/me/',this.form).subscribe({next:()=>void this.router.navigateByUrl('/profissional/instrutor/status'),error:e=>{this.sending.set(false);this.message.set(e?.error?.detail||'Não foi possível concluir. Revise os dados informados.')}})}
}
