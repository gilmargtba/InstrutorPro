import { TestBed } from '@angular/core/testing';
import { WhatsappLinkService } from './whatsapp-link.service';

describe('WhatsappLinkService', () => {
  it('rejects an untrusted destination before opening anything', async () => {
    const service = TestBed.inject(WhatsappLinkService);
    await expectAsync(service.open('https://example.com/5511999999999')).toBeRejected();
    await expectAsync(service.open('http://wa.me/5511999999999')).toBeRejected();
    await expectAsync(service.open('https://wa.me/not-a-number')).toBeRejected();
  });
});
