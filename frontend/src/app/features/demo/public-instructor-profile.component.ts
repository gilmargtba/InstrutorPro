import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

interface PublicProfile {
  id:string; display_name:string; bio:string; categories:string[]; transmission_options:string[];
  vehicle_available:boolean; availability_summary:string; profile_photo_url:string|null;
  verified_claims:string[]; service_area:{city:string;uf:string;radius_km:number}; synthetic:boolean;
}

@Component({
  selector:'app-public-instructor-profile', imports:[RouterLink],
  template:`<section class="page narrow">@if(loading){<p>Carregando perfil…</p>}@else if(error){<h1>Perfil indisponível</h1><a routerLink="/aluno/instrutores">Voltar à busca</a>}@else if(profile){@if(profile.synthetic){<div class="demo-flag">DEMO · perfil inteiramente sintético</div>}<a class="back" routerLink="/aluno/instrutores/mapa">← Voltar ao mapa</a><div class="profile"><div class="avatar large">@if(profile.profile_photo_url){<img [src]="profile.profile_photo_url" alt="Foto de perfil aprovada">}@else{<i class="pi pi-user"></i>}</div><div><p class="eyebrow">Instrutor disponível</p><h1>{{profile.display_name}}</h1><p>{{profile.service_area.city}}/{{profile.service_area.uf}} · atendimento em até {{profile.service_area.radius_km}} km</p></div></div><article><h2>Sobre</h2><p>{{profile.bio || 'O profissional ainda não adicionou uma apresentação pública.'}}</p><h2>Atendimento</h2><p>Categoria {{profile.categories.join(', ')}} · {{profile.transmission_options.join(' / ')}} · {{profile.vehicle_available?'Possui veículo':'Sem veículo informado'}}</p><p>{{profile.availability_summary}}</p><h2>Verificações aprovadas</h2>@if(!profile.verified_claims.length){<p>Nenhuma verificação pública disponível.</p>}@for(claim of profile.verified_claims;track claim){<p>✓ {{claimLabel(claim)}}</p>}<p class="muted">Documentos originais e endereços privados nunca são exibidos.</p><a class="button primary" routerLink="/aluno/solicitar" [queryParams]="{instrutor:profile.id}">Solicitar aula</a></article>}</section>`
})
export class PublicInstructorProfileComponent {
  private readonly http=inject(HttpClient); private readonly changeDetector=inject(ChangeDetectorRef); profile?:PublicProfile;loading=true;error=false;
  constructor(){const id=inject(ActivatedRoute).snapshot.paramMap.get('id');this.http.get<PublicProfile>(`/instructors/${id}/`).subscribe({next:p=>{this.profile=p;this.loading=false;this.changeDetector.detectChanges()},error:()=>{this.error=true;this.loading=false;this.changeDetector.detectChanges()}})}
  claimLabel(claim:string){return ({CREDENTIAL_VERIFIED:'Credenciamento verificado',COURSE_VERIFIED:'Curso de instrutor verificado',VEHICLE_VERIFIED:'Veículo/documentação verificada'} as Record<string,string>)[claim]||claim}
}
