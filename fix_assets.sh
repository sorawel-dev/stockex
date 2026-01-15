#!/bin/bash
# Script de dépannage automatique pour page blanche Odoo
# Usage: ./fix_assets.sh [database_name] [container_name]

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paramètres
DB_NAME="${1:-odoo}"
CONTAINER_NAME="${2:-odoo19}"

echo -e "${YELLOW}🔧 Démarrage du dépannage Odoo...${NC}"
echo "Base de données: $DB_NAME"
echo "Container: $CONTAINER_NAME"
echo ""

# 1. Vérifier que le container existe
echo -e "${YELLOW}📦 Vérification du container...${NC}"
if ! docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}❌ Container '$CONTAINER_NAME' introuvable${NC}"
    echo "Containers disponibles:"
    docker ps -a --format "{{.Names}}"
    exit 1
fi

# 2. Vérifier que le container tourne
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${YELLOW}⚠️  Container arrêté, démarrage...${NC}"
    docker start "$CONTAINER_NAME"
    sleep 5
fi
echo -e "${GREEN}✅ Container actif${NC}"
echo ""

# 3. Vérifier l'espace disque
echo -e "${YELLOW}💾 Vérification espace disque...${NC}"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}⚠️  Espace disque faible: ${DISK_USAGE}%${NC}"
fi
echo ""

# 4. Sauvegarder les logs actuels
echo -e "${YELLOW}📝 Sauvegarde des logs...${NC}"
docker logs "$CONTAINER_NAME" --tail 200 > "/tmp/odoo_logs_before_fix_$(date +%Y%m%d_%H%M%S).log"
echo -e "${GREEN}✅ Logs sauvegardés dans /tmp/${NC}"
echo ""

# 5. Méthode 1: Update du module
echo -e "${YELLOW}🔄 Tentative 1: Update module stockex...${NC}"
if docker exec "$CONTAINER_NAME" odoo-bin -d "$DB_NAME" -u stockex --stop-after-init --log-level=warn 2>&1 | tee /tmp/odoo_update.log; then
    echo -e "${GREEN}✅ Update réussi${NC}"
    
    # Redémarrer le container
    echo -e "${YELLOW}🔄 Redémarrage du container...${NC}"
    docker restart "$CONTAINER_NAME"
    sleep 15
    
    # Vérifier si la page fonctionne
    echo -e "${YELLOW}🌐 Test de connexion...${NC}"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login | grep -q "200"; then
        echo -e "${GREEN}✅✅✅ PROBLÈME RÉSOLU ! La page fonctionne.${NC}"
        echo ""
        echo "Vérifiez dans votre navigateur: http://localhost:8069"
        exit 0
    fi
fi

# 6. Méthode 2: Nettoyage cache assets
echo -e "${YELLOW}🧹 Tentative 2: Nettoyage cache assets...${NC}"
docker exec "$CONTAINER_NAME" bash -c "rm -rf /var/lib/odoo/.local/share/Odoo/filestore/$DB_NAME/assets/* || true"
docker exec "$CONTAINER_NAME" bash -c "rm -rf /home/odoo/.local/share/Odoo/filestore/$DB_NAME/assets/* || true"
echo -e "${GREEN}✅ Cache nettoyé${NC}"

# Redémarrer
echo -e "${YELLOW}🔄 Redémarrage du container...${NC}"
docker restart "$CONTAINER_NAME"
sleep 15

# Test
echo -e "${YELLOW}🌐 Test de connexion...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login | grep -q "200"; then
    echo -e "${GREEN}✅✅✅ PROBLÈME RÉSOLU ! La page fonctionne.${NC}"
    exit 0
fi

# 7. Méthode 3: Rollback Git (dernier recours)
echo -e "${YELLOW}⚠️  Tentative 3: Rollback Git au commit stable...${NC}"
echo "Cette action va revenir au commit bf9c503 (avant les nouvelles cartes)"
read -p "Continuer ? (o/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    # Trouver le chemin du module
    MODULE_PATH=$(docker exec "$CONTAINER_NAME" python3 -c "import sys; print([p for p in sys.path if 'stockex' in p][0] if any('stockex' in p for p in sys.path) else '/mnt/extra-addons/stockex')" 2>/dev/null || echo "/mnt/extra-addons/stockex")
    
    echo "Chemin module: $MODULE_PATH"
    
    # Rollback
    docker exec "$CONTAINER_NAME" bash -c "cd $MODULE_PATH && git fetch && git checkout bf9c503"
    
    # Update + redémarrage
    docker exec "$CONTAINER_NAME" odoo-bin -d "$DB_NAME" -u stockex --stop-after-init --log-level=warn
    docker restart "$CONTAINER_NAME"
    sleep 15
    
    # Test final
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login | grep -q "200"; then
        echo -e "${GREEN}✅✅✅ ROLLBACK RÉUSSI ! La page fonctionne.${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Note: Le module est maintenant au commit bf9c503 (version stable)${NC}"
        echo "Pour revenir à la dernière version:"
        echo "  docker exec $CONTAINER_NAME bash -c \"cd $MODULE_PATH && git checkout main && git pull\""
        echo "  docker exec $CONTAINER_NAME odoo-bin -d $DB_NAME -u stockex --stop-after-init"
        echo "  docker restart $CONTAINER_NAME"
        exit 0
    fi
fi

# Si rien n'a fonctionné
echo ""
echo -e "${RED}❌ ÉCHEC: Aucune méthode n'a résolu le problème${NC}"
echo ""
echo "Actions recommandées:"
echo "1. Consulter les logs détaillés:"
echo "   docker logs $CONTAINER_NAME --tail 100"
echo ""
echo "2. Vérifier les logs PostgreSQL:"
echo "   docker logs <postgres_container> --tail 100"
echo ""
echo "3. Vérifier la configuration Odoo:"
echo "   docker exec $CONTAINER_NAME cat /etc/odoo/odoo.conf"
echo ""
echo "4. Logs sauvegardés dans:"
echo "   /tmp/odoo_logs_before_fix_*.log"
echo "   /tmp/odoo_update.log"
echo ""
exit 1
