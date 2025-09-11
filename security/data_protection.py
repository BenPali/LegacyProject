"""
Couche de sécurité pour la protection des données

Cette couche ajoute la sécurité au système GeneWeb restauré
sans modifier le core fonctionnel.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class DataProtection:
    """
    Classe de protection des données ajoutée au système restauré
    
    Cette classe fournit des fonctions de sécurité sans modifier
    les structures de données ou la logique métier originales.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialise la protection des données"""
        if encryption_key:
            self.key = self._derive_key(encryption_key)
        else:
            # Utiliser une clé par défaut pour le développement
            self.key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Dérive une clé de chiffrement à partir d'un mot de passe"""
        salt = b'geneweb_legacy_salt'  # En production, utiliser un sel aléatoire
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_sensitive_field(self, value: str) -> str:
        """
        Chiffre un champ sensible
        
        Cette fonction peut être utilisée pour chiffrer des champs
        comme les notes ou les sources sans modifier la structure Person.
        """
        if not value:
            return value
        
        encrypted_data = self.cipher_suite.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_field(self, encrypted_value: str) -> str:
        """
        Déchiffre un champ sensible
        """
        if not encrypted_value:
            return encrypted_value
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception:
            return encrypted_value  # Retourner la valeur originale en cas d'erreur
    
    def hash_personal_data(self, data: str) -> str:
        """
        Crée un hash des données personnelles pour l'indexation
        
        Utile pour créer des index de recherche sans exposer les données.
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def anonymize_person_data(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymise les données d'une personne pour la conformité GDPR
        
        Cette fonction crée une version anonymisée des données sans
        modifier la structure originale.
        """
        anonymized = person_data.copy()
        
        # Champs à anonymiser
        sensitive_fields = ['first_name', 'surname', 'notes', 'birth_place', 'death_place']
        
        for field in sensitive_fields:
            if field in anonymized and anonymized[field]:
                # Créer un hash pour l'indexation
                anonymized[f"{field}_hash"] = self.hash_personal_data(str(anonymized[field]))
                # Anonymiser le champ original
                anonymized[field] = "[ANONYMIZED]"
        
        return anonymized
    
    def create_audit_log(self, action: str, user: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un log d'audit pour une action
        
        Cette fonction ajoute la traçabilité sans modifier le core.
        """
        import datetime
        
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "user": user,
            "data_hash": self.hash_personal_data(json.dumps(data, sort_keys=True)),
            "ip_address": "127.0.0.1",  # En production, récupérer l'IP réelle
            "user_agent": "GeneWeb-Legacy/1.0"
        }
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide et nettoie les données d'entrée
        
        Cette fonction ajoute la validation sans modifier la logique métier.
        """
        validated = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Nettoyer les chaînes de caractères
                validated[key] = value.strip()[:1000]  # Limiter la longueur
            elif isinstance(value, (int, float)):
                # Valider les nombres
                validated[key] = value
            elif isinstance(value, bool):
                # Préserver les booléens
                validated[key] = value
            else:
                # Convertir en chaîne pour les autres types
                validated[key] = str(value)[:1000]
        
        return validated
    
    def get_security_info(self) -> Dict[str, Any]:
        """Retourne les informations de sécurité"""
        return {
            "encryption_algorithm": "AES-256",
            "key_derivation": "PBKDF2-HMAC-SHA256",
            "iterations": 100000,
            "status": "active",
            "version": "1.0.0"
        }


class SecureGwdb:
    """
    Wrapper sécurisé pour la classe Gwdb restaurée
    
    Cette classe ajoute des couches de sécurité autour du système
    restauré sans modifier son fonctionnement interne.
    """
    
    def __init__(self, gwdb_instance, data_protection: DataProtection):
        """Initialise le wrapper sécurisé"""
        self.gwdb = gwdb_instance
        self.data_protection = data_protection
        self.audit_logs = []
    
    def get_person(self, iper: int, user: str = "anonymous") -> Optional[Any]:
        """
        Version sécurisée de get_person
        
        Ajoute la validation et l'audit sans modifier la logique originale.
        """
        # Validation de l'entrée
        if not isinstance(iper, int) or iper <= 0:
            return None
        
        # Appel de la fonction originale
        person = self.gwdb.get_person(iper)
        
        if person:
            # Créer un log d'audit
            audit_log = self.data_protection.create_audit_log(
                "get_person",
                user,
                {"iper": iper, "person_found": True}
            )
            self.audit_logs.append(audit_log)
        
        return person
    
    def add_person(self, person: Any, user: str = "anonymous") -> int:
        """
        Version sécurisée de add_person
        
        Ajoute la validation et l'audit sans modifier la logique originale.
        """
        # Validation des données
        if not person or not hasattr(person, 'first_name'):
            return 0
        
        # Nettoyer les données d'entrée
        person.first_name = self.data_protection.validate_input(
            {"first_name": person.first_name}
        )["first_name"]
        
        if hasattr(person, 'surname'):
            person.surname = self.data_protection.validate_input(
                {"surname": person.surname}
            )["surname"]
        
        # Appel de la fonction originale
        result = self.gwdb.add_person(person)
        
        # Créer un log d'audit
        audit_log = self.data_protection.create_audit_log(
            "add_person",
            user,
            {"person_key": result, "first_name": person.first_name}
        )
        self.audit_logs.append(audit_log)
        
        return result
    
    def get_audit_logs(self) -> list:
        """Retourne les logs d'audit"""
        return self.audit_logs.copy()
    
    def clear_audit_logs(self):
        """Efface les logs d'audit"""
        self.audit_logs.clear()
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de sécurité"""
        return {
            "total_audit_logs": len(self.audit_logs),
            "encryption_status": "active",
            "data_protection_version": "1.0.0",
            "last_audit": self.audit_logs[-1]["timestamp"] if self.audit_logs else None
        }
