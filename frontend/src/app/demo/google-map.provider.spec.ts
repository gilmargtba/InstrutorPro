import { GoogleMapProvider } from './google-map.provider';

describe('GoogleMapProvider public point selection', () => {
  it('moves to the published point and allows street-level zoom', () => {
    const provider = new GoogleMapProvider();
    const map = jasmine.createSpyObj<google.maps.Map>('Map', ['panTo', 'getZoom', 'setZoom']);
    map.getZoom.and.returnValue(12);
    const point = { lat: -18.01, lng: -49.37 };
    const marker = { content: document.createElement('span'), position: point };
    Object.assign(provider, { map, markers: new Map([['instructor', marker]]) });

    provider.select('instructor');

    expect(map.panTo).toHaveBeenCalledWith(point);
    expect(map.setZoom).toHaveBeenCalledWith(18);
    expect(marker.content.classList.contains('selected')).toBeTrue();
  });
});
