import { HttpClient } from "@angular/common/http";
import { DatePipe } from "@angular/common";
import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterLink } from "@angular/router";

type OwnAccount = {
  email: string;
  email_editable: boolean;
  phone: string;
  birth_date: string | null;
  roles: string[];
  student?: {
    display_name: string;
    city: string;
    uf: string;
    intended_category: string;
    preferred_transmission: string;
  };
  instructor?: {
    display_name: string;
    bio: string;
    categories: string[];
    transmission_options: string[];
    profile_status: string;
    verification_status: string;
    publication_status: string;
    whatsapp: string;
    price_amount: string;
    duration_minutes: number | null;
    city: string;
    uf: string;
    vehicle: any;
  };
};

@Component({
  selector: "app-account-nav",
  imports: [RouterLink],
  template: `<nav class="account-nav" aria-label="Menu da conta">
    <a routerLink="/minha-conta">Meus dados</a
    ><a routerLink="/minha-conta/privacidade">Privacidade e meus dados</a
    ><a routerLink="/privacidade">Política de Privacidade</a>
  </nav>`,
  styles: [
    `
      .account-nav {
        display: flex;
        gap: 0.6rem;
        overflow: auto;
        margin-bottom: 1.5rem;
      }
      .account-nav a {
        white-space: nowrap;
        padding: 0.7rem 0.9rem;
        border-radius: 999px;
        background: #e8f4f2;
        color: #084e62;
        font-weight: 750;
        text-decoration: none;
      }
    `,
  ],
})
export class AccountNavComponent {}

@Component({
  selector: "app-my-account",
  imports: [FormsModule, AccountNavComponent],
  template: ` <section class="page narrow">
    <app-account-nav />
    <header class="page-head">
      <div>
        <p class="eyebrow">Sua conta</p>
        <h1>Meus dados</h1>
        <p>
          Você controla os dados cadastrais e comerciais permitidos. Estados de
          verificação, publicação, papéis e plano não são editáveis aqui.
        </p>
      </div>
    </header>
    @if (model(); as m) {
      <form class="account-form" (ngSubmit)="save()">
        <fieldset>
          <legend>Dados pessoais</legend>
          <label
            >E-mail<input [value]="m.email" disabled /><small
              >Alterações de e-mail exigem um fluxo de verificação e ainda não
              estão disponíveis.</small
            ></label
          ><label
            >Telefone<input
              name="phone"
              [(ngModel)]="m.phone"
              inputmode="tel"
              placeholder="5511999999999" /></label
          ><label
            >Data de nascimento<input
              name="birth_date"
              [(ngModel)]="m.birth_date"
              type="date"
          /></label>
        </fieldset>
        @if (m.student) {
          <fieldset>
            <legend>Dados do aluno</legend>
            <label
              >Nome<input
                name="student_name"
                [(ngModel)]="m.student.display_name"
                maxlength="120" /></label
            ><label
              >Cidade<input
                name="student_city"
                [(ngModel)]="m.student.city"
                maxlength="100" /></label
            ><label
              >UF<input
                name="student_uf"
                [(ngModel)]="m.student.uf"
                maxlength="2" /></label
            ><label
              >Categoria pretendida<input
                name="student_category"
                [(ngModel)]="m.student.intended_category"
                maxlength="8" /></label
            ><label
              >Transmissão<select
                name="student_transmission"
                [(ngModel)]="m.student.preferred_transmission"
              >
                <option value="INDIFFERENT">Indiferente</option>
                <option value="MANUAL">Manual</option>
                <option value="AUTOMATIC">Automática</option>
              </select></label
            >
          </fieldset>
        }
        @if (m.instructor) {
          <fieldset>
            <legend>Perfil do instrutor</legend>
            <p class="notice">
              Alterar categorias, transmissão ou veículo envia o cadastro para
              nova revisão e retira a publicação até nova aprovação.
            </p>
            <label
              >Nome público<input
                name="instructor_name"
                [(ngModel)]="m.instructor.display_name"
                maxlength="120" /></label
            ><label
              >Apresentação<textarea
                name="bio"
                [(ngModel)]="m.instructor.bio"
                maxlength="2000"
              ></textarea></label
            ><label
              >WhatsApp profissional<input
                name="whatsapp"
                [(ngModel)]="m.instructor.whatsapp"
                placeholder="+5551999999999" /></label
            ><label
              >Preço por aula<input
                name="price"
                [(ngModel)]="m.instructor.price_amount"
                type="number"
                min="1"
                step="0.01" /></label
            ><label
              >Duração comercial em minutos<input
                name="duration"
                [(ngModel)]="m.instructor.duration_minutes"
                type="number"
                min="30"
                max="240" /></label
            ><label
              >Categorias, separadas por vírgula<input
                name="categories"
                [ngModel]="m.instructor.categories.join(', ')"
                (ngModelChange)="setCategories($event)" /></label
            ><label
              >Transmissões, separadas por vírgula<input
                name="transmissions"
                [ngModel]="m.instructor.transmission_options.join(', ')"
                (ngModelChange)="setTransmissions($event)"
            /></label>
          </fieldset>
        }
        <button class="button primary" [disabled]="saving()">
          Salvar alterações
        </button>
        @if (message()) {
          <p class="feedback" role="status">{{ message() }}</p>
        }
      </form>
    } @else {
      <p>Carregando…</p>
    }
  </section>`,
  styles: [
    `
      .account-form {
        display: grid;
        gap: 1rem;
      }
      .account-form fieldset {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        padding: 1.3rem;
        border: 1px solid #d6e5e3;
        border-radius: 1rem;
        background: #fff;
      }
      .account-form legend {
        padding: 0.4rem;
        font-size: 1.15rem;
        font-weight: 800;
      }
      .account-form label {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        font-weight: 700;
      }
      .account-form input,
      .account-form select,
      .account-form textarea {
        padding: 0.75rem;
        border: 1px solid #bad4d1;
        border-radius: 0.7rem;
      }
      .account-form textarea {
        min-height: 7rem;
      }
      .account-form small {
        font-weight: 400;
      }
      .notice,
      .feedback {
        grid-column: 1/-1;
        padding: 0.8rem;
        border-radius: 0.7rem;
        background: #fff3e9;
      }
      @media (max-width: 650px) {
        .account-form fieldset {
          grid-template-columns: 1fr;
        }
      }
    `,
  ],
})
export class MyAccountComponent {
  private http = inject(HttpClient);
  model = signal<OwnAccount | undefined>(undefined);
  saving = signal(false);
  message = signal("");
  constructor() {
    this.http
      .get<OwnAccount>("/account/me/")
      .subscribe((v) => this.model.set(v));
  }
  setCategories(value: string) {
    const m = this.model();
    if (m?.instructor)
      m.instructor.categories = value
        .split(",")
        .map((v) => v.trim().toUpperCase())
        .filter(Boolean);
  }
  setTransmissions(value: string) {
    const m = this.model();
    if (m?.instructor)
      m.instructor.transmission_options = value
        .split(",")
        .map((v) => v.trim().toUpperCase())
        .filter(Boolean);
  }
  save() {
    const m = this.model();
    if (!m) return;
    const payload: any = { phone: m.phone, birth_date: m.birth_date };
    if (m.student)
      Object.assign(payload, {
        student_display_name: m.student.display_name,
        student_city: m.student.city,
        student_uf: m.student.uf,
        intended_category: m.student.intended_category,
        preferred_transmission: m.student.preferred_transmission,
      });
    if (m.instructor)
      Object.assign(payload, {
        instructor_display_name: m.instructor.display_name,
        bio: m.instructor.bio,
        categories: m.instructor.categories,
        transmission_options: m.instructor.transmission_options,
        whatsapp: m.instructor.whatsapp,
        price_amount: m.instructor.price_amount,
        duration_minutes: m.instructor.duration_minutes,
      });
    this.saving.set(true);
    this.message.set("");
    this.http.patch<OwnAccount>("/account/me/", payload).subscribe({
      next: (v) => {
        this.model.set(v);
        this.saving.set(false);
        this.message.set("Dados atualizados com segurança.");
      },
      error: (e) => {
        this.saving.set(false);
        this.message.set(
          e?.error?.detail ||
            "Não foi possível salvar. Revise os dados e tente novamente.",
        );
      },
    });
  }
}

type PrivacyRequestRow = {
  id: string;
  request_type: string;
  status: string;
  details: string;
  requested_at: string;
};
@Component({
  selector: "app-account-privacy",
  imports: [DatePipe, FormsModule, AccountNavComponent],
  template: `<section class="page narrow"><app-account-nav/><header class="page-head"><div><p class="eyebrow">LGPD</p><h1>Privacidade e meus dados</h1><p>Solicitações passam por análise segura. Exclusão não apaga imediatamente registros que precisem ser preservados por obrigação legal, segurança, prevenção a fraude ou exercício regular de direitos.</p></div></header><form class="privacy-card" (ngSubmit)="submit()"><label>O que você deseja solicitar?<select name="type" [(ngModel)]="requestType"><option value="ACCESS">Acessar meus dados</option><option value="CORRECTION">Corrigir meus dados</option><option value="DELETION">Solicitar exclusão da conta</option><option value="PORTABILITY">Solicitar portabilidade, quando aplicável</option><option value="CONSENT_REVOCATION">Revogar consentimento específico</option><option value="OTHER">Solicitar informações</option></select></label><label>Detalhes<textarea name="details" [(ngModel)]="details" maxlength="2000"></textarea></label><button class="button primary">Enviar solicitação</button>@if(message()){<p role="status">{{message()}}</p>}</form><h2>Minhas solicitações</h2><div class="requests">@for(row of rows();track row.id){<article><strong>{{label(row.request_type)}}</strong><span>{{row.status}}</span><small>{{row.requested_at|date:'dd/MM/yyyy HH:mm'}}</small></article>}@empty{<p>Nenhuma solicitação registrada.</p>}</div><p>Canal de privacidade: <a href="mailto:focusgtba@gmail.com">focusgtba@gmail.com</a>. Não envie CPF, CNH ou documentos sensíveis por e-mail.</p></section>`,
  styles: [
    `
      .privacy-card {
        display: grid;
        gap: 1rem;
        padding: 1.3rem;
        border: 1px solid #d6e5e3;
        border-radius: 1rem;
        background: #fff;
      }
      .privacy-card label {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        font-weight: 700;
      }
      .privacy-card select,
      .privacy-card textarea {
        padding: 0.75rem;
        border: 1px solid #bad4d1;
        border-radius: 0.7rem;
      }
      .privacy-card textarea {
        min-height: 8rem;
      }
      .requests article {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 0.4rem;
        padding: 1rem;
        margin: 0.6rem 0;
        border: 1px solid #d6e5e3;
        border-radius: 0.8rem;
        background: #fff;
      }
      .requests small {
        grid-column: 1/-1;
      }
    `,
  ],
})
export class AccountPrivacyComponent {
  private http = inject(HttpClient);
  rows = signal<PrivacyRequestRow[]>([]);
  requestType = "ACCESS";
  details = "";
  message = signal("");
  constructor() {
    this.load();
  }
  load() {
    this.http
      .get<PrivacyRequestRow[]>("/privacy/requests/")
      .subscribe((v) => this.rows.set(v));
  }
  submit() {
    this.http
      .post<PrivacyRequestRow>("/privacy/requests/", {
        request_type: this.requestType,
        details: this.details,
      })
      .subscribe({
        next: () => {
          this.details = "";
          this.message.set("Solicitação registrada para análise.");
          this.load();
        },
        error: () =>
          this.message.set("Não foi possível registrar a solicitação."),
      });
  }
  label(v: string) {
    return (
      (
        {
          ACCESS: "Acesso",
          CORRECTION: "Correção",
          DELETION: "Exclusão",
          PORTABILITY: "Portabilidade",
          CONSENT_REVOCATION: "Revogação de consentimento",
          OTHER: "Informações",
        } as any
      )[v] || v
    );
  }
}

@Component({
  selector: "app-privacy-policy",
  template: `<article class="page narrow policy"><p class="eyebrow">Versão 2026-09-16 · última atualização 16/09/2026</p><h1>Política de Privacidade e Proteção de Dados</h1><h2>InstrutorProCNH</h2><p>Esta política descreve o tratamento realizado pelas funcionalidades atualmente disponíveis. A operação é identificada pelo CNPJ 10.280.826/0001-05. Dados empresariais ainda não confirmados não são publicados.</p><h2>Dados tratados e finalidades</h2><p>Tratamos dados cadastrais de alunos e instrutores para criar contas, manter perfis, autenticar acesso, prestar suporte e proteger a plataforma. Dados comerciais do instrutor incluem área autorizada de atendimento, categorias, transmissão, veículo, preço e duração comercial da aula. Documentos de credenciamento, veículo e arquivos privados não são exibidos publicamente.</p><h2>Localização</h2><p>O GPS somente é solicitado após ação explícita. A busca manual por cidade, bairro ou CEP permanece disponível. Não publicamos endereço residencial nem localização individual de alunos; perfis usam região de atendimento autorizada e dados minimizados.</p><h2>WhatsApp e métricas</h2><p>Registramos o evento de intenção de contato antes de redirecionar ao WhatsApp. Não lemos nem armazenamos o conteúdo das conversas e o clique não é tratado como venda. Métricas do marketplace incluem buscas, visualizações de perfil e cliques de contato.</p><h2>Cookies, sessões e registros técnicos</h2><p>Cookies necessários mantêm sessão autenticada e proteção CSRF. Registros técnicos, identificadores de requisição e eventos de auditoria apoiam segurança, diagnóstico e responsabilização. Não usamos consentimento como base universal; a base aplicável depende da finalidade e do contexto.</p><h2>Compartilhamento e segurança</h2><p>Dados são compartilhados somente com provedores necessários à infraestrutura e às funcionalidades habilitadas, sob controles contratuais e de acesso aplicáveis. Aplicamos autenticação, autorização por objeto, minimização, registros de auditoria e armazenamento privado. Nenhuma medida elimina integralmente os riscos.</p><h2>Retenção e exclusão</h2><p>Conservamos dados pelo tempo necessário às finalidades e às obrigações aplicáveis. Uma solicitação de exclusão inicia análise: registros podem ser preservados quando necessários por obrigação legal ou regulatória, segurança, prevenção a fraude ou exercício regular de direitos. Não realizamos exclusão física indiscriminada.</p><h2>Direitos dos titulares</h2><p>Na área “Privacidade e meus dados”, titulares podem solicitar acesso, correção, exclusão, informações, portabilidade quando aplicável e revogação de consentimento específico. Não envie CPF, CNH ou documentos por e-mail.</p><h2>Menores</h2><p>O cadastro operacional de menores permanece bloqueado enquanto não houver política e mecanismos específicos aprovados.</p><h2>Contato</h2><p>Canal inicial de privacidade: <a href="mailto:focusgtba@gmail.com">focusgtba@gmail.com</a>.</p></article>`,
  styles: [
    `
      .policy {
        line-height: 1.65;
      }
      .policy h1 {
        font-size: clamp(2.2rem, 5vw, 3.8rem);
        line-height: 1.05;
      }
      .policy h2 {
        margin-top: 2rem;
        color: #123e64;
      }
      .policy p {
        color: #3f5e6e;
      }
    `,
  ],
})
export class PrivacyPolicyComponent {}
