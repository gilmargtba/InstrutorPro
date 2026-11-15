import { Injectable } from '@angular/core';
import L from 'leaflet';
import 'leaflet.markercluster';
import { SearchInstructor } from './instructor-search.provider';
import { apiUrl, publicMediaUrl } from '../core/api-url';

export abstract class MapProvider { abstract mount(element:HTMLElement,onSelect:(id:string)=>void):void;abstract focus(latitude:number,longitude:number,zoom?:number):void;abstract render(items:SearchInstructor[],selectedId:string|null):void;abstract select(id:string):void;abstract zoomSelected():boolean;abstract atMaxZoom():boolean;abstract refresh():void;abstract destroy():void; }

@Injectable({providedIn:'root'})
export class LeafletMapProvider implements MapProvider {
  private map?:L.Map;private cluster?:L.MarkerClusterGroup;private markers=new Map<string,L.Marker>();private onSelect:(id:string)=>void=()=>{};
  private resizeObserver?:ResizeObserver;private refreshTimer?:ReturnType<typeof setTimeout>;private selectedId:string|null=null;
  mount(element:HTMLElement,onSelect:(id:string)=>void){
    this.destroy();
    this.onSelect=onSelect;
    this.map=L.map(element,{zoomControl:true}).setView([-14.2,-51.9],4);
    this.map.on('zoomend',()=>{const marker=this.selectedId?this.markers.get(this.selectedId):undefined;if(marker)this.map?.panTo(marker.getLatLng())});
    L.tileLayer(apiUrl('/map/tiles/{z}/{x}/{y}.png'),{attribution:'&copy; MapTiler &copy; OpenStreetMap contributors',maxZoom:19}).addTo(this.map);
    if(typeof ResizeObserver!=='undefined'){
      this.resizeObserver=new ResizeObserver(()=>this.refresh());
      this.resizeObserver.observe(element);
    }
  }
  focus(latitude:number,longitude:number,zoom=12){this.selectedId=null;this.map?.setView([latitude,longitude],zoom)}
  render(items:SearchInstructor[],selectedId:string|null){if(!this.map)return;this.selectedId=selectedId;if(this.cluster)this.map.removeLayer(this.cluster);this.markers.clear();this.cluster=L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:55});const group=L.featureGroup();for(const item of items){const initials=item.display_name.split(' ').slice(0,2).map(part=>part.match(/[\p{L}\p{N}]/u)?.[0]??'').join('').toUpperCase()||'IP';const content=document.createElement('span');content.setAttribute('aria-hidden','true');const photo=publicMediaUrl(item.profile_photo_url);if(photo){const image=document.createElement('img');image.src=photo;image.alt='';image.onerror=()=>{image.remove();content.textContent=initials};content.appendChild(image)}else{content.textContent=initials}const icon=L.divIcon({className:'demo-marker',html:content,iconSize:[42,42],iconAnchor:[21,21]});const marker=L.marker([item.latitude,item.longitude],{title:item.display_name,icon}).on('click',()=>this.onSelect(item.id));marker.bindTooltip(item.display_name);this.cluster.addLayer(marker);group.addLayer(marker);this.markers.set(item.id,marker)}this.map.addLayer(this.cluster);if(items.length)this.map.fitBounds(group.getBounds().pad(.25),{maxZoom:14});if(selectedId)this.select(selectedId)}
  select(id:string){this.selectedId=id;const marker=this.markers.get(id);if(marker&&this.map){this.cluster?.zoomToShowLayer(marker,()=>{this.map?.setView(marker.getLatLng(),Math.max(this.map.getZoom(),18));marker.openTooltip()})}}
  zoomSelected():boolean{if(!this.map)return false;const marker=this.selectedId?this.markers.get(this.selectedId):undefined;const next=Math.min(this.map.getZoom()+1,19);if(next===this.map.getZoom())return false;this.map.setView(marker?.getLatLng()??this.map.getCenter(),next);return true}
  atMaxZoom():boolean{return (this.map?.getZoom()??0)>=19}
  refresh(){if(this.refreshTimer)clearTimeout(this.refreshTimer);this.refreshTimer=setTimeout(()=>{this.refreshTimer=undefined;this.map?.invalidateSize({pan:false})},0)}
  destroy(){this.resizeObserver?.disconnect();this.resizeObserver=undefined;if(this.refreshTimer)clearTimeout(this.refreshTimer);this.refreshTimer=undefined;this.map?.remove();this.map=undefined;this.cluster=undefined;this.markers.clear();this.selectedId=null}
}
