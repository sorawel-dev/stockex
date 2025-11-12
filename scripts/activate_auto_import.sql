-- Script SQL pour activer l'import automatique Kobo → Odoo toutes les 30 minutes
-- À exécuter dans la base de données Odoo

-- 1. Activer le CRON d'import automatique (30 minutes)
UPDATE ir_cron 
SET 
    active = TRUE,
    interval_number = 30,
    interval_type = 'minutes',
    nextcall = NOW() + INTERVAL '30 minutes'
WHERE 
    name = 'Stockex: Synchronisation Auto Kobo Collect';

-- 2. Activer l'import automatique pour la configuration Kobo
-- (Remplacer 'Config Kobo - Bassa Warehouse' par le nom de votre configuration)
UPDATE stockex_kobo_config
SET 
    auto_import = TRUE,
    cron_interval_number = 30,
    cron_interval_type = 'minutes'
WHERE 
    active = TRUE 
    AND name LIKE '%Bassa%';

-- 3. Vérifier les configurations
SELECT 
    id,
    name,
    active,
    auto_import,
    auto_validate,
    cron_interval_number,
    cron_interval_type,
    last_sync
FROM stockex_kobo_config
WHERE active = TRUE;

-- 4. Vérifier le CRON
SELECT 
    id,
    name,
    active,
    interval_number,
    interval_type,
    nextcall,
    lastcall
FROM ir_cron
WHERE name LIKE '%Kobo%';
-- Script SQL pour activer l'import automatique Kobo → Odoo toutes les 30 minutes
-- À exécuter dans la base de données Odoo

-- 1. Activer le CRON d'import automatique (30 minutes)
UPDATE ir_cron 
SET 
    active = TRUE,
    interval_number = 30,
    interval_type = 'minutes',
    nextcall = NOW() + INTERVAL '30 minutes'
WHERE 
    name = 'Stockex: Synchronisation Auto Kobo Collect';

-- 2. Activer l'import automatique pour la configuration Kobo
-- (Remplacer 'Config Kobo - Bassa Warehouse' par le nom de votre configuration)
UPDATE stockex_kobo_config
SET 
    auto_import = TRUE,
    cron_interval_number = 30,
    cron_interval_type = 'minutes'
WHERE 
    active = TRUE 
    AND name LIKE '%Bassa%';

-- 3. Vérifier les configurations
SELECT 
    id,
    name,
    active,
    auto_import,
    auto_validate,
    cron_interval_number,
    cron_interval_type,
    last_sync
FROM stockex_kobo_config
WHERE active = TRUE;

-- 4. Vérifier le CRON
SELECT 
    id,
    name,
    active,
    interval_number,
    interval_type,
    nextcall,
    lastcall
FROM ir_cron
WHERE name LIKE '%Kobo%';
