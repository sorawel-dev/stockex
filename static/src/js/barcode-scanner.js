/**
 * Scanner de Codes-Barres - Stockex Mobile
 * =========================================
 * Utilise QuaggaJS pour scanner codes-barres via caméra mobile.
 * 
 * Formats supportés : EAN-13, EAN-8, Code 128, Code 39, UPC
 */

class BarcodeScanner {
    constructor(options = {}) {
        this.videoElement = options.videoElement || null;
        this.onDetected = options.onDetected || null;
        this.onError = options.onError || null;
        this.isScanning = false;
        this.lastScannedCode = null;
        this.lastScannedTime = 0;
        this.debounceMs = options.debounceMs || 1000; // Évite doubles scans
    }
    
    /**
     * Initialise Quagga et démarre le scan
     */
    start() {
        if (this.isScanning) {
            console.warn('[Scanner] Already scanning');
            return;
        }
        
        if (!this.videoElement) {
            console.error('[Scanner] Video element not provided');
            return;
        }
        
        const config = {
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: this.videoElement,
                constraints: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "environment", // Caméra arrière
                    aspectRatio: { ideal: 16/9 },
                },
            },
            decoder: {
                readers: [
                    "ean_reader",       // EAN-13, EAN-8
                    "ean_8_reader",
                    "code_128_reader",  // Code 128
                    "code_39_reader",   // Code 39
                    "upc_reader",       // UPC
                    "upc_e_reader",
                ],
                debug: {
                    showCanvas: true,
                    showPatches: false,
                    showFoundPatches: false,
                    showSkeleton: false,
                    showLabels: false,
                    showPatchLabels: false,
                    showRemainingPatchLabels: false,
                    boxFromPatches: {
                        showTransformed: true,
                        showTransformedBox: true,
                        showBB: true,
                    },
                },
            },
            locator: {
                patchSize: "medium",
                halfSample: true,
            },
            numOfWorkers: navigator.hardwareConcurrency || 4,
            frequency: 10, // Scans par seconde
        };
        
        Quagga.init(config, (err) => {
            if (err) {
                console.error('[Scanner] Initialization failed:', err);
                if (this.onError) {
                    this.onError(err);
                }
                return;
            }
            
            console.log('[Scanner] Initialization finished. Starting...');
            Quagga.start();
            this.isScanning = true;
            
            // Événement détection code-barres
            Quagga.onDetected(this.handleDetection.bind(this));
        });
    }
    
    /**
     * Gère la détection d'un code-barres
     */
    handleDetection(result) {
        const code = result.codeResult.code;
        const format = result.codeResult.format;
        const now = Date.now();
        
        // Debounce : ignore si même code scanné récemment
        if (code === this.lastScannedCode && (now - this.lastScannedTime) < this.debounceMs) {
            return;
        }
        
        this.lastScannedCode = code;
        this.lastScannedTime = now;
        
        console.log('[Scanner] Code detected:', code, format);
        
        // Feedback visuel et sonore
        this.playBeep();
        this.vibrate();
        
        // Callback
        if (this.onDetected) {
            this.onDetected(code, format);
        }
    }
    
    /**
     * Arrête le scanner
     */
    stop() {
        if (!this.isScanning) {
            return;
        }
        
        Quagga.stop();
        this.isScanning = false;
        console.log('[Scanner] Stopped');
    }
    
    /**
     * Feedback sonore
     */
    playBeep() {
        // Utilise Web Audio API
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800; // Fréquence Hz
        oscillator.type = 'square';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    }
    
    /**
     * Feedback vibration
     */
    vibrate() {
        if ('vibrate' in navigator) {
            navigator.vibrate(200); // 200ms
        }
    }
    
    /**
     * Bascule flash/torche (si disponible)
     */
    async toggleFlash() {
        try {
            const track = Quagga.CameraAccess.getActiveTrack();
            if (!track) {
                console.warn('[Scanner] No active camera track');
                return;
            }
            
            const capabilities = track.getCapabilities();
            if (!capabilities.torch) {
                console.warn('[Scanner] Torch not supported');
                return;
            }
            
            const constraints = track.getConstraints();
            const currentTorch = constraints.advanced?.[0]?.torch || false;
            
            await track.applyConstraints({
                advanced: [{ torch: !currentTorch }],
            });
            
            console.log('[Scanner] Flash toggled:', !currentTorch);
        } catch (error) {
            console.error('[Scanner] Flash toggle error:', error);
        }
    }
}

/**
 * Gestion hors ligne - IndexedDB
 * ================================
 * Stocke les inventaires localement quand offline
 */
class OfflineStorage {
    constructor(dbName = 'stockex-mobile', version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }
    
    /**
     * Ouvre la base de données IndexedDB
     */
    async open() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);
            
            request.onerror = () => {
                console.error('[OfflineStorage] Error opening DB:', request.error);
                reject(request.error);
            };
            
            request.onsuccess = () => {
                this.db = request.result;
                console.log('[OfflineStorage] DB opened');
                resolve(this.db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Store inventaires en attente de sync
                if (!db.objectStoreNames.contains('pending_inventories')) {
                    const inventoryStore = db.createObjectStore('pending_inventories', {
                        keyPath: 'local_id',
                        autoIncrement: false,
                    });
                    inventoryStore.createIndex('timestamp', 'timestamp', { unique: false });
                    inventoryStore.createIndex('synced', 'synced', { unique: false });
                }
                
                // Store produits en cache
                if (!db.objectStoreNames.contains('cached_products')) {
                    const productStore = db.createObjectStore('cached_products', {
                        keyPath: 'id',
                    });
                    productStore.createIndex('barcode', 'barcode', { unique: true });
                    productStore.createIndex('code', 'code', { unique: false });
                }
                
                console.log('[OfflineStorage] DB upgraded to version', this.version);
            };
        });
    }
    
    /**
     * Sauvegarde un inventaire localement
     */
    async saveInventory(inventory) {
        if (!this.db) await this.open();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['pending_inventories'], 'readwrite');
            const store = transaction.objectStore('pending_inventories');
            
            const inventoryData = {
                local_id: inventory.local_id || `temp-${Date.now()}`,
                location_id: inventory.location_id,
                date: inventory.date || new Date().toISOString().split('T')[0],
                lines: inventory.lines || [],
                timestamp: Date.now(),
                synced: false,
            };
            
            const request = store.put(inventoryData);
            
            request.onsuccess = () => {
                console.log('[OfflineStorage] Inventory saved:', inventoryData.local_id);
                resolve(inventoryData);
            };
            
            request.onerror = () => {
                console.error('[OfflineStorage] Error saving inventory:', request.error);
                reject(request.error);
            };
        });
    }
    
    /**
     * Récupère les inventaires en attente de sync
     */
    async getPendingInventories() {
        if (!this.db) await this.open();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['pending_inventories'], 'readonly');
            const store = transaction.objectStore('pending_inventories');
            const index = store.index('synced');
            const request = index.getAll(false); // synced = false
            
            request.onsuccess = () => {
                console.log('[OfflineStorage] Pending inventories:', request.result.length);
                resolve(request.result);
            };
            
            request.onerror = () => {
                console.error('[OfflineStorage] Error getting pending:', request.error);
                reject(request.error);
            };
        });
    }
    
    /**
     * Marque un inventaire comme synchronisé
     */
    async markSynced(local_id, server_id) {
        if (!this.db) await this.open();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['pending_inventories'], 'readwrite');
            const store = transaction.objectStore('pending_inventories');
            const request = store.get(local_id);
            
            request.onsuccess = () => {
                const data = request.result;
                if (data) {
                    data.synced = true;
                    data.server_id = server_id;
                    data.synced_at = Date.now();
                    
                    const updateRequest = store.put(data);
                    
                    updateRequest.onsuccess = () => {
                        console.log('[OfflineStorage] Marked as synced:', local_id);
                        resolve(data);
                    };
                    
                    updateRequest.onerror = () => {
                        reject(updateRequest.error);
                    };
                } else {
                    resolve(null);
                }
            };
            
            request.onerror = () => {
                reject(request.error);
            };
        });
    }
    
    /**
     * Cache un produit localement
     */
    async cacheProduct(product) {
        if (!this.db) await this.open();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['cached_products'], 'readwrite');
            const store = transaction.objectStore('cached_products');
            const request = store.put(product);
            
            request.onsuccess = () => {
                console.log('[OfflineStorage] Product cached:', product.id);
                resolve(product);
            };
            
            request.onerror = () => {
                reject(request.error);
            };
        });
    }
    
    /**
     * Recherche produit en cache par barcode
     */
    async findProductByBarcode(barcode) {
        if (!this.db) await this.open();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['cached_products'], 'readonly');
            const store = transaction.objectStore('cached_products');
            const index = store.index('barcode');
            const request = index.get(barcode);
            
            request.onsuccess = () => {
                resolve(request.result || null);
            };
            
            request.onerror = () => {
                reject(request.error);
            };
        });
    }
}

// Export global
window.BarcodeScanner = BarcodeScanner;
window.OfflineStorage = OfflineStorage;
