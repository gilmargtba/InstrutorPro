import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { ClinicDemoComponent, DemandDemoComponent, InstructorDashboardComponent, InstructorProfileComponent, JourneyComponent, MatchingComponent, ProfessionalEntryComponent, ServiceDiscoveryComponent, StudentDemandComponent, StudentRequestComponent } from './features/demo/demo-pages.component';
import { InstructorMapComponent } from './features/demo/instructor-map.component';
import { InstructorNationalMapComponent } from './features/demo/instructor-national-map.component';
import { InstructorOnboardingComponent } from './features/demo/instructor-onboarding.component';
import { StudentMarketplaceComponent } from './features/demo/student-marketplace.component';
import { InstructorEntryComponent, InstructorPortalComponent, InstructorStatusComponent, LoginComponent, StudentDashboardComponent, StudentEntryComponent } from './features/demo/marketplace-entry.component';

export const routes: Routes = [
  { path:'', component:HomeComponent, title:'InstrutorProCNH — Sua jornada para a CNH' },
  { path:'aluno', component:StudentEntryComponent, title:'Aluno — InstrutorProCNH' },
  { path:'cadastro/aluno', component:StudentMarketplaceComponent, title:'Criar conta de aluno — InstrutorProCNH' },
  { path:'entrar', component:LoginComponent, title:'Entrar — InstrutorProCNH' },
  { path:'aluno/jornada', component:JourneyComponent, title:'Minha Jornada CNH — InstrutorProCNH' },
  { path:'aluno/painel', component:StudentDashboardComponent, title:'Painel do aluno — InstrutorProCNH' },
  { path:'aluno/servicos', component:ServiceDiscoveryComponent, title:'Encontre serviços — InstrutorProCNH' },
  { path:'aluno/instrutores', component:InstructorNationalMapComponent, title:'Instrutores no Brasil — InstrutorProCNH' },
  { path:'aluno/instrutores/mapa', component:InstructorMapComponent, title:'Mapa local de instrutores — InstrutorProCNH' },
  { path:'aluno/instrutores/:id', component:InstructorProfileComponent, title:'Perfil demonstrativo — InstrutorProCNH' },
  { path:'aluno/solicitar', component:StudentRequestComponent, title:'Solicitar aula — InstrutorProCNH' },
  { path:'aluno/matching', component:MatchingComponent, title:'Matching demonstrativo — InstrutorProCNH' },
  { path:'aluno/demanda', component:StudentMarketplaceComponent, title:'Demanda demonstrativa — InstrutorProCNH' },
  { path:'aluno/cadastro-demo', component:StudentMarketplaceComponent, title:'Cadastro do aluno DEMO — InstrutorProCNH' },
  { path:'aluno/clinicas', component:ClinicDemoComponent, title:'Clínicas e exames — InstrutorProCNH' },
  { path:'profissional', component:ProfessionalEntryComponent, title:'Área profissional — InstrutorProCNH' },
  { path:'profissional/instrutor/entrada', component:InstructorEntryComponent, title:'Cadastro do instrutor — InstrutorProCNH' },
  { path:'profissional/instrutor', component:InstructorPortalComponent, title:'Painel do instrutor — InstrutorProCNH' },
  { path:'profissional/instrutor/status', component:InstructorStatusComponent, title:'Status do instrutor — InstrutorProCNH' },
  { path:'profissional/instrutor/onboarding', component:InstructorOnboardingComponent, title:'Quero atuar como instrutor — InstrutorProCNH' },
  { path:'profissional/demanda', component:DemandDemoComponent, title:'Mapa de demanda — InstrutorProCNH' },
  { path:'**', redirectTo:'' },
];
