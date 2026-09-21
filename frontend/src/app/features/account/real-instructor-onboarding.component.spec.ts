import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { RealInstructorOnboardingComponent } from './real-instructor-onboarding.component';

describe('RealInstructorOnboardingComponent',()=>{
  beforeEach(()=>TestBed.configureTestingModule({imports:[RealInstructorOnboardingComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));
  it('saves only the allowed non-documental onboarding fields',()=>{
    const component=TestBed.createComponent(RealInstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto'}});
    component.form.whatsapp='+5551999990001';component.form.price_amount=95;component.form.instructor_city='Goiânia';component.form.instructor_uf='GO';component.form.service_latitude=-16.6869;component.form.service_longitude=-49.2648;component.form.service_location_authorized=true;component.form.vehicle.make='Marca';component.form.vehicle.model='Modelo';
    component.submit();
    const request=http.expectOne('/account/me/');expect(request.request.method).toBe('PATCH');expect(request.request.body.categories).toEqual(['B']);expect(request.request.body.vehicle.transmission).toBe('MANUAL');expect(request.request.body.document).toBeUndefined();request.flush({});
  });
});
