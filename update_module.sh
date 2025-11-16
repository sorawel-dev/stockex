#!/bin/bash
# Script de mise à jour du module stockex

echo "🔄 Redémarrage d'Odoo..."
docker restart odoo-service

echo "⏳ Attente du démarrage d'Odoo (15 secondes)..."
sleep 15

echo "✅ Odoo redémarré avec succès!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Ouvrez votre navigateur et allez sur votre instance Odoo"
echo "2. Allez dans Apps (Applications)"
echo "3. Recherchez 'stockex'"
echo "4. Cliquez sur les 3 points ⋮ puis 'Mettre à jour'"
echo ""
echo "Les nouveaux droits d'accès seront alors appliqués ✅"
