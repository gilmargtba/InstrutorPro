import { provideHttpClient } from "@angular/common/http";
import {
  HttpTestingController,
  provideHttpClientTesting,
} from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { provideRouter } from "@angular/router";

import {
  AccountPrivacyComponent,
  MyAccountComponent,
  PrivacyPolicyComponent,
} from "./account-privacy.component";

describe("account and privacy", () => {
  let http: HttpTestingController | undefined;
  afterEach(() => {
    http?.verify();
    http = undefined;
  });

  it("loads and saves only the editable self-service contract", () => {
    TestBed.configureTestingModule({
      imports: [MyAccountComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    const fixture = TestBed.createComponent(MyAccountComponent);
    http = TestBed.inject(HttpTestingController);
    const account = {
      email: "student@example.invalid",
      email_editable: false,
      phone: "",
      birth_date: null,
      roles: ["STUDENT"],
      student: {
        display_name: "Ana",
        city: "Porto Alegre",
        uf: "RS",
        intended_category: "B",
        preferred_transmission: "INDIFFERENT",
      },
    };
    http.expectOne("/account/me/").flush(account);
    fixture.componentInstance.save();
    const update = http.expectOne("/account/me/");
    expect(update.request.method).toBe("PATCH");
    expect(update.request.body.student_display_name).toBe("Ana");
    expect(update.request.body.roles).toBeUndefined();
    expect(update.request.body.email).toBeUndefined();
    update.flush(account);
  });

  it("creates a privacy request without deleting the account client-side", () => {
    TestBed.configureTestingModule({
      imports: [AccountPrivacyComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    const fixture = TestBed.createComponent(AccountPrivacyComponent);
    http = TestBed.inject(HttpTestingController);
    http.expectOne("/privacy/requests/").flush([]);
    fixture.componentInstance.requestType = "DELETION";
    fixture.componentInstance.submit();
    const request = http.expectOne("/privacy/requests/");
    expect(request.request.method).toBe("POST");
    expect(request.request.body.request_type).toBe("DELETION");
    request.flush({
      id: "request-id",
      request_type: "DELETION",
      status: "OPEN",
      details: "",
      requested_at: "2026-09-16T00:00:00Z",
    });
    http.expectOne("/privacy/requests/").flush([]);
  });

  it("publishes the confirmed privacy identity without invented legal data", () => {
    TestBed.configureTestingModule({ imports: [PrivacyPolicyComponent] });
    const text = TestBed.createComponent(PrivacyPolicyComponent).nativeElement.textContent;
    expect(text).toContain("InstrutorProCNH");
    expect(text).toContain("10.280.826/0001-05");
    expect(text).toContain("focusgtba@gmail.com");
    expect(text).not.toContain("DPO:");
  });
});
