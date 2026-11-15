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

  it('keeps the selected public point centered when zooming and stops at the limit', () => {
    const provider = new GoogleMapProvider();
    const map = jasmine.createSpyObj<google.maps.Map>('Map', ['getZoom', 'setZoom', 'setCenter']);
    const point = {lat: -15.54, lng: -47.34};
    Object.assign(provider, {map, markers: new Map([['instructor', {position: point}]]), selectedId: 'instructor'});
    map.getZoom.and.returnValue(19);
    expect(provider.zoomSelected()).toBeTrue();
    expect(map.setCenter).toHaveBeenCalledWith(point);
    expect(map.setZoom).toHaveBeenCalledWith(20);
    map.getZoom.and.returnValue(20);
    expect(provider.zoomSelected()).toBeFalse();
    expect(map.setZoom).toHaveBeenCalledTimes(1);
  });
});
