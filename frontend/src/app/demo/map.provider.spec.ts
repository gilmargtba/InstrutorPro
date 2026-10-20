import { LeafletMapProvider } from './map.provider';
describe('LeafletMapProvider',()=>{it('synchronizes marker selection through its callback',()=>{const provider=new LeafletMapProvider();const host=document.createElement('div');host.style.height='300px';document.body.appendChild(host);let selected='';provider.mount(host,id=>selected=id);expect(host.querySelector('.leaflet-tile')?.getAttribute('src')).toContain('/api/v1/map/tiles/');provider.render([{id:'demo-1',display_name:'Pessoa Demo',latitude:-30.03,longitude:-51.21,distance_km:1,categories:['B'],offer_category:'B',transmission:'MANUAL',vehicle_available:true,price_amount:90,price_from:false,duration_minutes:60,vehicle:{make:'Chevrolet',model:'Onix',year:2024,transmission:'MANUAL'},availability_summary:'Demo',demo:true,profile_photo_url:null,verified_claims:[],city:'Porto Alegre',uf:'RS'}],null);(host.querySelector('.demo-marker') as HTMLElement).click();expect(selected).toBe('demo-1');provider.select('demo-1');provider.destroy();host.remove()})});

describe('LeafletMapProvider approved photo markers', () => {
  it('shows the public photo URL when provided by the search API', () => {
    const provider = new LeafletMapProvider();
    const host = document.createElement('div');
    host.style.height = '300px';
    document.body.appendChild(host);
    provider.mount(host, () => undefined);
    provider.render([{
      id: 'instructor-1', display_name: 'Pessoa Publicada', latitude: -18.01,
      longitude: -49.37, distance_km: 1, categories: ['B'], offer_category: 'B',
      transmission: 'MANUAL', vehicle_available: true, price_amount: 90,
      price_from: false, duration_minutes: 60, vehicle: null,
      availability_summary: '', demo: false,
      profile_photo_url: '/api/v1/instructors/profile-photos/approved/',
      verified_claims: [], city: 'Goiatuba', uf: 'GO',
    }], null);
    expect(host.querySelector('.demo-marker img')?.getAttribute('src')).toBe(
      '/api/v1/instructors/profile-photos/approved/'
    );
    provider.destroy();
    host.remove();
  });
});
