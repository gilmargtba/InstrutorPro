import { Injectable } from '@angular/core';
import * as L from 'leaflet';
import { SearchInstructor } from './instructor-search.provider';

export abstract class MapProvider { abstract mount(element:HTMLElement,onSelect:(id:string)=>void):void;abstract render(items:SearchInstructor[],selectedId:string|null):void;abstract select(id:string):void;abstract destroy():void; }

@Injectable({providedIn:'root'})
export class LeafletMapProvider implements MapProvider {
  private map?:L.Map;private markers=new Map<string,L.Marker>();private onSelect:(id:string)=>void=()=>{};
  mount(element:HTMLElement,onSelect:(id:string)=>void){this.destroy();this.onSelect=onSelect;this.map=L.map(element,{zoomControl:true}).setView([-30.0346,-51.2177],12);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors',maxZoom:19}).addTo(this.map)}
  render(items:SearchInstructor[],selectedId:string|null){if(!this.map)return;this.markers.forEach(m=>m.remove());this.markers.clear();const group=L.featureGroup();for(const item of items){const icon=L.divIcon({className:'demo-marker',html:'<span aria-hidden="true">🚗</span>',iconSize:[38,38],iconAnchor:[19,19]});const marker=L.marker([item.latitude,item.longitude],{title:item.display_name,icon}).on('click',()=>this.onSelect(item.id));marker.bindTooltip(item.display_name);marker.addTo(this.map);group.addLayer(marker);this.markers.set(item.id,marker)}if(items.length)this.map.fitBounds(group.getBounds().pad(.25),{maxZoom:14});if(selectedId)this.select(selectedId)}
  select(id:string){const marker=this.markers.get(id);if(marker&&this.map){marker.openTooltip();this.map.panTo(marker.getLatLng())}}
  destroy(){this.map?.remove();this.map=undefined;this.markers.clear()}
}
