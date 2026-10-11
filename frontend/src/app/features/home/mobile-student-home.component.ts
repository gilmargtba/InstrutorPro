import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { StudentLocationService } from '../../core/student-location.service';

@Component({
  selector: 'app-mobile-student-home',
  imports: [FormsModule],
  template: `
    <section class="mobile-home">
      <p class="eyebrow">InstrutorProCNH</p>
      <h1>Encontre seu instrutor</h1>
      <p>Pesquise profissionais disponíveis sem criar conta.</p>
      <button class="locate" type="button" (click)="useLocation()" [disabled]="locating()">
        <i class="pi pi-crosshairs"></i> {{ locating() ? 'Localizando…' : 'Usar minha localização' }}
      </button>
      <div class="divider">ou escolha uma cidade, UF ou CEP</div>
      <form (ngSubmit)="search()">
        <label for="mobile-place">Cidade / UF / CEP</label>
        <input id="mobile-place" name="place" [(ngModel)]="place" placeholder="Ex.: Goiatuba, GO" required>
        <label for="mobile-category">Categoria da CNH</label>
        <select id="mobile-category" name="category" [(ngModel)]="category">
          <option value="">Todas as categorias</option>
          @for (item of categories; track item) { <option [value]="item">{{item}}</option> }
        </select>
        <button class="submit" type="submit">Encontrar instrutores</button>
      </form>
      @if (error()) { <p class="error" role="alert">{{error()}}</p> }
      <p class="privacy">A localização é solicitada só após seu toque. Se negar, continue pela cidade ou CEP.</p>
    </section>
  `,
  styles: [`
    .mobile-home{max-width:35rem;margin:auto;padding:2rem 1.25rem 7rem;min-height:calc(100dvh - 8rem)}
    h1{font-size:clamp(2.8rem,12vw,4.2rem);line-height:1.02;color:#103f63;margin:.5rem 0}
    p{color:#527083}.locate,.submit{display:flex;align-items:center;justify-content:center;gap:.7rem;width:100%;min-height:3.6rem;border:0;border-radius:1rem;font-weight:800;font-size:1rem;cursor:pointer}
    .locate{margin-top:2rem;background:#e6f5f3;color:#0d6771}.submit{margin-top:1.5rem;background:#ef762d;color:#fff}
    .divider{text-align:center;margin:1.8rem 0;color:#5d7782}form{display:grid;gap:.65rem}label{font-weight:800;color:#163e57;margin-top:.7rem}input,select{width:100%;min-height:3.4rem;border:1px solid #bcd3d0;border-radius:.85rem;padding:.8rem;background:#fff}
    .error{color:#982d26}.privacy{font-size:.82rem;margin-top:1.4rem}
  `],
})
export class MobileStudentHomeComponent {
  private readonly router = inject(Router);
  private readonly location = inject(StudentLocationService);
  readonly categories = ['A', 'B', 'C', 'D', 'E'];
  readonly locating = signal(false);
  readonly error = signal('');
  place = '';
  category = '';

  search(): void {
    const local = this.place.trim();
    if (!local) { this.error.set('Informe uma cidade, UF ou CEP.'); return; }
    void this.router.navigate(['/aluno/instrutores/mapa'], {
      queryParams: { local, categoria: this.category || null },
    });
  }

  async useLocation(): Promise<void> {
    this.error.set('');
    this.locating.set(true);
    try {
      this.location.handOff(await this.location.currentPosition());
      await this.router.navigate(['/aluno/instrutores/mapa'], {
        queryParams: { categoria: this.category || null },
      });
    } catch {
      this.error.set('Localização não autorizada. Pesquise por cidade, UF ou CEP.');
    } finally {
      this.locating.set(false);
    }
  }
}
