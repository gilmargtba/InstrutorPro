import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

export interface SearchFilters { location:string; radius:number; category:string; transmission:string; vehicleAvailable:boolean; maxPrice:number|null; ordering:'distance'|'price'; }
export interface SearchInstructor { id:string;display_name:string;latitude:number;longitude:number;distance_km:number;categories:string[];transmission:string;vehicle_available:boolean;price_amount:number;price_from:boolean;duration_minutes:number;vehicle:{make:string;model:string;year:number;transmission:string}|null;availability_summary:string;demo:boolean;profile_photo_url:string|null;verified_claims:string[];city:string;uf:string; }
export interface GeocodingResult { id:string;label:string;latitude:number;longitude:number;place_type:string;city:string;uf:string;bbox:number[]|null }
export interface GeocodeResponse { results:GeocodingResult[];provider:string }
interface SearchResponse { count:number;results:SearchInstructor[] }
export interface InstructorStateSummary { uf:string;count:number;search_location:string }
interface StateSummaryResponse { states:InstructorStateSummary[] }

@Injectable({providedIn:'root'})
export class InstructorSearchProvider {
  private readonly http=inject(HttpClient);
  geocode(query:string,limit=5){return this.http.get<GeocodeResponse>('/geocoding/search/',{params:{q:query,limit}})}
  states(){return this.http.get<StateSummaryResponse>('/instructors/states/')}
  search(latitude:number,longitude:number,filters:SearchFilters){
    let params=new HttpParams().set('latitude',latitude).set('longitude',longitude).set('radius_km',filters.radius).set('category',filters.category).set('vehicle_available',filters.vehicleAvailable).set('ordering',filters.ordering);
    if(filters.transmission) params=params.set('transmission',filters.transmission);
    if(filters.maxPrice) params=params.set('max_price',filters.maxPrice);
    return this.http.get<SearchResponse>('/instructors/search/',{params});
  }
  profile(id:string){return this.http.get<Record<string,unknown>>(`/instructors/${id}/`)}
  whatsapp(id:string,category:string,source:string){return this.http.post<{destination_url:string;unique_contact:boolean}>(`/instructors/${id}/whatsapp-contact/`,{category,source})}
}
