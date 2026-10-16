import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { ProfessionalVerificationComponent } from './professional-verification.component';

describe('ProfessionalVerificationComponent',()=>{
  beforeEach(()=>TestBed.configureTestingModule({imports:[ProfessionalVerificationComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));
  it('offers voluntary documents with zero UF requirements and friendly security labels',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'DRAFT',cpf_masked:'***25',can_edit:true,document_upload_available:true,requirements:[],document_types:[{value:'PROFESSIONAL_CREDENTIAL',label:'Credencial profissional'}],documents:[{id:'one',requirement_id:null,label:'Credencial profissional',original_name:'teste.pdf',scan_status:'CLEAN'}]});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Adicionar documento');
    expect(fixture.nativeElement.textContent).toContain('Pronto');
    expect(fixture.nativeElement.textContent).not.toContain('CLEAN');
    expect(fixture.nativeElement.textContent).not.toContain('Nenhum documento foi configurado');
  });
  it('shows applicant blockers separately from the human UF decision',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'DRAFT',cpf_masked:'***.***.***-25',can_edit:true,document_upload_available:true,requirements:[],documents:[],submission_blockers:['Anexe sua CNH selecionando o tipo de documento CNH.']});
    fixture.detectChanges();
    const content=fixture.nativeElement.textContent;
    expect(content).toContain('Pendências antes do envio');
    expect(content).toContain('Anexe sua CNH');
    expect(content).toContain('UF ainda pendente não impede o cadastro');
  });
  it('shows the 24 to 48 hour estimate only for a submitted request',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'SUBMITTED',cpf_masked:'***.***.***-25',can_edit:false,documents:[]});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('24 a 48 horas');
    expect(fixture.nativeElement.textContent).toContain('A aprovação não é automática');
  });
  it('requests explicit visual-review confirmation for a private CNH photo upload',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'DRAFT',cpf_masked:'***.***.***-25',can_edit:true,document_upload_available:true,visual_review_available:true,requirements:[],document_types:[],documents:[]});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Não há reconhecimento facial automático');
    const input=fixture.nativeElement.querySelector('input[aria-label="Capturar ou escolher foto com a CNH"]') as HTMLInputElement;
    expect(input.disabled).toBeTrue();
    fixture.componentInstance.manualVisualReviewAuthorized=true;
    const file=new File(['\xff\xd8\xff\xe0photo'],'visual.jpg',{type:'image/jpeg'});
    fixture.componentInstance.uploadDocument(null,{target:{files:[file],value:'visual.jpg'}} as unknown as Event,'SELFIE_WITH_CNH');
    const request=http.expectOne('/instructor/verification/documents/');
    expect(request.request.body.get('document_type')).toBe('SELFIE_WITH_CNH');
    expect(request.request.body.get('manual_identity_review_authorized')).toBe('true');
    request.flush({status:'DRAFT',cpf_masked:'***.***.***-25',can_edit:true,document_upload_available:true,visual_review_available:true,documents:[{id:'photo',label:'Foto com CNH para conferência visual',original_name:'visual.jpg',scan_status:'CLEAN'}]});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Foto com CNH para conferência visual');
  });
  it('does not send an invalid CPF',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'DRAFT',cpf_masked:'',submitted_at:null,review_started_at:null,decided_at:null,message:'',can_edit:true});
    fixture.componentInstance.cpf='111.111.111-11';fixture.componentInstance.confirmed=true;fixture.componentInstance.submit();
    http.expectNone('/instructor/verification/');expect(fixture.componentInstance.error()).toContain('CPF válido');
  });
  it('saves and submits a valid CPF without retaining it',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'DRAFT',cpf_masked:'',submitted_at:null,review_started_at:null,decided_at:null,message:'',can_edit:true});
    fixture.componentInstance.cpf='529.982.247-25';fixture.componentInstance.confirmed=true;fixture.componentInstance.submit();
    const save=http.expectOne('/instructor/verification/');
    expect(save.request.body).toEqual({cpf:'529.982.247-25'});
    save.flush({status:'DRAFT'});
    http.expectOne('/instructor/verification/submit/').flush({status:'SUBMITTED',cpf_masked:'***.***.***-25',submitted_at:'x',review_started_at:null,decided_at:null,message:'',can_edit:false});
    expect(fixture.componentInstance.cpf).toBe('');
  });
  it('shows a useful error instead of loading forever',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({detail:'Forbidden'},{status:403,statusText:'Forbidden'});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Não foi possível carregar a verificação profissional.');
    expect(fixture.nativeElement.textContent).not.toContain('Carregando');
  });
  it('opens a supplement without asking to edit the previously verified CPF',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'VERIFIED',cpf_masked:'***.***.***-25',can_edit:false,can_start_supplement:true,document_upload_available:true,documents:[]});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Complementar documentos');
    fixture.componentInstance.startSupplement();
    const opened=http.expectOne('/instructor/verification/supplement/');
    expect(opened.request.method).toBe('POST');
    opened.flush({status:'DRAFT',cpf_masked:'***.***.***-25',can_edit:true,is_supplement:true,document_upload_available:true,document_types:[{value:'PROFESSIONAL_CREDENTIAL',label:'Credencial profissional'}],documents:[]});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Adicionar documento');
    expect(fixture.nativeElement.textContent).toContain('Enviar documentos para análise');
    expect(fixture.nativeElement.querySelector('input[name="cpf"]')).toBeNull();
    expect(fixture.nativeElement.textContent).not.toContain('Salvar rascunho');
  });
});
