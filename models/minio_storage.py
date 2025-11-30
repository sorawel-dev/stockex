# -*- coding: utf-8 -*-

import os
import logging
from datetime import timedelta, date

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    Minio = None
    S3Error = Exception

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

if not MINIO_AVAILABLE:
    _logger.warning("Module MinIO non disponible. Le stockage MinIO ne fonctionnera pas. Installez-le avec: pip3 install minio")


class MinioStorage(models.AbstractModel):
    """Gestionnaire de stockage MinIO pour les pièces jointes."""
    _name = 'minio.storage'
    _description = 'MinIO Storage Manager'

    @api.model
    def _get_minio_client(self):
        """Retourne un client MinIO configuré."""
        if not MINIO_AVAILABLE:
            raise UserError(
                "Le module Python 'minio' n'est pas installé. "
                "Veuillez l'installer avec: pip3 install minio"
            )
        
        ICP = self.env['ir.config_parameter'].sudo()
        
        endpoint = ICP.get_param('minio.endpoint', 'infra-minio:9000')
        access_key = ICP.get_param('minio.access_key', '')
        secret_key = ICP.get_param('minio.secret_key', '')
        secure = ICP.get_param('minio.secure', 'False') == 'True'
        region = ICP.get_param('minio.region', 'Deutchland')
        
        if not access_key or not secret_key:
            raise UserError(
                "Configuration MinIO incomplète. "
                "Veuillez configurer minio.endpoint, minio.access_key et minio.secret_key "
                "dans les paramètres système."
            )
        
        try:
            client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure,
                region=region
            )
            return client
        except Exception as e:
            _logger.error(f"Erreur connexion MinIO: {e}")
            raise UserError(f"Impossible de se connecter à MinIO: {e}")

    @api.model
    def _get_bucket_name(self):
        """Retourne le nom du bucket configuré."""
        ICP = self.env['ir.config_parameter'].sudo()
        return ICP.get_param('minio.bucket', 'stockex-documents')

    @api.model
    def _ensure_bucket_exists(self):
        """Crée le bucket s'il n'existe pas."""
        client = self._get_minio_client()
        bucket = self._get_bucket_name()
        
        try:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                _logger.info(f"✅ Bucket MinIO '{bucket}' créé")
            return bucket
        except S3Error as e:
            _logger.error(f"Erreur création bucket: {e}")
            raise UserError(f"Impossible de créer le bucket MinIO: {e}")

    @api.model
    def generate_upload_url(self, filename, res_model, res_id):
        """Génère une URL pré-signée pour upload direct vers MinIO.
        
        Args:
            filename: Nom du fichier
            res_model: Modèle Odoo parent
            res_id: ID de l'enregistrement parent
            
        Returns:
            dict: {
                'upload_url': URL pré-signée,
                'object_name': Chemin de l'objet dans MinIO,
                'bucket': Nom du bucket
            }
        """
        client = self._get_minio_client()
        bucket = self._ensure_bucket_exists()
        
        # Générer chemin objet unique
        today = date.today().strftime('%Y-%m-%d')
        object_name = f"stockex/{res_model}/{res_id}/{filename}-{today}"
        
        try:
            # URL pré-signée valide 15 minutes
            presigned_url = client.presigned_put_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=timedelta(minutes=15)
            )
            
            _logger.info(f"📤 URL upload générée: {object_name}")
            
            return {
                'upload_url': presigned_url,
                'object_name': object_name,
                'bucket': bucket
            }
        except S3Error as e:
            _logger.error(f"Erreur génération URL upload: {e}")
            raise UserError(f"Impossible de générer l'URL d'upload: {e}")

    @api.model
    def generate_download_url(self, bucket, object_name, expires_days=7):
        """Génère une URL pré-signée pour téléchargement.
        
        Args:
            bucket: Nom du bucket
            object_name: Chemin de l'objet
            expires_days: Durée de validité (jours)
            
        Returns:
            str: URL pré-signée
        """
        client = self._get_minio_client()
        
        try:
            presigned_url = client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=timedelta(days=expires_days)
            )
            
            _logger.info(f"📥 URL download générée: {object_name}")
            return presigned_url
        except S3Error as e:
            _logger.error(f"Erreur génération URL download: {e}")
            raise UserError(f"Impossible de générer l'URL de téléchargement: {e}")

    @api.model
    def delete_object(self, bucket, object_name):
        """Supprime un objet du stockage MinIO.
        
        Args:
            bucket: Nom du bucket
            object_name: Chemin de l'objet
        """
        client = self._get_minio_client()
        
        try:
            client.remove_object(bucket, object_name)
            _logger.info(f"🗑️ Objet supprimé: {bucket}/{object_name}")
        except S3Error as e:
            _logger.error(f"Erreur suppression objet: {e}")
            # Ne pas lever d'erreur, juste logger
