import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { WhatsappLinkService } from '../../core/whatsapp-link.service';
import { PublicInstructorProfileComponent } from './public-instructor-profile.component';

describe('PublicInstructorProfileComponent lesson options', () => {
  const whatsapp = { open: jasmine.createSpy('open').and.returnValue(Promise.resolve()) };

  beforeEach(() => TestBed.configureTestingModule({
    imports: [PublicInstructorProfileComponent],
    providers: [
      provideHttpClient(), provideHttpClientTesting(), provideRouter([]),
      { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => 'instructor-1' }, queryParamMap: { get: () => null } } } },
      { provide: WhatsappLinkService, useValue: whatsapp },
    ],
  }));

  it('shows each active category offer and contacts the selected category', () => {
    const fixture = TestBed.createComponent(PublicInstructorProfileComponent);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/instructors/instructor-1/').flush({
      id: 'instructor-1', display_name: 'Instrutora Exemplo', bio: '', categories: ['A', 'B'],
      transmission_options: ['MANUAL'], vehicle_available: false, availability_summary: '',
      profile_photo_url: null, verified_claims: [], service_area: { city: 'Goiatuba', uf: 'GO', radius_km: 10 },
      synthetic: false, price_amount: 80, offer_category: 'A', price_from: true, duration_minutes: 50,
      vehicle: null, lesson_options: [
        { category: 'A', price_amount: 80, duration_minutes: 50 },
        { category: 'B', price_amount: 100, duration_minutes: 60 },
      ],
      lesson_packages: [{ id: 'package-1', name: 'Cinco aulas', category: 'B', categories: ['B'], lesson_count: 5,
        price_amount: 450, price_per_lesson: 90, vehicle_included: true, description: 'Pacote opcional' }],
    });
    fixture.detectChanges();
    const cards = fixture.nativeElement.querySelectorAll('.lesson-option');
    expect(cards.length).toBe(3);
    expect(cards[0].textContent).toContain('R$ 80,00');
    expect(cards[1].textContent).toContain('60 minutos');
    cards[1].querySelector('button').click();
    const contact = http.expectOne('/instructors/instructor-1/whatsapp-contact/');
    expect(contact.request.body.category).toBe('B');
    contact.flush({ destination_url: 'https://wa.me/5564999999999' });
    expect(whatsapp.open).toHaveBeenCalledWith('https://wa.me/5564999999999');
    expect(cards[2].textContent).toContain('Cinco aulas');
    expect(cards[2].textContent).toContain('R$ 450,00');
    cards[2].querySelector('button').click();
    const packageContact = http.expectOne('/instructors/instructor-1/whatsapp-contact/');
    expect(packageContact.request.body).toEqual({ category: 'B', source: 'public-package' });
    packageContact.flush({ destination_url: 'https://wa.me/5564999999999' });
  });

  it('shows both package categories and routes contact to the chosen one', () => {
    const fixture = TestBed.createComponent(PublicInstructorProfileComponent);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/instructors/instructor-1/').flush({
      id: 'instructor-1', display_name: 'Instrutora Exemplo', bio: '', categories: ['A', 'B'],
      transmission_options: ['MANUAL'], vehicle_available: true, availability_summary: '',
      profile_photo_url: null, verified_claims: [], service_area: { city: 'Goiatuba', uf: 'GO', radius_km: 10 },
      synthetic: false, price_amount: 80, offer_category: 'A', price_from: true, duration_minutes: 50,
      vehicle: null, lesson_options: [], lesson_packages: [{ id: 'package-1', name: 'A e B',
        category: 'A', categories: ['A', 'B'], lesson_count: 5, price_amount: 300,
        price_per_lesson: 60, vehicle_included: true, description: '' }],
    });
    fixture.detectChanges();
    const card = fixture.nativeElement.querySelector('.lesson-option') as HTMLElement;
    expect(card.textContent).toContain('Categorias A, B');
    const buttons = card.querySelectorAll('button');
    expect(buttons.length).toBe(2);
    buttons[1].click();
    const contact = http.expectOne('/instructors/instructor-1/whatsapp-contact/');
    expect(contact.request.body.category).toBe('B');
    contact.flush({ destination_url: 'https://wa.me/5564999999999' });
  });
});
