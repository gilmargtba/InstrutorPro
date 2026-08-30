import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

export interface SearchFilters { location:string; radius:number; category:string; transmission:string; vehicleAvailable:boolean; }
export interface SearchInstructor { id:string;display_name:string;latitude:number;longitude:number;distance_km:number;categories:string[];transmission:string;vehicle_available:boolean;demo_rating:number;demo_price:number;availability_summary:string;demo:boolean; }
interface GeocodeResponse { results:{label:string;latitude:number;longitude:number}[];provider:string }
interface SearchResponse { count:number;results:SearchInstructor[] }
export interface InstructorStateSummary { uf:string;count:number;search_location:string }
interface StateSummaryResponse { states:InstructorStateSummary[] }

@Injectable({providedIn:'root'})
export class InstructorSearchProvider {
  private readonly http=inject(HttpClient);
  geocode(query:string){return this.http.get<GeocodeResponse>('/geocoding/search/',{params:{q:query}})}
  states(){return this.http.get<StateSummaryResponse>('/instructors/states/')}
  search(latitude:number,longitude:number,filters:SearchFilters){
    let params=new HttpParams().set('latitude',latitude).set('longitude',longitude).set('radius_km',filters.radius).set('category',filters.category).set('vehicle_available',filters.vehicleAvailable);
    if(filters.transmission) params=params.set('transmission',filters.transmission);
    return this.http.get<SearchResponse>('/instructors/search/',{params});
  }
}
