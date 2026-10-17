import { TestBed } from '@angular/core/testing';
import { AppDownloadComponent } from './app-download.component';

describe('AppDownloadComponent', () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => { globalThis.fetch = originalFetch; });

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [AppDownloadComponent] }).compileComponents();
  });

  it('hides the download when the signed APK is absent', async () => {
    globalThis.fetch = jasmine.createSpy('fetch').and.resolveTo(new Response(null, { status: 404 }));
    const fixture = TestBed.createComponent(AppDownloadComponent);
    fixture.detectChanges();
    await fixture.componentInstance.ngOnInit();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('a[download]')).toBeNull();
    expect(fixture.nativeElement.textContent).toContain('ainda não está disponível');
    expect(fixture.nativeElement.textContent).toContain('Adicionar à Tela de Início');
    expect(fixture.nativeElement.textContent).toContain('não um aplicativo da App Store');
  });

  it('offers only the exact local APK when present with the expected MIME', async () => {
    globalThis.fetch = jasmine.createSpy('fetch').and.resolveTo(new Response(null, {
      status: 200,
      headers: { 'content-type': 'application/vnd.android.package-archive' },
    }));
    const fixture = TestBed.createComponent(AppDownloadComponent);
    fixture.detectChanges();
    await fixture.componentInstance.ngOnInit();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('a[download]').getAttribute('href'))
      .toBe('/downloads/InstrutorProCNH-android.apk');
    expect(fixture.nativeElement.textContent).toContain('D23707AF7B05E2C2E9C164C14434785036DC713D7DD6B695C3E35F993B43900E');
    expect(globalThis.fetch).toHaveBeenCalledWith('/downloads/InstrutorProCNH-android.apk', {
      method: 'HEAD', cache: 'no-store',
    });
  });
});
