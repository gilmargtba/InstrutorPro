import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, NgZone, OnDestroy, ViewChild, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import L from 'leaflet';
import { BRAZIL_UFS } from '../../shared/brazil-ufs';
import { GeocodingResult, InstructorSearchProvider } from '../../demo/instructor-search.provider';

@Component({
  selector: 'app-real-instructor-onboarding',
  imports: [FormsModule],
  template: `<section class="page narrow"><p class="eyebrow">Cadastro profissional</p><h1>Complete seu cadastro profissional</h1><p>Seu perfil ficará <strong>não verificado e não publicado</strong> até análise. Documentos profissionais e foto de perfil são enviados separadamente para revisão privada.</p>
  <form #onboardingForm="ngForm" class="onboarding" (ngSubmit)="submit(onboardingForm.valid)">
    <label>Nome público<input name="displayName" [(ngModel)]="form.instructor_display_name" required maxlength="120"></label>
    <label>Apresentação<textarea name="bio" [(ngModel)]="form.bio" required maxlength="2000"></textarea></label>
    <fieldset class="photo-fieldset"><legend>Foto do perfil (opcional)</legend>
      <p>Envie uma foto sua em JPEG ou PNG, até 5 MB. Ela fica privada até análise e só aparece ao público depois de aprovada e se seu perfil estiver publicado.</p>
      <button type="button" class="button secondary" (click)="loadPhotoStatus()">Ver situação da foto</button>
      @if(photoStatus()){<p role="status">Situação: {{photoStatusLabel(photoStatus())}}. @if(photoPreviewUrl()){<a [href]="photoPreviewUrl()" target="_blank" rel="noopener">Ver minha foto privada</a>}</p>}
      @if(photoAvailable() === false){<p role="status">O envio de foto está indisponível neste momento.</p>}
      <label>Selecionar foto<input type="file" accept="image/jpeg,image/png" (change)="selectPhoto($event)"></label>
      <label class="check"><input type="checkbox" name="photoAuthorization" [(ngModel)]="photoAuthorized"> Autorizo a exibição desta foto no meu perfil público após revisão e publicação.</label>
      <button type="button" class="button secondary" [disabled]="!selectedPhoto||!photoAuthorized||photoSending()||photoAvailable()===false" (click)="uploadPhoto()">{{photoSending()?'Enviando…':'Enviar foto para revisão'}}</button>
      @if(photoMessage()){<p role="status">{{photoMessage()}}</p>}
    </fieldset>
    <fieldset><legend>Categorias</legend><div class="category-options">@for(option of categoryOptions;track option){<label class="check"><input type="checkbox" [name]="'category-'+option" [checked]="categories.includes(option)" (change)="toggleCategory(option)"> Categoria {{option}}</label>}</div></fieldset>
    <fieldset><legend>Ofertas por categoria</legend><p>Informe preço e duração próprios para cada categoria. Marcar A e B não copia preços nem publica o perfil automaticamente.</p>
      @for(category of categories;track category){<div class="category-offer"><strong>Categoria {{category}}</strong>
        <label>Preço por aula (R$)<input [name]="'offer-price-'+category" [(ngModel)]="offerDrafts[category].price_amount" type="number" min="1" step="0.01" required></label>
        <label>Duração (minutos)<input [name]="'offer-duration-'+category" [(ngModel)]="offerDrafts[category].duration_minutes" type="number" min="30" max="240" required></label>
      </div>}
    </fieldset>
    <label>Transmissão<select name="transmission" [(ngModel)]="transmission" required><option value="MANUAL">Manual</option><option value="AUTOMATIC">Automática</option></select></label>
    <label>WhatsApp profissional<input name="whatsapp" [(ngModel)]="form.whatsapp" placeholder="+5564999999999" pattern="[+]55[1-9][0-9]{9,10}" required><small>Use +55, DDD e número, somente com algarismos. Ex.: +5564999999999.</small></label>
    <fieldset><legend>Veículo</legend><label>Marca<input name="make" [(ngModel)]="form.vehicle.make" required></label><label>Modelo<input name="model" [(ngModel)]="form.vehicle.model" required></label><label>Ano<input name="year" [(ngModel)]="form.vehicle.year" type="number" min="1990" required></label></fieldset>
    <fieldset><legend>Área pública de atendimento</legend>
      <p>Escolha um bairro, ponto comercial ou marcador aproximado. <strong>Não informe nem marque sua residência.</strong> A posição pública é reduzida para precisão aproximada.</p>
      <label>Cidade<input name="city" [(ngModel)]="form.instructor_city" (ngModelChange)="clearPublicLocation()" required></label>
      <label>UF<select name="uf" [(ngModel)]="form.instructor_uf" (ngModelChange)="clearPublicLocation()" required><option value="">Selecione</option>@for(uf of ufs;track uf){<option [value]="uf">{{uf}}</option>}</select></label>
      <label class="full">Bairro ou ponto público (opcional)<input name="publicLocationQuery" [(ngModel)]="publicLocationQuery" maxlength="120" placeholder="Ex.: Centro, Praça da Matriz ou Shopping"><small>Use somente referência pública. Não use rua, número ou endereço residencial.</small></label>
      <button class="button secondary location-search" type="button" (click)="findPublicLocation()" [disabled]="locating()||!form.instructor_city||!form.instructor_uf">{{locating()?'Buscando…':'Buscar área pública'}}</button>
      @if(locationResults().length>1){<div class="location-options" aria-label="Resultados da busca">@for(point of locationResults();track point.id){<button type="button" (click)="selectPublicLocation(point)">{{point.label}}</button>}</div>}
      @if(locationMessage()){<p class="location-result" role="status">{{locationMessage()}}</p>}
      <div #publicMap class="public-location-map" role="application" aria-label="Mapa para ajustar o marcador público aproximado"></div>
      <p class="map-help">Depois da busca, clique no mapa para ajustar o marcador dentro da região exibida. A coordenada salva é aproximada e não deve representar sua residência.</p>
      <label>Latitude pública aproximada<input name="latitude" [(ngModel)]="form.service_latitude" type="number" readonly></label>
      <label>Longitude pública aproximada<input name="longitude" [(ngModel)]="form.service_longitude" type="number" readonly></label>
      <label>Raio<select name="radius" [(ngModel)]="form.service_radius_km"><option [ngValue]="5">5 km</option><option [ngValue]="10">10 km</option><option [ngValue]="20">20 km</option><option [ngValue]="50">50 km</option></select></label>
      <label class="check"><input name="locationAuthorization" [(ngModel)]="form.service_location_authorized" type="checkbox" [disabled]="!hasPublicLocation()"> Autorizo a publicação desta área aproximada de atendimento.</label>
    </fieldset>
    <button class="button primary" [disabled]="sending()||onboardingForm.invalid">Concluir cadastro</button>@if(message()){<p role="alert">{{message()}}</p>}
  </form></section>`,
  styles: [`.onboarding{display:grid;gap:1rem}.onboarding label{display:grid;gap:.35rem;font-weight:700}.onboarding input,.onboarding select,.onboarding textarea{padding:.75rem;border:1px solid #bad4d1;border-radius:.7rem}.onboarding input[readonly]{background:#eef5f4;color:#345}.onboarding textarea{min-height:7rem}.onboarding fieldset{display:grid;grid-template-columns:1fr 1fr;gap:1rem;padding:1.2rem;border:1px solid #d6e5e3;border-radius:1rem}.onboarding fieldset>p,.onboarding fieldset legend,.check,.full,.location-search,.location-result,.location-options,.public-location-map,.map-help,.category-options{grid-column:1/-1}.photo-fieldset{grid-template-columns:1fr!important}.photo-fieldset .button{justify-self:start}.category-offer{display:grid;gap:.7rem;border:1px solid #d6e5e3;padding:1rem;border-radius:.7rem}.category-offer strong{color:#123f5f}.category-options{display:grid;grid-template-columns:repeat(5,1fr);gap:.5rem}.full small,.map-help{font-weight:400;color:#456}.check{grid-template-columns:auto 1fr!important}.location-options{display:grid;gap:.5rem}.location-options button{padding:.7rem;text-align:left;border:1px solid #bad4d1;border-radius:.65rem;background:#fff;color:#123f5f;cursor:pointer}.public-location-map{height:320px;border:1px solid #bad4d1;border-radius:.9rem;overflow:hidden}.map-help{margin-top:-.5rem}@media(max-width:650px){.onboarding fieldset{grid-template-columns:1fr}.category-options{grid-template-columns:1fr 1fr}.public-location-map{height:260px}}`],
})
export class RealInstructorOnboardingComponent implements AfterViewInit, OnDestroy {
  @ViewChild('publicMap') private publicMapElement?: ElementRef<HTMLDivElement>;
  readonly ufs = BRAZIL_UFS;
  readonly categoryOptions = ['A','B','C','D','E'];
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly search = inject(InstructorSearchProvider);
  private readonly zone = inject(NgZone);
  private map?: L.Map;
  private marker?: L.CircleMarker;
  private locationAnchor?: L.LatLng;
  sending = signal(false);
  locating = signal(false);
  message = signal('');
  locationMessage = signal('');
  locationResults = signal<GeocodingResult[]>([]);
  photoStatus = signal('');
  photoPreviewUrl = signal<string|null>(null);
  photoAvailable = signal<boolean|null>(null);
  photoMessage = signal('');
  photoSending = signal(false);
  selectedPhoto: File|null = null;
  photoAuthorized = false;
  offerDrafts: Record<string,{price_amount:number|null;duration_minutes:number|null}> = {B:{price_amount:null,duration_minutes:60}};
  publicLocationQuery = '';
  categories = ['B'];
  transmission = 'MANUAL';
  form: any = {instructor_display_name:'',bio:'',whatsapp:'',price_amount:null,duration_minutes:60,instructor_city:'',instructor_uf:'',service_latitude:null,service_longitude:null,service_radius_km:10,service_location_authorized:false,vehicle:{category:'B',make:'',model:'',year:new Date().getFullYear(),transmission:'MANUAL'}};

  constructor(){this.http.get<any>('/account/me/').subscribe({next:r=>{const instructor=r.instructor;if(!instructor){void this.router.navigateByUrl('/cadastro/instrutor');return}this.categories=instructor.categories?.length?instructor.categories:['B'];this.offerDrafts={};for(const category of this.categories){const saved=instructor.offers?.find((offer:{category:string})=>offer.category===category);this.offerDrafts[category]={price_amount:saved?Number(saved.price_amount):(this.categories.length===1&&instructor.price_amount?Number(instructor.price_amount):null),duration_minutes:saved?.duration_minutes??(this.categories.length===1?instructor.duration_minutes??60:null)}}this.transmission=instructor.transmission_options?.[0]||'MANUAL';this.form={...this.form,instructor_display_name:instructor.display_name||'',bio:instructor.bio||'',whatsapp:instructor.whatsapp||'',instructor_city:instructor.city||'',instructor_uf:instructor.uf||'',service_latitude:instructor.service_latitude??null,service_longitude:instructor.service_longitude??null,service_radius_km:instructor.service_radius_km??10,service_location_authorized:!!instructor.service_location_authorized,vehicle:{category:instructor.vehicle?.category||this.categories[0],make:instructor.vehicle?.make||'',model:instructor.vehicle?.model||'',year:instructor.vehicle?.year||new Date().getFullYear(),transmission:instructor.vehicle?.transmission||this.transmission,...(instructor.vehicle?.ownership_type?{ownership_type:instructor.vehicle.ownership_type}:{})}};if(this.hasPublicLocation()){this.locationMessage.set(`Área pública salva: ${this.form.instructor_city}/${this.form.instructor_uf}.`);this.locationAnchor=L.latLng(this.form.service_latitude,this.form.service_longitude);this.renderMapPoint()}},error:()=>void this.router.navigateByUrl('/entrar')})}

  ngAfterViewInit(){if(!this.publicMapElement)return;this.map=L.map(this.publicMapElement.nativeElement,{zoomControl:true}).setView([-14.2,-51.9],4);L.tileLayer('/api/v1/map/tiles/{z}/{x}/{y}.png',{attribution:'&copy; MapTiler &copy; OpenStreetMap contributors',maxZoom:19}).addTo(this.map);this.map.on('click',event=>this.zone.run(()=>this.selectMapPoint(event.latlng)));this.renderMapPoint();setTimeout(()=>this.map?.invalidateSize(),0)}
  ngOnDestroy(){this.map?.remove();this.map=undefined;this.marker=undefined}

  clearPublicLocation(){this.form.service_latitude=null;this.form.service_longitude=null;this.locationMessage.set('');this.locationResults.set([]);this.locationAnchor=undefined;if(this.marker&&this.map)this.map.removeLayer(this.marker);this.marker=undefined}

  findPublicLocation(){if(!this.form.instructor_city||!this.form.instructor_uf)return;this.locating.set(true);this.locationMessage.set('');this.locationResults.set([]);const expectedUf=String(this.form.instructor_uf).toUpperCase();const query=[this.publicLocationQuery.trim(),this.form.instructor_city,expectedUf,'Brasil'].filter(Boolean).join(', ');this.search.geocode(query,5).subscribe({next:response=>{this.locating.set(false);const expectedCity=this.normalize(this.form.instructor_city);const points=response.results.filter(item=>item.uf===expectedUf&&(this.normalize(item.city)===expectedCity||this.normalize(item.label).includes(expectedCity)));if(!points.length){this.clearPublicLocation();this.locationMessage.set('Área pública não encontrada nessa cidade/UF. Revise a referência e tente novamente.');return}this.locationResults.set(points);this.selectPublicLocation(points[0]);if(points.length>1)this.locationMessage.set(`Selecionamos ${points[0].label}. Você pode escolher outro resultado abaixo ou ajustar no mapa.`)},error:e=>{this.locating.set(false);this.clearPublicLocation();this.locationMessage.set(e?.error?.detail||'Não foi possível buscar a área agora. Tente novamente.')}})}

  selectPublicLocation(point:GeocodingResult){this.locationAnchor=L.latLng(point.latitude,point.longitude);this.setPublicCoordinates(point.latitude,point.longitude,`Área pública selecionada: ${point.label}.`)}

  private selectMapPoint(point:L.LatLng){if(!this.locationAnchor){this.locationMessage.set('Busque primeiro a cidade, bairro ou ponto público antes de ajustar o mapa.');return}if(this.locationAnchor.distanceTo(point)>50000){this.locationMessage.set('O marcador deve permanecer próximo da área pública encontrada. Refaça a busca para outra região.');return}this.setPublicCoordinates(point.lat,point.lng,'Marcador público aproximado ajustado no mapa.')}

  private setPublicCoordinates(latitude:number,longitude:number,message:string){this.form.service_latitude=this.approximate(latitude);this.form.service_longitude=this.approximate(longitude);this.locationMessage.set(message);this.renderMapPoint()}
  private approximate(value:number){return Math.round(value*100)/100}
  private normalize(value:string){return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().toLocaleLowerCase('pt-BR')}
  hasPublicLocation(){return this.form.service_latitude!==null&&this.form.service_longitude!==null}
  private renderMapPoint(){if(!this.map||!this.hasPublicLocation())return;const point=L.latLng(this.form.service_latitude,this.form.service_longitude);if(this.marker)this.marker.setLatLng(point);else this.marker=L.circleMarker(point,{radius:11,color:'#fff',weight:3,fillColor:'#f97316',fillOpacity:1,className:'public-location-pin'}).addTo(this.map);this.map.setView(point,13)}

  toggleCategory(category:string){this.categories=this.categories.includes(category)?this.categories.filter(value=>value!==category):[...this.categories,category].sort();if(this.categories.includes(category)&&!this.offerDrafts[category])this.offerDrafts[category]={price_amount:null,duration_minutes:null}}

  loadPhotoStatus(){this.http.get<{upload_available:boolean;latest_status:string|null;private_preview_url:string|null}>('/instructor/profile-photo/').subscribe({next:state=>{this.photoAvailable.set(state.upload_available);this.photoStatus.set(state.latest_status||'Nenhuma foto enviada');this.photoPreviewUrl.set(state.private_preview_url)},error:()=>this.photoMessage.set('Não foi possível consultar a situação da foto.')})}

  photoStatusLabel(value:string){return ({PENDING:'Aguardando revisão',APPROVED:'Aprovada',REJECTED:'Rejeitada',REPLACEMENT_REQUESTED:'Substituição solicitada'} as Record<string,string>)[value]||value}

  selectPhoto(event:Event){const file=(event.target as HTMLInputElement).files?.[0]||null;this.selectedPhoto=null;this.photoMessage.set('');if(!file)return;if(!['image/jpeg','image/png'].includes(file.type)||file.size===0||file.size>5*1024*1024){this.photoMessage.set('Selecione JPEG ou PNG de até 5 MB.');return}this.selectedPhoto=file}

  uploadPhoto(){if(!this.selectedPhoto||!this.photoAuthorized)return;this.photoSending.set(true);this.photoMessage.set('');const payload=new FormData();payload.append('file',this.selectedPhoto);payload.append('publication_authorized','true');this.http.post<{upload_available:boolean;latest_status:string;private_preview_url:string}>('/instructor/profile-photo/',payload).subscribe({next:state=>{this.photoSending.set(false);this.selectedPhoto=null;this.photoStatus.set(state.latest_status);this.photoPreviewUrl.set(state.private_preview_url);this.photoMessage.set('Foto recebida em armazenamento privado. Aguarde a revisão antes da exibição pública.')},error:e=>{this.photoSending.set(false);this.photoMessage.set(e?.error?.file?.[0]||'Não foi possível enviar a foto. Tente novamente.')}})}

  submit(valid:boolean|null=true){if(!valid){this.message.set('Revise os campos obrigatórios e o formato do WhatsApp.');return}if(!this.categories.length){this.message.set('Selecione pelo menos uma categoria.');return}const offers=this.categories.map(category=>({category,...this.offerDrafts[category]}));if(offers.some(offer=>!offer.price_amount||offer.price_amount<1||!offer.duration_minutes||offer.duration_minutes<30||offer.duration_minutes>240)){this.message.set('Informe preço e duração válidos separadamente para cada categoria.');return}this.sending.set(true);this.message.set('');const {price_amount,duration_minutes,...profileFields}=this.form;const payload={...profileFields,categories:this.categories,offers,transmission_options:[this.transmission],vehicle:{...this.form.vehicle,category:this.categories[0],transmission:this.transmission}};if(!this.hasPublicLocation()){delete payload.service_latitude;delete payload.service_longitude;payload.service_location_authorized=false}this.http.patch('/account/me/',payload).subscribe({next:()=>void this.router.navigateByUrl('/profissional/instrutor/status'),error:e=>{this.sending.set(false);this.message.set(this.errorMessage(e))}})}

  private errorMessage(error:any){const payload=error?.error?.error;const messages=this.detailMessages(payload?.details);if(messages.length)return messages.join(' ');return payload?.message||error?.error?.detail||'Não foi possível concluir. Revise os dados informados.'}
  private detailMessages(value:any,field='Cadastro'):string[]{const labels:Record<string,string>={instructor_display_name:'Nome público',bio:'Apresentação',categories:'Categorias',transmission_options:'Transmissão',whatsapp:'WhatsApp',price_amount:'Preço por aula',duration_minutes:'Duração',instructor_city:'Cidade',instructor_uf:'UF',service_area:'Área pública de atendimento',service_latitude:'Latitude pública',service_longitude:'Longitude pública',service_radius_km:'Raio',service_location_authorized:'Autorização da área pública',vehicle:'Veículo',category:'Categoria',make:'Marca',model:'Modelo',year:'Ano',transmission:'Transmissão',ownership_type:'Disponibilidade do veículo',non_field_errors:'Cadastro'};if(Array.isArray(value))return value.flatMap(item=>this.detailMessages(item,field));if(value&&typeof value==='object')return Object.entries(value).flatMap(([key,item])=>this.detailMessages(item,labels[key]||key));if(typeof value==='string')return [`${field}: ${value}`];return []}
}
