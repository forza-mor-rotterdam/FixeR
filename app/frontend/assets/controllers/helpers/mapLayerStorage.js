const KAART_LAYER_STORAGE_PREFIX = 'kaartLayer:'

export function getMapLayerStorageKey(mapLayerType) {
  return `${KAART_LAYER_STORAGE_PREFIX}${mapLayerType}`
}

export function getStoredMapLayerState(mapLayerType) {
  return sessionStorage.getItem(getMapLayerStorageKey(mapLayerType)) === 'true'
}

export function setStoredMapLayerState(mapLayerType, enabled) {
  sessionStorage.setItem(getMapLayerStorageKey(mapLayerType), enabled ? 'true' : 'false')
}
