"""
Module Gwdb - Base de données restaurée depuis OCaml GeneWeb

Ce module contient la traduction fidèle des structures de données
et fonctions du module Gwdb original en OCaml.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from .definitions import (
    Sex, Access, Date, Death, Burial, Title, Relation, Event, 
    RelationType, Divorce, Iper, Ifam
)


@dataclass
class Person:
    """
    Structure person restaurée fidèlement depuis OCaml GeneWeb
    
    Cette classe préserve exactement la même structure et les mêmes champs
    que la structure person originale en OCaml.
    """
    key: Iper
    first_name: str
    surname: str
    occ: int
    public_name: str
    image: str
    first_name_aliases: List[str] = field(default_factory=list)
    surname_aliases: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)
    titles: List[Title] = field(default_factory=list)
    rparents: List[Relation] = field(default_factory=list)
    related: List[Iper] = field(default_factory=list)
    occupation: str = ""
    sex: Sex = Sex.NEUTER
    access: Access = Access.PUBLIC
    birth: Optional[Date] = None
    birth_place: str = ""
    birth_src: str = ""
    baptism: Optional[Date] = None
    baptism_place: str = ""
    baptism_src: str = ""
    death: Death = field(default_factory=lambda: Death.not_dead())
    death_place: str = ""
    death_src: str = ""
    burial: Burial = field(default_factory=lambda: Burial.unknown_burial())
    burial_place: str = ""
    burial_src: str = ""
    pevents: List[Event] = field(default_factory=list)
    notes: str = ""
    psources: str = ""
    key_index: int = 0
    consang: int = 0
    linked_page: Optional[str] = None
    has_sources: bool = False
    families: List[Ifam] = field(default_factory=list)
    families_u: List[Ifam] = field(default_factory=list)


@dataclass
class Family:
    """
    Structure family restaurée fidèlement depuis OCaml GeneWeb
    
    Cette classe préserve exactement la même structure et les mêmes champs
    que la structure family originale en OCaml.
    """
    key: Ifam
    marriage: Optional[Date] = None
    marriage_place: str = ""
    marriage_src: str = ""
    witnesses: List[Iper] = field(default_factory=list)
    relation: RelationType = RelationType.MARRIED
    divorce: Divorce = field(default_factory=lambda: Divorce.not_divorced())
    fevents: List[Event] = field(default_factory=list)
    comment: str = ""
    origin_file: str = ""
    fsources: str = ""
    fam_index: int = 0
    sex: Sex = Sex.NEUTER
    children: List[Iper] = field(default_factory=list)
    parents: List[Iper] = field(default_factory=list)


class Gwdb:
    """
    Classe principale de base de données restaurée depuis OCaml GeneWeb
    
    Cette classe implémente les fonctions principales de gestion de la base
    de données généalogique, traduites fidèlement depuis l'OCaml original.
    """
    
    def __init__(self):
        """Initialise la base de données vide"""
        self.persons: Dict[Iper, Person] = {}
        self.families: Dict[Ifam, Family] = {}
        self.next_iper = 1
        self.next_ifam = 1
    
    def get_person(self, iper: Iper) -> Optional[Person]:
        """
        Fonction get_person restaurée depuis OCaml
        
        Retourne la personne correspondant à l'identifiant iper,
        ou None si elle n'existe pas.
        """
        return self.persons.get(iper)
    
    def get_family(self, ifam: Ifam) -> Optional[Family]:
        """
        Fonction get_family restaurée depuis OCaml
        
        Retourne la famille correspondant à l'identifiant ifam,
        ou None si elle n'existe pas.
        """
        return self.families.get(ifam)
    
    def get_parents(self, iper: Iper) -> List[Iper]:
        """
        Fonction get_parents restaurée depuis OCaml
        
        Retourne la liste des parents d'une personne.
        """
        person = self.get_person(iper)
        if person is None:
            return []
        
        parents = []
        for ifam in person.families:
            family = self.get_family(ifam)
            if family:
                parents.extend(family.parents)
        
        return parents
    
    def get_children(self, ifam: Ifam) -> List[Iper]:
        """
        Fonction get_children restaurée depuis OCaml
        
        Retourne la liste des enfants d'une famille.
        """
        family = self.get_family(ifam)
        if family is None:
            return []
        return family.children
    
    def get_siblings(self, iper: Iper) -> List[Iper]:
        """
        Fonction get_siblings restaurée depuis OCaml
        
        Retourne la liste des frères et sœurs d'une personne.
        """
        parents = self.get_parents(iper)
        siblings = []
        
        for parent in parents:
            parent_obj = self.get_person(parent)
            if parent_obj:
                for ifam in parent_obj.families:
                    family = self.get_family(ifam)
                    if family:
                        siblings.extend(family.children)
        
        # Retirer la personne elle-même de la liste
        siblings = [s for s in siblings if s != iper]
        return list(set(siblings))  # Supprimer les doublons
    
    def get_spouse(self, iper: Iper, ifam: Ifam) -> Optional[Iper]:
        """
        Fonction get_spouse restaurée depuis OCaml
        
        Retourne le conjoint d'une personne dans une famille donnée.
        """
        family = self.get_family(ifam)
        if family is None:
            return None
        
        if family.parents:
            for parent in family.parents:
                if parent != iper:
                    return parent
        
        return None
    
    def get_ancestors(self, iper: Iper, max_gen: int) -> List[Iper]:
        """
        Fonction get_ancestors restaurée depuis OCaml
        
        Retourne la liste des ancêtres jusqu'à max_gen générations.
        """
        ancestors = []
        visited = set()
        
        def _get_ancestors_rec(current_iper: Iper, generation: int):
            if generation >= max_gen or current_iper in visited:
                return
            
            visited.add(current_iper)
            parents = self.get_parents(current_iper)
            
            for parent in parents:
                ancestors.append(parent)
                _get_ancestors_rec(parent, generation + 1)
        
        _get_ancestors_rec(iper, 0)
        return ancestors
    
    def get_descendants(self, iper: Iper, max_gen: int) -> List[Iper]:
        """
        Fonction get_descendants restaurée depuis OCaml
        
        Retourne la liste des descendants jusqu'à max_gen générations.
        """
        descendants = []
        visited = set()
        
        def _get_descendants_rec(current_iper: Iper, generation: int):
            if generation >= max_gen or current_iper in visited:
                return
            
            visited.add(current_iper)
            person = self.get_person(current_iper)
            if person is None:
                return
            
            for ifam in person.families:
                children = self.get_children(ifam)
                for child in children:
                    descendants.append(child)
                    _get_descendants_rec(child, generation + 1)
        
        _get_descendants_rec(iper, 0)
        return descendants
    
    def get_relationship(self, iper1: Iper, iper2: Iper) -> Optional[str]:
        """
        Fonction get_relationship restaurée depuis OCaml
        
        Calcule la relation entre deux personnes.
        """
        if iper1 == iper2:
            return "self"
        
        # Vérifier si l'une est parent de l'autre
        parents1 = self.get_parents(iper1)
        if iper2 in parents1:
            return "parent"
        
        parents2 = self.get_parents(iper2)
        if iper1 in parents2:
            return "child"
        
        # Vérifier si ce sont des frères/sœurs
        siblings1 = self.get_siblings(iper1)
        if iper2 in siblings1:
            return "sibling"
        
        # Vérifier si ce sont des conjoints
        person1 = self.get_person(iper1)
        if person1:
            for ifam in person1.families:
                spouse = self.get_spouse(iper1, ifam)
                if spouse == iper2:
                    return "spouse"
        
        return None
    
    def get_common_ancestor(self, iper1: Iper, iper2: Iper) -> Optional[Iper]:
        """
        Fonction get_common_ancestor restaurée depuis OCaml
        
        Trouve un ancêtre commun entre deux personnes.
        """
        ancestors1 = set(self.get_ancestors(iper1, 10))
        ancestors2 = set(self.get_ancestors(iper2, 10))
        
        common = ancestors1.intersection(ancestors2)
        if common:
            # Retourner l'ancêtre le plus proche (plus récent)
            return min(common, key=lambda x: len(self.get_ancestors(x, 10)))
        
        return None
    
    def add_person(self, person: Person) -> Iper:
        """
        Ajoute une personne à la base de données
        
        Retourne l'identifiant assigné à la personne.
        """
        if person.key == 0:
            person.key = self.next_iper
            self.next_iper += 1
        
        self.persons[person.key] = person
        return person.key
    
    def add_family(self, family: Family) -> Ifam:
        """
        Ajoute une famille à la base de données
        
        Retourne l'identifiant assigné à la famille.
        """
        if family.key == 0:
            family.key = self.next_ifam
            self.next_ifam += 1
        
        self.families[family.key] = family
        return family.key
