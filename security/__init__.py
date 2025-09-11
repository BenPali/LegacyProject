"""
Module de sécurité pour le système GeneWeb restauré

Ce module ajoute des couches de sécurité au système restauré
sans modifier le core fonctionnel.
"""

from .data_protection import DataProtection, SecureGwdb

__all__ = ["DataProtection", "SecureGwdb"]
