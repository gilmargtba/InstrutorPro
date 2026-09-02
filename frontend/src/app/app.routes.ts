import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { ClinicDemoComponent, DemandDemoComponent, InstructorDashboardComponent, InstructorProfileComponent, JourneyComponent, MatchingComponent, ProfessionalEntryComponent, ServiceDiscoveryComponent, StudentDemandComponent, StudentRequestComponent } from './features/demo/demo-pages.component';
import { InstructorMapComponent } from './features/demo/instructor-map.component';
import { InstructorNationalMapComponent } from './features/demo/instructor-national-map.component';
import { InstructorOnboardingComponent } from './features/demo/instructor-onboarding.component';
import { StudentMarketplaceComponent } from './features/demo/student-marketplace.component';
import { InstructorEntryComponent, InstructorStatusComponent, LoginComponent, StudentEntryComponent } from './features/demo/marketplace-entry.component';

export const routes: Routes = [
  { path:'', component:HomeComponent, title:'InstrutorProcnh — Sua jornada para a CNH' },
  { path:'aluno', component:StudentEntryComponent, title:'Aluno — InstrutorProcnh' },
  { path:'cadastro/aluno', component:StudentMarketplaceComponent, title:'Criar conta de aluno — InstrutorProcnh' },
  { path:'entrar', component:LoginComponent, title:'Entrar — InstrutorProcnh' },
  { path:'aluno/jornada', component:JourneyComponent, title:'Minha Jornada CNH — InstrutorProcnh' },
  { path:'aluno/servicos', component:ServiceDiscoveryComponent, title:'Encontre serviços — InstrutorProcnh' },
  { path:'aluno/instrutores', component:InstructorNationalMapComponent, title:'Instrutores no Brasil — InstrutorProcnh' },
  { path:'aluno/instrutores/mapa', component:InstructorMapComponent, title:'Mapa local de instrutores — InstrutorProcnh' },
  { path:'aluno/instrutores/:id', component:InstructorProfileComponent, title:'Perfil demonstrativo — InstrutorProcnh' },
  { path:'aluno/solicitar', component:StudentRequestComponent, title:'Solicitar aula — InstrutorProcnh' },
  { path:'aluno/matching', component:MatchingComponent, title:'Matching demonstrativo — InstrutorProcnh' },
  { path:'aluno/demanda', component:StudentMarketplaceComponent, title:'Demanda demonstrativa — InstrutorProcnh' },
  { path:'aluno/cadastro-demo', component:StudentMarketplaceComponent, title:'Cadastro do aluno DEMO — InstrutorProcnh' },
  { path:'aluno/clinicas', component:ClinicDemoComponent, title:'Clínicas e exames — InstrutorProcnh' },
  { path:'profissional', component:ProfessionalEntryComponent, title:'Área profissional — InstrutorProcnh' },
  { path:'profissional/instrutor/entrada', component:InstructorEntryComponent, title:'Cadastro do instrutor — InstrutorProcnh' },
  { path:'profissional/instrutor', component:InstructorDashboardComponent, title:'Painel do instrutor — InstrutorProcnh' },
  { path:'profissional/instrutor/status', component:InstructorStatusComponent, title:'Status do instrutor — InstrutorProcnh' },
  { path:'profissional/instrutor/onboarding', component:InstructorOnboardingComponent, title:'Quero atuar como instrutor — InstrutorProcnh' },
  { path:'profissional/demanda', component:DemandDemoComponent, title:'Mapa de demanda — InstrutorProcnh' },
  { path:'**', redirectTo:'' },
];
