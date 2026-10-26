import { importLibrary, setOptions } from '@googlemaps/js-api-loader';

let configured = false;

export async function loadGoogleMaps(key: string, mapId: string) {
  if (!configured) {
    setOptions({ key, language: 'pt-BR', region: 'BR', mapIds: [mapId] });
    configured = true;
  }
  let timer: ReturnType<typeof setTimeout> | undefined;
  const deadline = new Promise<never>((_, reject) => {
    timer = setTimeout(() => reject(new Error('Google Maps loading timed out.')), 8000);
  });
  try {
    return await Promise.race([Promise.all([importLibrary('maps'), importLibrary('marker')]), deadline]);
  } finally {
    clearTimeout(timer);
  }
}
