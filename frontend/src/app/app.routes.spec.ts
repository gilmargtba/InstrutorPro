import { mobileRoutes, routes } from './app.routes';
import { CFCUnavailableComponent } from './features/cfc/cfc-pages.component';
describe('Demo navigation',()=>{it('contains the complete student flow',()=>{const paths=routes.map(r=>r.path);expect(paths).toContain('aluno/jornada');expect(paths).toContain('aluno/instrutores');expect(paths).toContain('aluno/instrutores/mapa');expect(paths).toContain('aluno/instrutores/:id');expect(paths).toContain('aluno/solicitar');expect(paths).toContain('aluno/matching');expect(paths).toContain('aluno/clinicas')});it('contains the professional instructor and demand flow',()=>{const paths=routes.map(r=>r.path);expect(paths).toContain('profissional');expect(paths).toContain('profissional/instrutor');expect(paths).toContain('profissional/demanda');expect(paths).toContain('cfc/cadastro')})});
describe('Mobile student navigation',()=>{it('exposes only anonymous discovery and privacy routes',()=>{const paths=mobileRoutes.map(route=>route.path);expect(paths).toContain('aluno/instrutores/mapa');expect(paths).toContain('aluno/instrutores/:id');expect(paths).not.toContain('profissional');expect(paths).not.toContain('entrar');expect(paths).not.toContain('instrutor/plano')})});

it('shows an unavailable page for direct CFC links while the module is paused', () => {
  for (const path of ['cfc', 'cfc/cadastro', 'cfc/ativar-instrutor']) {
    expect(routes.find(route => route.path === path)?.component).toBe(CFCUnavailableComponent);
  }
});

it('offers the no-instructor page on web and mobile', () => {
  expect(routes.some(route => route.path === 'aluno/sem-instrutor')).toBeTrue();
  expect(mobileRoutes.some(route => route.path === 'aluno/sem-instrutor')).toBeTrue();
});
