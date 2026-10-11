import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { StudentLocationService } from '../../core/student-location.service';
import { MobileStudentHomeComponent } from './mobile-student-home.component';

describe('MobileStudentHomeComponent', () => {
  let router: jasmine.SpyObj<Router>;
  let location: jasmine.SpyObj<StudentLocationService>;

  beforeEach(async () => {
    router = jasmine.createSpyObj('Router', ['navigate']);
    router.navigate.and.resolveTo(true);
    location = jasmine.createSpyObj('StudentLocationService', ['currentPosition', 'handOff']);
    await TestBed.configureTestingModule({
      imports: [MobileStudentHomeComponent],
      providers: [
        { provide: Router, useValue: router },
        { provide: StudentLocationService, useValue: location },
      ],
    }).compileComponents();
  });

  it('requires a place and carries the selected A–E category', () => {
    const component = TestBed.createComponent(MobileStudentHomeComponent).componentInstance;
    component.search();
    expect(router.navigate).not.toHaveBeenCalled();
    component.place = 'Goiatuba, GO';
    component.category = 'B';
    component.search();
    expect(router.navigate).toHaveBeenCalledWith(['/aluno/instrutores/mapa'], {
      queryParams: { local: 'Goiatuba, GO', categoria: 'B' },
    });
  });

  it('keeps manual search available when geolocation is denied', async () => {
    const component = TestBed.createComponent(MobileStudentHomeComponent).componentInstance;
    location.currentPosition.and.rejectWith(new Error('permission denied'));
    await component.useLocation();
    expect(component.error()).toContain('cidade');
    expect(router.navigate).not.toHaveBeenCalled();
    expect(location.handOff).not.toHaveBeenCalled();
  });

  it('hands off coordinates without placing them in a URL', async () => {
    const component = TestBed.createComponent(MobileStudentHomeComponent).componentInstance;
    location.currentPosition.and.resolveTo({ latitude: -18.01, longitude: -49.37 });
    await component.useLocation();
    expect(location.handOff).toHaveBeenCalledWith({ latitude: -18.01, longitude: -49.37 });
    expect(router.navigate).toHaveBeenCalledWith(['/aluno/instrutores/mapa'], {
      queryParams: { categoria: null },
    });
  });
});
