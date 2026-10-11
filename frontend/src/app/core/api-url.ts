import { environment } from '../../environments/environment';

export function apiUrl(path: string): string {
  return `${environment.apiBaseUrl}${path}`;
}

export function publicMediaUrl(path: string | null): string | null {
  if (!path || !environment.mobile || !path.startsWith('/') || path.startsWith('//')) return path;
  return new URL(path, environment.apiBaseUrl).toString();
}
