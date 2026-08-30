import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { ClinicDemoComponent, DemandDemoComponent, InstructorDashboardComponent, InstructorProfileComponent, JourneyComponent, MatchingComponent, ProfessionalEntryComponent, ServiceDiscoveryComponent, StudentDemandComponent, StudentRequestComponent } from './features/demo/demo-pages.component';
import { InstructorMapComponent } from './features/demo/instructor-map.component';
import { InstructorNationalMapComponent } from './features/demo/instructor-national-map.component';
import { InstructorOnboardingComponent } from './features/demo/instructor-onboarding.component';
import { StudentMarketplaceComponent } from './features/demo/student-marketplace.component';
import { InstructorEntryComponent, InstructorStatusComponent, LoginComponent, StudentEntryComponent } from './features/demo/marketplace-entry.component';

export const routes: Routes = [
  { path:'', component:HomeComponent, title:'InstrutorPro — Sua jornada para a CNH' },
  { path:'aluno', component:StudentEntryComponent, title:'Aluno — InstrutorPro' },
  { path:'cadastro/aluno', component:StudentMarketplaceComponent, title:'Criar conta de aluno — InstrutorPro' },
  { path:'entrar', component:LoginComponent, title:'Entrar — InstrutorPro' },
  { path:'aluno/jornada', component:JourneyComponent, title:'Minha Jornada CNH — InstrutorPro' },
  { path:'aluno/servicos', component:ServiceDiscoveryComponent, title:'Encontre serviços — InstrutorPro' },
  { path:'aluno/instrutores', component:InstructorNationalMapComponent, title:'Instrutores no Brasil — InstrutorPro' },
  { path:'aluno/instrutores/mapa', component:InstructorMapComponent, title:'Mapa local de instrutores — InstrutorPro' },
  { path:'aluno/instrutores/:id', component:InstructorProfileComponent, title:'Perfil demonstrativo — InstrutorPro' },
  { path:'aluno/solicitar', component:StudentRequestComponent, title:'Solicitar aula — InstrutorPro' },
  { path:'aluno/matching', component:MatchingComponent, title:'Matching demonstrativo — InstrutorPro' },
  { path:'aluno/demanda', component:StudentMarketplaceComponent, title:'Demanda demonstrativa — InstrutorPro' },
  { path:'aluno/cadastro-demo', component:StudentMarketplaceComponent, title:'Cadastro do aluno DEMO — InstrutorPro' },
  { path:'aluno/clinicas', component:ClinicDemoComponent, title:'Clínicas e exames — InstrutorPro' },
  { path:'profissional', component:ProfessionalEntryComponent, title:'Área profissional — InstrutorPro' },
  { path:'profissional/instrutor/entrada', component:InstructorEntryComponent, title:'Cadastro do instrutor — InstrutorPro' },
  { path:'profissional/instrutor', component:InstructorDashboardComponent, title:'Painel do instrutor — InstrutorPro' },
  { path:'profissional/instrutor/status', component:InstructorStatusComponent, title:'Status do instrutor — InstrutorPro' },
  { path:'profissional/instrutor/onboarding', component:InstructorOnboardingComponent, title:'Quero atuar como instrutor — InstrutorPro' },
  { path:'profissional/demanda', component:DemandDemoComponent, title:'Mapa de demanda — InstrutorPro' },
  { path:'**', redirectTo:'' },
];
