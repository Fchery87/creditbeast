const CACHE_NAME = 'creditbeast-v1.0.0';
const RUNTIME_CACHE_NAME = 'creditbeast-runtime-v1.0.0';

// Resources to cache on install
const PRECACHE_RESOURCES = [
  '/',
  '/dashboard',
  '/dashboard/clients',
  '/dashboard/disputes',
  '/dashboard/analytics',
  '/dashboard/billing',
  '/dashboard/notifications',
  '/dashboard/documents',
  '/dashboard/compliance',
  '/dashboard/settings',
  '/manifest.json',
  '/offline.html'
];

// Install event - cache core resources
self.addEventListener('install', event => {
  console.log('Service Worker: Install event');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching core resources');
        return cache.addAll(PRECACHE_RESOURCES);
      })
      .then(() => {
        console.log('Service Worker: Skip waiting');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activate event');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Claiming clients');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip cross-origin requests
  if (url.origin !== self.location.origin) {
    return;
  }
  
  // Handle different types of requests
  if (request.url.includes('/api/')) {
    // API requests - Network first, cache fallback
    event.respondWith(networkFirstStrategy(request));
  } else if (request.destination === 'document') {
    // HTML pages - Network first with offline fallback
    event.respondWith(handleDocumentRequest(request));
  } else if (request.destination === 'image') {
    // Images - Cache first
    event.respondWith(cacheFirstStrategy(request));
  } else {
    // Other resources - Cache first
    event.respondWith(cacheFirstStrategy(request));
  }
});

// Network first strategy (good for APIs and fresh data)
async function networkFirstStrategy(request) {
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache', error);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response(
      JSON.stringify({ error: 'Offline - data not available' }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Cache first strategy (good for static resources)
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('Service Worker: Cache and network both failed', error);
    throw error;
  }
}

// Handle document requests with offline page fallback
async function handleDocumentRequest(request) {
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('Service Worker: Network failed for document, trying cache');
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for document requests
    return caches.match('/offline.html') || new Response(
      '<h1>Offline</h1><p>Please check your internet connection.</p>',
      { headers: { 'Content-Type': 'text/html' } }
    );
  }
}

// Push notification event
self.addEventListener('push', event => {
  console.log('Service Worker: Push event received');
  
  const options = {
    body: 'You have new updates from CreditBeast',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    tag: 'creditbeast-notification',
    data: {
      url: '/dashboard'
    },
    actions: [
      {
        action: 'view',
        title: 'View Dashboard'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };
  
  if (event.data) {
    try {
      const payload = event.data.json();
      options.body = payload.message || options.body;
      options.data = { ...options.data, ...payload.data };
    } catch (e) {
      console.log('Service Worker: Error parsing push data', e);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification('CreditBeast', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification click received');
  
  event.notification.close();
  
  const action = event.action;
  const data = event.notification.data;
  
  let urlToOpen = '/dashboard';
  
  if (action === 'view' && data && data.url) {
    urlToOpen = data.url;
  }
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // Check if a window is already open
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Open new window if none exists
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('Service Worker: Background sync event', event.tag);
  
  if (event.tag === 'offline-actions') {
    event.waitUntil(syncOfflineActions());
  }
});

// Sync offline actions when back online
async function syncOfflineActions() {
  try {
    // This would sync any queued actions when connection is restored
    const response = await fetch('/api/sync/offline-actions', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      console.log('Service Worker: Offline actions synced successfully');
    }
  } catch (error) {
    console.log('Service Worker: Failed to sync offline actions', error);
  }
}

// Message handling for communication with main thread
self.addEventListener('message', event => {
  console.log('Service Worker: Message received', event.data);
  
  if (event.data && event.data.type) {
    switch (event.data.type) {
      case 'SKIP_WAITING':
        self.skipWaiting();
        break;
      case 'GET_VERSION':
        event.ports[0].postMessage({ version: CACHE_NAME });
        break;
      case 'CACHE_URLS':
        event.waitUntil(
          caches.open(RUNTIME_CACHE_NAME).then(cache => {
            return cache.addAll(event.data.urls);
          })
        );
        break;
    }
  }
});

// Error handling
self.addEventListener('error', event => {
  console.error('Service Worker: Global error', event.error);
});

self.addEventListener('unhandledrejection', event => {
  console.error('Service Worker: Unhandled promise rejection', event.reason);
});