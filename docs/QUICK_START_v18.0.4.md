# 🚀 Guide de Démarrage Rapide - Nouveautés v18.0.4.0.0

## 📦 Gestion Lots & Traçabilité

### Inventaire par Lot/Série

#### Pour les produits pharmaceutiques/alimentaires avec dates d'expiration

1. **Prérequis** : Votre produit doit avoir `Suivi par Lot/Série` activé
   - Menu : `Inventaire > Produits > Produits`
   - Onglet `Inventaire` → `Suivi` = `Par Lot` ou `Par Numéro de Série`

2. **Créer un Inventaire avec Lots**

   ```
   Menu : Stockex > Inventaires > Créer
   
   1. Sélectionnez l'emplacement
   2. Ajoutez une ligne de produit (avec tracking=lot)
   3. Cliquez sur le bouton "Générer Lots" (en haut)
      → Les lots existants sont automatiquement chargés
   
   4. OU remplir manuellement l'onglet "Détail par Lot"
      → Sélectionnez le lot
      → Saisissez la quantité réelle
   
   5. La quantité réelle totale est calculée automatiquement
   ```

3. **Alertes Expiration Automatiques**

   Les lignes de lot sont colorées selon la date d'expiration :
   - 🔴 **Rouge** : Lot expiré (< aujourd'hui)
   - 🟡 **Jaune** : Alerte expiration (< 60 jours)
   - 🟢 **Vert** : Lot OK (> 60 jours)

4. **Menu "Lots Expirant"**

   ```
   Menu : Stockex > Rapports > Lots Expirant
   
   → Liste tous les lots expirant dans les 60 prochains jours
   → Permet action rapide (destruction, vente rapide)
   ```

### Traçabilité Réglementaire

#### Pour conformité pharma/alimentaire

1. **Enrichir un Lot avec Informations Conformité**

   ```
   Menu : Inventaire > Produits > Lots/Numéros de Série
   
   1. Sélectionnez un lot
   2. Onglet "Traçabilité & Conformité" :
   
   Traçabilité Amont :
   - N° Lot Fournisseur : PHARMA-2025-ABC
   - N° Lot Interne : INT-001-2025
   - Date Fabrication : 2025-01-15
   - Date Réception : 2025-02-10
   
   Conformité Qualité :
   - Statut Qualité : Approuvé / Quarantaine / Rejeté
   - Certificat d'Analyse : Joindre PDF
   - Notes Conformité : "Conforme GMP, audit validé"
   
   Alertes :
   - Alerte Expiration (jours) : 60 (modifiable)
   ```

2. **Historique Inventaires d'un Lot**

   ```
   Dans le formulaire d'un lot :
   → Bouton "Historique Inventaires" (en haut)
   → Affiche tous les comptages historiques du lot
   ```

3. **Rappel Produit (Product Recall)**

   ```
   Scénario : Rappel lot fournisseur "PHARMA-2025-ABC"
   
   1. Menu : Inventaire > Produits > Lots/Numéros de Série
   2. Rechercher : N° Lot Fournisseur = "PHARMA-2025-ABC"
   3. Bouton "Historique Inventaires" :
      → Liste tous les inventaires ayant compté ce lot
      → Emplacements concernés
      → Quantités historiques
   
   4. Identifier clients livrés (via Odoo Sales/Inventory)
   5. Traçabilité complète amont/aval disponible
   ```

---

## 📊 Dashboard Analytique

### KPIs Temps Réel

#### Visualisez vos performances inventaire

1. **Accéder au Dashboard**

   ```
   Menu : Stockex > 📊 Analytics
   
   → Dashboard s'ouvre directement
   → Période par défaut : "Ce Mois"
   ```

2. **Changer la Période d'Analyse**

   ```
   En haut du formulaire :
   - Aujourd'hui
   - Cette Semaine
   - Ce Mois (défaut)
   - Ce Trimestre
   - Cette Année
   - Personnalisé (sélectionnez dates début/fin)
   
   → KPIs se recalculent automatiquement
   ```

3. **Les 5 KPIs Essentiels**

   | KPI | Interprétation |
   |-----|----------------|
   | **Total Inventaires** | Nombre total d'inventaires créés |
   | **Inventaires Validés** | Nombre validés (complétés) |
   | **Précision Moyenne** | % de précision des comptages<br>🎯 Objectif : > 95% |
   | **Valeur Écarts** | Somme valorisation écarts (€)<br>⚠️ Négatif = manquants |
   | **Rotation Stock** | Combien de fois stock renouvelé<br>📈 Plus élevé = meilleur |

4. **Graphiques**

   **Onglet "📈 Tendances"** :
   - Évolution nombre d'inventaires sur 12 mois
   - Identifiez pics/creux d'activité
   
   **Onglet "💰 Valorisation"** :
   - Top 10 catégories par valeur stock
   - Identifiez catégories à forte valeur
   
   **Onglet "📊 Écarts"** :
   - Top 10 catégories par écarts (€)
   - Rouge = écarts négatifs (manquants)
   - Vert = écarts positifs (surplus)
   - Identifiez catégories problématiques

5. **Actions Rapides**

   ```
   Bouton "↻ Actualiser" : Force recalcul des KPIs
   Bouton "Voir Inventaires" : Liste inventaires de la période
   ```

### Exemples Interprétation

**Scénario 1 : Précision Faible**
```
KPI Précision Moyenne : 78%  ⚠️

Actions :
1. Onglet "Écarts" → Identifier catégories problématiques
2. Formation équipe comptage
3. Audit process (double comptage)
```

**Scénario 2 : Rotation Faible**
```
KPI Rotation Stock : 0.5 fois/mois  📉

Interprétation :
- Stock renouvelé seulement 2 fois/an
- Surstockage possible
- Capital immobilisé

Actions :
1. Onglet "Valorisation" → Identifier catégories dormantes
2. Promotions/destockage
3. Réduire commandes
```

**Scénario 3 : Écarts Négatifs Importants**
```
KPI Valeur Écarts : -15,000€  🔴

Interprétation :
- Manquants significatifs
- Vols possibles / erreurs saisie

Actions :
1. Onglet "Écarts" → Top catégories négatives
2. Audit sécurité entrepôt
3. Vérifier process réception/expédition
```

---

## 🔌 API REST

### Intégrations Externes

#### Connectez vos systèmes tiers à Stockex

### Authentification

**Actuellement** : Session Odoo standard (cookies)

```bash
# Connexion via curl
curl -X POST http://votredomaine.com/web/login \
  -d "login=admin&password=admin"
  
# Les requêtes suivantes utilisent les cookies de session
```

**TODO v18.0.5** : JWT/OAuth2

### Endpoints Disponibles

#### 1. Liste Inventaires

```bash
GET /api/stockex/inventories

Paramètres (optionnels) :
- state : draft, in_progress, approved, validated
- location_id : ID emplacement
- date_from : YYYY-MM-DD
- date_to : YYYY-MM-DD
- limit : max résultats (défaut: 100)
- offset : pagination (défaut: 0)

Exemple :
curl http://votredomaine.com/api/stockex/inventories?state=validated&limit=50
```

**Réponse JSON** :
```json
{
  "total": 125,
  "limit": 50,
  "offset": 0,
  "inventories": [
    {
      "id": 42,
      "name": "INV/2025/001",
      "date": "2025-10-28",
      "location_id": 8,
      "location_name": "Entrepôt Principal/Stock",
      "state": "validated",
      "state_display": "Validé",
      "total_lines": 156,
      "total_difference_value": -1250.50,
      "user_id": 2,
      "user_name": "Marc Dupont"
    }
  ]
}
```

#### 2. Détail Inventaire

```bash
GET /api/stockex/inventories/<id>

Paramètres :
- include_lines : true/false (défaut: true)

Exemple :
curl http://votredomaine.com/api/stockex/inventories/42?include_lines=true
```

**Réponse JSON** :
```json
{
  "id": 42,
  "name": "INV/2025/001",
  "date": "2025-10-28",
  "state": "validated",
  "total_lines": 156,
  "total_difference_value": -1250.50,
  "lines": [
    {
      "id": 512,
      "product_id": 89,
      "product_code": "ABC-001",
      "product_name": "Produit Test",
      "theoretical_qty": 100.0,
      "real_qty": 95.0,
      "difference": -5.0,
      "standard_price": 50.0,
      "difference_value": -250.0,
      "state": "validated"
    }
  ]
}
```

#### 3. Créer Inventaire

```bash
POST /api/stockex/inventories
Content-Type: application/json

Body JSON :
{
  "location_id": 8,
  "date": "2025-10-28",
  "lines": [
    {
      "product_id": 89,
      "real_qty": 95
    }
  ]
}

Exemple :
curl -X POST http://votredomaine.com/api/stockex/inventories \
  -H "Content-Type: application/json" \
  -d '{"location_id": 8, "lines": [{"product_id": 89, "real_qty": 95}]}'
```

**Réponse JSON** :
```json
{
  "success": true,
  "inventory_id": 43,
  "name": "INV/2025/002"
}
```

#### 4. Liste Produits

```bash
GET /api/stockex/products

Paramètres :
- search : recherche nom ou code
- category_id : ID catégorie
- limit : max résultats (défaut: 100)

Exemple :
curl "http://votredomaine.com/api/stockex/products?search=ABC&limit=20"
```

#### 5. Liste Emplacements

```bash
GET /api/stockex/locations

Paramètres :
- warehouse_id : ID entrepôt (filtre emplacements enfants)

Exemple :
curl http://votredomaine.com/api/stockex/locations?warehouse_id=1
```

#### 6. KPIs Globaux

```bash
GET /api/stockex/kpis

Exemple :
curl http://votredomaine.com/api/stockex/kpis
```

**Réponse JSON** :
```json
{
  "total_inventories": 125,
  "pending_validations": 8,
  "average_accuracy": 94.5,
  "total_variance_value": -3250.75
}
```

### Gestion Erreurs

**Codes HTTP** :
- `200` : Succès
- `400` : Requête invalide (params manquants)
- `404` : Ressource introuvable
- `500` : Erreur serveur

**Réponse Erreur** :
```json
{
  "error": true,
  "message": "Inventaire introuvable"
}
```

### Cas d'Usage

**Intégration Tableau de Bord BI Externe** :
```python
# Python - Récupérer KPIs pour Power BI
import requests

response = requests.get('http://votredomaine.com/api/stockex/kpis')
kpis = response.json()

print(f"Précision : {kpis['average_accuracy']}%")
```

**Synchronisation ERP Externe** :
```javascript
// JavaScript - Créer inventaire depuis SAP
fetch('http://votredomaine.com/api/stockex/inventories', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    location_id: 8,
    lines: sapData.map(item => ({
      product_id: item.odoo_product_id,
      real_qty: item.quantity
    }))
  })
})
.then(res => res.json())
.then(data => console.log('Inventaire créé:', data.inventory_id));
```

---

## 📋 Checklist Mise en Production

### Avant Activation

- [ ] Formation équipe (2h)
  - [ ] Gestion lots/séries (1h)
  - [ ] Dashboard analytics (30min)
  - [ ] API REST (30min si applicable)

- [ ] Configuration
  - [ ] Activer suivi lots pour produits pharma/alimentaire
  - [ ] Configurer alertes expiration (défaut 60j, modifiable)
  - [ ] Tester génération automatique lignes lot

- [ ] Tests
  - [ ] Créer inventaire test avec lots
  - [ ] Vérifier alertes expiration
  - [ ] Ouvrir dashboard analytics
  - [ ] Tester 1 endpoint API (optionnel)

### Après Activation

- [ ] Monitoring
  - [ ] Surveiller dashboard "📊 Analytics" quotidiennement
  - [ ] Vérifier menu "Lots Expirant" hebdomadairement
  - [ ] KPI Précision : objectif > 95%

- [ ] Actions Correctives
  - [ ] Si précision < 90% : Formation équipe
  - [ ] Si écarts > 5% valeur stock : Audit process
  - [ ] Si lots expirés non traités : Alerte manager

---

## 🆘 Support

**Questions fréquentes** : Voir `docs/FAQ_LOTS_EXPIRATION.md` (à créer)  
**Documentation technique** : Voir `docs/IMPLEMENTATION_REPORT.md`  
**Bugs** : GitHub Issues ou contact Sorawel

**Contact** :
- Email : dev@sorawel.com
- Website : https://www.sorawel.com

---

**Version du guide** : 1.0  
**Compatible avec** : Stockex v18.0.4.0.0+  
**Dernière mise à jour** : 2025-10-28
