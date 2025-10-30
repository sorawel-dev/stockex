/**
 * Service Worker - Stockex Mobile PWA
 * ====================================
 * Gestion mode offline avec stratégie Cache-First pour assets
 * et Network-First pour données dynamiques.
 */

const CACHE_VERSION = 'stockex-v1.0.0';
const STATIC_CACHE = `stockex-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `stockex-dynamic-${CACHE_VERSION}`;
const OFFLINE_PAGE = '/stockex/mobile/offline';

// Assets à mettre en cache immédiatement
const STATIC_ASSETS = [
    '/stockex/mobile',
    '/stockex/mobile/offline',
    '/stockex/static/src/css/mobile.css',
    '/stockex/static/src/js/mobile-app.js',
    '/stockex/static/src/js/barcode-scanner.js',
    '/stockex/static/src/js/offline-storage.js',
    '/stockex/static/img/icon-192x192.png',
    '/stockex/static/img/icon-512x512.png',
    '/stockex/static/manifest.json',
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
    console.log('[SW] Installing Service Worker...', CACHE_VERSION);
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[SW] Static assets cached successfully');
                return self.skipWaiting(); // Active immédiatement
            })
            .catch((error) => {
                console.error('[SW] Error caching static assets:', error);
            })
    );
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating Service Worker...', CACHE_VERSION);
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                // Supprime les anciens caches
                return Promise.all(
                    cacheNames
                        .filter((cacheName) => {
                            return cacheName.startsWith('stockex-') && 
                                   cacheName !== STATIC_CACHE && 
                                   cacheName !== DYNAMIC_CACHE;
                        })
                        .map((cacheName) => {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Service Worker activated');
                return self.clients.claim(); // Prend contrôle des clients
            })
    );
});

// Interception des requêtes (Fetch)
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Ignore les requêtes non-HTTP
    if (!request.url.startsWith('http')) {
        return;
    }
    
    // Stratégie selon le type de ressource
    if (isStaticAsset(url.pathname)) {
        // Assets statiques : Cache-First
        event.respondWith(cacheFirst(request));
    } else if (isAPIRequest(url.pathname)) {
        // API : Network-First avec cache fallback
        event.respondWith(networkFirstWithCache(request));
    } else {
        // Autres : Network-First
        event.respondWith(networkFirst(request));
    }
});

/**
 * Détermine si c'est un asset statique
 */
function isStaticAsset(pathname) {
    return pathname.includes('/static/') || 
           pathname.endsWith('.css') || 
           pathname.endsWith('.js') || 
           pathname.endsWith('.png') || 
           pathname.endsWith('.jpg') ||
           pathname.endsWith('.svg') ||
           pathname.endsWith('.woff') ||
           pathname.endsWith('.woff2');
}

/**
 * Détermine si c'est une requête API
 */
function isAPIRequest(pathname) {
    return pathname.startsWith('/api/stockex/') ||
           pathname.includes('/jsonrpc');
}

/**
 * Stratégie Cache-First
 * Cherche d'abord dans le cache, sinon réseau
 */
async function cacheFirst(request) {
    try {
        const cache = await caches.open(STATIC_CACHE);
        const cached = await cache.match(request);
        
        if (cached) {
            console.log('[SW] Cache hit:', request.url);
            return cached;
        }
        
        console.log('[SW] Cache miss, fetching:', request.url);
        const response = await fetch(request);
        
        // Met en cache pour la prochaine fois
        if (response && response.status === 200) {
            const responseToCache = response.clone();
            cache.put(request, responseToCache);
        }
        
        return response;
    } catch (error) {
        console.error('[SW] Cache-First error:', error);
        return new Response('Offline - Asset not available', {
            status: 503,
            statusText: 'Service Unavailable',
        });
    }
}

/**
 * Stratégie Network-First
 * Essaie le réseau d'abord, sinon cache
 */
async function networkFirst(request) {
    try {
        const response = await fetch(request);
        
        // Met en cache dynamique pour offline
        if (response && response.status === 200) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', request.url);
        
        const cached = await caches.match(request);
        if (cached) {
            return cached;
        }
        
        // Page offline de secours
        if (request.mode === 'navigate') {
            const offlinePage = await caches.match(OFFLINE_PAGE);
            if (offlinePage) {
                return offlinePage;
            }
        }
        
        return new Response('Offline - No cached version', {
            status: 503,
            statusText: 'Service Unavailable',
        });
    }
}

/**
 * Stratégie Network-First avec cache pour API
 * Stocke les réponses API pour consultation offline
 */
async function networkFirstWithCache(request) {
    try {
        const response = await fetch(request);
        
        // Cache les réponses GET réussies
        if (response && response.status === 200 && request.method === 'GET') {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.log('[SW] API offline, checking cache:', request.url);
        
        // Tente le cache
        const cached = await caches.match(request);
        if (cached) {
            console.log('[SW] Returning cached API response');
            return cached;
        }
        
        // Réponse offline pour API
        return new Response(
            JSON.stringify({
                error: true,
                offline: true,
                message: 'Vous êtes hors ligne. Cette requête sera synchronisée quand vous serez en ligne.',
            }),
            {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' },
            }
        );
    }
}

/**
 * Synchronisation en arrière-plan (Background Sync)
 */
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'sync-inventories') {
        event.waitUntil(syncInventories());
    }
});

/**
 * Synchronise les inventaires locaux avec le serveur
 */
async function syncInventories() {
    try {
        console.log('[SW] Syncing pending inventories...');
        
        // Récupère les données depuis IndexedDB (via message aux clients)
        const clients = await self.clients.matchAll();
        
        clients.forEach((client) => {
            client.postMessage({
                type: 'SYNC_REQUESTED',
                timestamp: Date.now(),
            });
        });
        
        return Promise.resolve();
    } catch (error) {
        console.error('[SW] Sync error:', error);
        return Promise.reject(error);
    }
}

/**
 * Push Notifications (future)
 */
self.addEventListener('push', (event) => {
    console.log('[SW] Push notification received');
    
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'Stockex';
    const options = {
        body: data.body || 'Nouvelle notification',
        icon: '/stockex/static/img/icon-192x192.png',
        badge: '/stockex/static/img/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: data,
        actions: [
            { action: 'open', title: 'Ouvrir' },
            { action: 'close', title: 'Fermer' },
        ],
    };
    
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

/**
 * Gestion des clics sur notifications
 */
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/stockex/mobile')
        );
    }
});

/**
 * Messages depuis l'application
 */
self.addEventListener('message', (event) => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data.type === 'CACHE_URLS') {
        const urls = event.data.urls || [];
        cacheUrls(urls);
    }
});

/**
 * Met en cache des URLs spécifiques
 */
async function cacheUrls(urls) {
    const cache = await caches.open(DYNAMIC_CACHE);
    return cache.addAll(urls);
}

console.log('[SW] Service Worker loaded', CACHE_VERSION);
