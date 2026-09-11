import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Meta, Title } from '@angular/platform-browser';

interface PublicProfile {
  id:string; display_name:string; bio:string; categories:string[]; transmission_options:string[];
  vehicle_available:boolean; availability_summary:string; profile_photo_url:string|null;
  verified_claims:string[]; service_area:{city:string;uf:string;radius_km:number}; synthetic:boolean;
  price_amount:number;price_from:boolean;duration_minutes:number;vehicle:{make:string;model:string;year:number;transmission:string}|null;
}

@Component({
  selector:'app-public-instructor-profile', imports:[RouterLink],
  template:`<section class="page narrow">@if(loading){<p>Carregando perfil…</p>}@else if(error){<h1>Perfil indisponível</h1><a routerLink="/aluno/instrutores">Voltar à busca</a>}@else if(profile){@if(profile.synthetic){<div class="demo-flag">DEV/TEST · perfil sintético</div>}<a class="back" routerLink="/aluno/instrutores/mapa">← Voltar ao mapa</a><div class="profile"><div class="avatar large">@if(profile.profile_photo_url){<img [src]="profile.profile_photo_url" alt="Foto aprovada de {{profile.display_name}}">}@else{<i class="pi pi-user"></i>}</div><div><p class="eyebrow">Instrutor disponível</p><h1>{{profile.display_name}}</h1><p>Atende em {{profile.service_area.city}}/{{profile.service_area.uf}} · até {{profile.service_area.radius_km}} km</p>@if(profile.verified_claims.includes('CREDENTIAL_VERIFIED')){<p>✓ Credenciamento verificado</p>}</div></div><article><h2>Sobre</h2><p>{{profile.bio || 'O profissional ainda não adicionou uma apresentação pública.'}}</p><h2>Informações das aulas</h2><p>Categoria {{profile.categories.join(', ')}} · {{profile.transmission_options.join(' / ')}}</p>@if(profile.vehicle){<p>Veículo: {{profile.vehicle.make}} {{profile.vehicle.model}} {{profile.vehicle.year}} · {{profile.vehicle.transmission}}</p>}<p>{{profile.price_from?'A partir de ':''}}<strong>R$ {{profile.price_amount}}</strong> por aula de {{profile.duration_minutes}} minutos.</p><p>{{profile.availability_summary}}</p><h2>Verificações aprovadas</h2>@if(!profile.verified_claims.length){<p>Nenhuma verificação pública disponível.</p>}@for(claim of profile.verified_claims;track claim){<p>✓ {{claimLabel(claim)}}</p>}<p class="muted">Documentos, telefone bruto, endereço residencial e placa nunca são exibidos.</p><button class="button primary" type="button" (click)="contact()"><i class="pi pi-whatsapp"></i> Chamar no WhatsApp</button>@if(contactError){<p role="alert">{{contactError}}</p>}</article>}</section>`
})
export class PublicInstructorProfileComponent {
  private readonly http=inject(HttpClient); private readonly changeDetector=inject(ChangeDetectorRef);private readonly title=inject(Title);private readonly meta=inject(Meta);private readonly id=inject(ActivatedRoute).snapshot.paramMap.get('id'); profile?:PublicProfile;loading=true;error=false;contactError='';
  constructor(){this.http.get<PublicProfile>(`/instructors/${this.id}/`).subscribe({next:p=>{this.profile=p;this.loading=false;this.title.setTitle(`Instrutor de direção em ${p.service_area.city} - ${p.display_name} | InstrutorProCNH`);this.meta.updateTag({name:'description',content:`Conheça ${p.display_name}, instrutor de direção em ${p.service_area.city}. Consulte categorias, veículo, preço e área de atendimento.`});this.changeDetector.detectChanges()},error:()=>{this.error=true;this.loading=false;this.changeDetector.detectChanges()}})}
  contact(){if(!this.profile)return;this.http.post<{destination_url:string}>(`/instructors/${this.id}/whatsapp-contact/`,{category:this.profile.categories[0],source:'public-profile'}).subscribe({next:r=>window.location.assign(r.destination_url),error:()=>{this.contactError='Não foi possível abrir o WhatsApp agora.';this.changeDetector.detectChanges()}})}
  claimLabel(claim:string){return ({CREDENTIAL_VERIFIED:'Credenciamento verificado',COURSE_VERIFIED:'Curso de instrutor verificado',VEHICLE_VERIFIED:'Veículo/documentação verificada'} as Record<string,string>)[claim]||claim}
}
