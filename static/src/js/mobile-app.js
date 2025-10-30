/**
 * Application Mobile Stockex - PWA
 * =================================
 * Application principale gérant navigation, sync, et état offline
 */

class StockexMobileApp {
    constructor() {
        this.offlineStorage = new OfflineStorage();
        this.scanner = null;
        this.isOnline = navigator.onLine;
        this.currentInventory = null;
        this.syncInProgress = false;
        
        this.init();
    }
    
    async init() {
        console.log('[App] Initializing Stockex Mobile...');
        
        // Ouvre IndexedDB
        await this.offlineStorage.open();
        
        // Enregistre Service Worker
        this.registerServiceWorker();
        
        // Écoute événements réseau
        this.setupNetworkListeners();
        
        // Écoute messages Service Worker
        this.setupServiceWorkerListeners();
        
        // Sync automatique au démarrage si online
        if (this.isOnline) {
            this.syncPendingInventories();
        }
        
        console.log('[App] Initialized successfully');
    }
    
    /**
     * Enregistre le Service Worker
     */
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/stockex/sw.js', {
                    scope: '/stockex/',
                });
                
                console.log('[App] Service Worker registered:', registration.scope);
                
                // Écoute les mises à jour
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    console.log('[App] New Service Worker found');
                    
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // Nouvelle version disponible
                            this.notifyUpdate();
                        }
                    });
                });
            } catch (error) {
                console.error('[App] Service Worker registration failed:', error);
            }
        }
    }
    
    /**
     * Configuration des écouteurs réseau
     */
    setupNetworkListeners() {
        window.addEventListener('online', () => {
            console.log('[App] Back online');
            this.isOnline = true;
            this.showNotification('Connexion rétablie', 'success');
            this.syncPendingInventories();
        });
        
        window.addEventListener('offline', () => {
            console.log('[App] Gone offline');
            this.isOnline = false;
            this.showNotification('Mode hors ligne activé', 'warning');
        });
    }
    
    /**
     * Écoute messages du Service Worker
     */
    setupServiceWorkerListeners() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', (event) => {
                console.log('[App] Message from SW:', event.data);
                
                if (event.data.type === 'SYNC_REQUESTED') {
                    this.syncPendingInventories();
                }
            });
        }
    }
    
    /**
     * Synchronise les inventaires en attente
     */
    async syncPendingInventories() {
        if (!this.isOnline || this.syncInProgress) {
            return;
        }
        
        this.syncInProgress = true;
        this.showNotification('Synchronisation en cours...', 'info');
        
        try {
            const pending = await this.offlineStorage.getPendingInventories();
            
            if (pending.length === 0) {
                console.log('[App] No pending inventories to sync');
                this.syncInProgress = false;
                return;
            }
            
            console.log(`[App] Syncing ${pending.length} inventories...`);
            
            const response = await fetch('/api/mobile/inventories/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        inventories: pending,
                    },
                }),
            });
            
            const result = await response.json();
            
            if (result.result && result.result.success) {
                // Marque comme synchronisés
                for (const synced of result.result.synced) {
                    await this.offlineStorage.markSynced(synced.local_id, synced.server_id);
                }
                
                this.showNotification(
                    `${result.result.synced_count} inventaire(s) synchronisé(s)`,
                    'success'
                );
            } else {
                throw new Error('Sync failed');
            }
            
        } catch (error) {
            console.error('[App] Sync error:', error);
            this.showNotification('Erreur de synchronisation', 'error');
        } finally {
            this.syncInProgress = false;
        }
    }
    
    /**
     * Recherche un produit (online ou cache)
     */
    async searchProduct(barcode) {
        try {
            // Essaie d'abord le cache
            const cached = await this.offlineStorage.findProductByBarcode(barcode);
            if (cached) {
                console.log('[App] Product found in cache:', cached);
                return cached;
            }
            
            // Si online, requête serveur
            if (this.isOnline) {
                const response = await fetch('/api/mobile/products/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            barcode: barcode,
                        },
                    }),
                });
                
                const result = await response.json();
                
                if (result.result && result.result.found) {
                    const product = result.result.product;
                    
                    // Met en cache
                    await this.offlineStorage.cacheProduct(product);
                    
                    return product;
                }
            }
            
            return null;
        } catch (error) {
            console.error('[App] Product search error:', error);
            throw error;
        }
    }
    
    /**
     * Ajoute une ligne d'inventaire
     */
    async addInventoryLine(productId, qty) {
        if (!this.currentInventory) {
            throw new Error('No active inventory');
        }
        
        const line = {
            product_id: productId,
            real_qty: qty,
        };
        
        if (this.isOnline && this.currentInventory.server_id) {
            // Sync immédiat si online
            try {
                const response = await fetch('/api/mobile/inventory/add-line', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            inventory_id: this.currentInventory.server_id,
                            product_id: productId,
                            real_qty: qty,
                        },
                    }),
                });
                
                const result = await response.json();
                
                if (result.result && result.result.success) {
                    return result.result.line;
                }
            } catch (error) {
                console.error('[App] Error adding line online:', error);
                // Fallback vers stockage local
            }
        }
        
        // Stockage local
        const existingLineIndex = this.currentInventory.lines.findIndex(
            l => l.product_id === productId
        );
        
        if (existingLineIndex >= 0) {
            this.currentInventory.lines[existingLineIndex].real_qty = qty;
        } else {
            this.currentInventory.lines.push(line);
        }
        
        await this.offlineStorage.saveInventory(this.currentInventory);
        
        return line;
    }
    
    /**
     * Affiche une notification
     */
    showNotification(message, type = 'info') {
        // Utilise notifications navigateur si autorisé
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Stockex Mobile', {
                body: message,
                icon: '/stockex/static/img/icon-192x192.png',
                badge: '/stockex/static/img/badge-72x72.png',
            });
        }
        
        // Affiche aussi dans UI
        const notifElement = document.createElement('div');
        notifElement.className = `notification notification-${type}`;
        notifElement.textContent = message;
        notifElement.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 15px 25px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#17a2b8'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            animation: slideDown 0.3s ease-out;
        `;
        
        document.body.appendChild(notifElement);
        
        setTimeout(() => {
            notifElement.style.animation = 'slideUp 0.3s ease-out';
            setTimeout(() => notifElement.remove(), 300);
        }, 3000);
    }
    
    /**
     * Notifie qu'une nouvelle version est disponible
     */
    notifyUpdate() {
        const updateBanner = document.createElement('div');
        updateBanner.innerHTML = `
            <div style="
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: #007bff;
                color: white;
                padding: 15px;
                text-align: center;
                z-index: 9999;
            ">
                <p style="margin: 0 0 10px 0;">
                    <strong>Nouvelle version disponible !</strong>
                </p>
                <button id="btn-update-app" style="
                    background: white;
                    color: #007bff;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    cursor: pointer;
                ">
                    Mettre à jour maintenant
                </button>
            </div>
        `;
        
        document.body.appendChild(updateBanner);
        
        document.getElementById('btn-update-app').addEventListener('click', () => {
            if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
                navigator.serviceWorker.controller.postMessage({
                    type: 'SKIP_WAITING',
                });
                
                window.location.reload();
            }
        });
    }
    
    /**
     * Demande permission notifications
     */
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log('[App] Notification permission:', permission);
            return permission;
        }
        return Notification.permission;
    }
}

// Initialise l'app au chargement
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.stockexApp = new StockexMobileApp();
    });
} else {
    window.stockexApp = new StockexMobileApp();
}

// Style animations
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideDown {
        from { transform: translate(-50%, -100%); opacity: 0; }
        to { transform: translate(-50%, 0); opacity: 1; }
    }
    
    @keyframes slideUp {
        from { transform: translate(-50%, 0); opacity: 1; }
        to { transform: translate(-50%, -100%); opacity: 0; }
    }
`;
document.head.appendChild(styleSheet);
