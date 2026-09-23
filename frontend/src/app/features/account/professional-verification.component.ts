import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

type VerificationState = {
  status: 'DRAFT'|'SUBMITTED'|'UNDER_REVIEW'|'VERIFIED'|'REJECTED';
  cpf_masked: string;
  submitted_at: string|null;
  review_started_at: string|null;
  decided_at: string|null;
  message: string;
  can_edit: boolean;
  documents_enabled?: boolean;
  requirements?: {id:string;label:string;required:boolean}[];
  documents?: {id:string;requirement_id:string;scan_status:string;status:string}[];
};

@Component({
  selector: 'app-professional-verification',
  imports: [FormsModule, RouterLink],
  template: `<section class="page narrow">
    <header class="page-head"><div><p class="eyebrow">Área privada do instrutor</p><h1>Verificação profissional</h1></div></header>
    @if(state(); as current){
      <article class="notice">
        <h2>{{label(current.status)}}</h2>
        @if(current.cpf_masked){<p>CPF informado: <strong>{{current.cpf_masked}}</strong></p>}
        @if(current.message){<p>{{current.message}}</p>}
        @if(current.can_edit){
          <form (ngSubmit)="submit()">
            <h3>1. Identificação privada</h3>
            <label>CPF
              <input name="cpf" inputmode="numeric" autocomplete="off" maxlength="14" [(ngModel)]="cpf" (ngModelChange)="formatCpf()" placeholder="000.000.000-00" required>
            </label>
            <p class="privacy">O CPF será usado exclusivamente para identificação e verificação profissional. Ele não será exibido no perfil público.</p>
            <h3>2. Dados profissionais</h3>
            <p>Os dados profissionais são os informados em <a routerLink="/profissional/instrutor/onboarding">Editar perfil</a>.</p>
            @if(current.documents_enabled){
              <h3>3. Documentos solicitados para sua UF e categoria</h3>
              @if(!current.requirements?.length){<p>Nenhum documento foi configurado para esta solicitação. Não envie documentos desnecessários.</p>}
              @for(requirement of current.requirements || []; track requirement.id){
                <div class="document-row">
                  <strong>{{requirement.label}}{{requirement.required?' (obrigatório)':''}}</strong>
                  @if(documentFor(requirement.id); as document){
                    <span>Antimalware: {{document.scan_status}}</span>
                    <button type="button" [disabled]="sending" (click)="removeDocument(document.id)">Remover</button>
                  } @else {
                    <input type="file" accept=".pdf,.jpg,.jpeg,.png" [disabled]="sending || !current.cpf_masked" (change)="uploadDocument(requirement.id,$event)" aria-label="Enviar {{requirement.label}}">
                  }
                </div>
              }
              <p class="privacy">Salve primeiro o CPF. Arquivos aceitos: PDF, JPEG ou PNG, até 5 MB. Documentos não são publicados.</p>
            } @else {<p>Documentos ainda não estão sendo solicitados nesta etapa.</p>}
            <h3>4. Revisão e envio</h3>
            <label class="consent"><input type="checkbox" name="confirmed" [(ngModel)]="confirmed"> Confirmo que o CPF é meu e autorizo seu uso para esta verificação.</label>
            <button class="button secondary" type="button" [disabled]="sending || !confirmed" (click)="saveDraft()">Salvar rascunho</button>
            <button class="button primary" [disabled]="sending || !confirmed">Enviar solicitação de verificação</button>
          </form>
        } @else {
          <p>Sua solicitação está protegida contra reenvio. Acompanhe o andamento nesta página.</p>
        }
        @if(error()){<p class="error" role="alert">{{error()}}</p>}
        <a routerLink="/profissional/instrutor/status">Voltar ao status do cadastro</a>
      </article>
    } @else if(error()) {
      <article class="notice"><p class="error" role="alert">{{error()}}</p><a class="button primary" routerLink="/entrar">Entrar com a conta do instrutor</a></article>
    } @else {<p>Carregando…</p>}
  </section>`,
  styles: [`.notice{display:grid;gap:1rem;padding:1.5rem;border:1px solid #d6e5e3;border-radius:1rem;background:#fff}.notice form,.notice label{display:grid;gap:.5rem}.notice input{min-height:3rem;padding:.7rem;border:1px solid #bfd5d2;border-radius:.7rem}.notice .consent{display:flex;align-items:flex-start}.notice .consent input{min-height:auto;margin-top:.25rem}.privacy{font-size:.92rem}.error{color:#9a302c}.document-row{display:grid;gap:.5rem;padding:.8rem;border:1px solid #d6e5e3;border-radius:.5rem}`]
})
export class ProfessionalVerificationComponent {
  private http=inject(HttpClient);
  state=signal<VerificationState|undefined>(undefined);
  error=signal(''); cpf=''; confirmed=false; sending=false;

  constructor(){this.load()}
  load(){this.http.get<VerificationState>('/instructor/verification/').subscribe({next:value=>this.state.set(value),error:()=>this.error.set('Não foi possível carregar a verificação profissional.')})}
  label(value:string){return value==='SUBMITTED'?'Solicitação enviada':value==='UNDER_REVIEW'?'Em análise':value==='VERIFIED'?'Verificação concluída':value==='REJECTED'?'Solicitação não concluída':'Nova solicitação'}
  formatCpf(){const digits=this.cpf.replace(/\D/g,'').slice(0,11);this.cpf=digits.replace(/^(\d{3})(\d)/,'$1.$2').replace(/^(\d{3})\.(\d{3})(\d)/,'$1.$2.$3').replace(/(\d{3})(\d{1,2})$/,'$1-$2')}
  private validCpf(){const d=this.cpf.replace(/\D/g,'');if(d.length!==11||/^([0-9])\1+$/.test(d))return false;for(let size=9;size<=10;size++){let total=0;for(let i=0;i<size;i++)total+=Number(d[i])*(size+1-i);let check=(total*10)%11;if(check===10)check=0;if(check!==Number(d[size]))return false}return true}
  documentFor(requirementId:string){return this.state()?.documents?.find(document=>document.requirement_id===requirementId)}
  saveDraft(){
    this.error.set('');
    if(!this.validCpf()){this.error.set('Informe um CPF válido.');return}
    if(!this.confirmed){this.error.set('Confirme a autorização para continuar.');return}
    this.sending=true;
    this.http.patch<VerificationState>('/instructor/verification/',{cpf:this.cpf}).subscribe({next:value=>{this.sending=false;this.cpf='';this.state.set(value)},error:error=>this.fail(error)});
  }
  uploadDocument(requirementId:string,event:Event){
    const file=(event.target as HTMLInputElement).files?.[0];
    if(!file)return;
    this.sending=true;this.error.set('');
    const data=new FormData();data.append('requirement_id',requirementId);data.append('file',file);
    this.http.post<VerificationState>('/instructor/verification/documents/',data).subscribe({next:value=>{this.sending=false;this.state.set(value)},error:error=>this.fail(error)});
  }
  removeDocument(id:string){
    this.sending=true;this.error.set('');
    this.http.delete('/instructor/verification/documents/'+id+'/').subscribe({next:()=>{this.sending=false;this.load()},error:error=>this.fail(error)});
  }
  submit(){
    this.error.set('');
    if(!this.validCpf() && !(this.state()?.cpf_masked && !this.cpf)){
      this.error.set('Informe um CPF válido.');return
    }
    if(!this.confirmed){this.error.set('Confirme a autorização para continuar.');return}
    this.sending=true;
    const send=()=>this.http.post<VerificationState>('/instructor/verification/submit/',{}).subscribe({next:value=>{this.sending=false;this.cpf='';this.state.set(value)},error:error=>this.fail(error)});
    if(this.cpf){this.http.patch<VerificationState>('/instructor/verification/',{cpf:this.cpf}).subscribe({next:send,error:error=>this.fail(error)})}
    else{send()}
  }
  private fail(error:HttpErrorResponse){
    this.sending=false;
    const body=error.error||{};
    const detail=body.file||body.cpf||body.detail;
    this.error.set((Array.isArray(detail)?detail[0]:detail)||'Não foi possível enviar a solicitação.');
  }
}
