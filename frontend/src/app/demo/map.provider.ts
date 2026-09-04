import { Injectable } from '@angular/core';
import L from 'leaflet';
import 'leaflet.markercluster';
import { SearchInstructor } from './instructor-search.provider';

export abstract class MapProvider { abstract mount(element:HTMLElement,onSelect:(id:string)=>void):void;abstract focus(latitude:number,longitude:number,zoom?:number):void;abstract render(items:SearchInstructor[],selectedId:string|null):void;abstract select(id:string):void;abstract refresh():void;abstract destroy():void; }

@Injectable({providedIn:'root'})
export class LeafletMapProvider implements MapProvider {
  private map?:L.Map;private cluster?:L.MarkerClusterGroup;private markers=new Map<string,L.Marker>();private onSelect:(id:string)=>void=()=>{};
  mount(element:HTMLElement,onSelect:(id:string)=>void){this.destroy();this.onSelect=onSelect;this.map=L.map(element,{zoomControl:true}).setView([-14.2,-51.9],4);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors',maxZoom:19}).addTo(this.map)}
  focus(latitude:number,longitude:number,zoom=12){this.map?.setView([latitude,longitude],zoom)}
  render(items:SearchInstructor[],selectedId:string|null){if(!this.map)return;if(this.cluster)this.map.removeLayer(this.cluster);this.markers.clear();this.cluster=L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:55});const group=L.featureGroup();for(const item of items){const initials=item.display_name.split(' ').slice(0,2).map(part=>part.match(/[\p{L}\p{N}]/u)?.[0]??'').join('').toUpperCase()||'IP';const icon=L.divIcon({className:'demo-marker',html:`<span aria-hidden="true">${initials}</span>`,iconSize:[42,42],iconAnchor:[21,21]});const marker=L.marker([item.latitude,item.longitude],{title:item.display_name,icon}).on('click',()=>this.onSelect(item.id));marker.bindTooltip(item.display_name);this.cluster.addLayer(marker);group.addLayer(marker);this.markers.set(item.id,marker)}this.map.addLayer(this.cluster);if(items.length)this.map.fitBounds(group.getBounds().pad(.25),{maxZoom:14});if(selectedId)this.select(selectedId)}
  select(id:string){const marker=this.markers.get(id);if(marker&&this.map){this.cluster?.zoomToShowLayer(marker,()=>marker.openTooltip());this.map.panTo(marker.getLatLng())}}
  refresh(){setTimeout(()=>this.map?.invalidateSize(),0)}
  destroy(){this.map?.remove();this.map=undefined;this.cluster=undefined;this.markers.clear()}
}
