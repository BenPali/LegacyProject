"""
Module Def - Définitions de base restaurées depuis OCaml GeneWeb

Ce module contient la traduction fidèle des types et définitions
du module Def original en OCaml, sans aucune modification fonctionnelle.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Union
from datetime import date


class Sex(Enum):
    """Type sex restauré depuis OCaml"""
    MALE = "Male"
    FEMALE = "Female" 
    NEUTER = "Neuter"


class Precision(Enum):
    """Type precision restauré depuis OCaml"""
    SURE = "Sure"
    ABOUT = "About"
    MAYBE = "Maybe"
    BEFORE = "Before"
    AFTER = "After"
    OR_YEAR = "OrYear"
    YEAR_INT = "YearInt"


class Access(Enum):
    """Type access restauré depuis OCaml"""
    IF_TITLES = "IfTitles"
    PUBLIC = "Public"
    PRIVATE = "Private"


@dataclass
class Dmy:
    """Structure dmy restaurée depuis OCaml"""
    day: int
    month: int
    year: int
    prec: Precision
    delta: int = 0


class Date:
    """Type date restauré depuis OCaml"""
    
    def __init__(self, dmy: Optional[Dmy] = None, text: Optional[str] = None):
        self.dmy = dmy
        self.text = text
        self.is_none = dmy is None and text is None
    
    @classmethod
    def dgregorian(cls, dmy: Dmy) -> 'Date':
        """Constructeur Dgregorian restauré"""
        return cls(dmy=dmy)
    
    @classmethod
    def dtext(cls, text: str) -> 'Date':
        """Constructeur Dtext restauré"""
        return cls(text=text)
    
    @classmethod
    def dnone(cls) -> 'Date':
        """Constructeur Dnone restauré"""
        return cls()


class Death:
    """Type death restauré depuis OCaml"""
    
    def __init__(self, death_type: str, date: Optional[Date] = None):
        self.death_type = death_type  # "NotDead", "Dead", "DontKnowIfDead", "OfCourseDead"
        self.date = date
    
    @classmethod
    def not_dead(cls) -> 'Death':
        """Constructeur NotDead restauré"""
        return cls("NotDead")
    
    @classmethod
    def dead(cls, date: Date) -> 'Death':
        """Constructeur Dead restauré"""
        return cls("Dead", date)
    
    @classmethod
    def dont_know_if_dead(cls) -> 'Death':
        """Constructeur DontKnowIfDead restauré"""
        return cls("DontKnowIfDead")
    
    @classmethod
    def of_course_dead(cls, date: Date) -> 'Death':
        """Constructeur OfCourseDead restauré"""
        return cls("OfCourseDead", date)


class Burial:
    """Type burial restauré depuis OCaml"""
    
    def __init__(self, burial_type: str, date: Optional[Date] = None):
        self.burial_type = burial_type  # "UnknownBurial", "Buried", "Cremated"
        self.date = date
    
    @classmethod
    def unknown_burial(cls) -> 'Burial':
        """Constructeur UnknownBurial restauré"""
        return cls("UnknownBurial")
    
    @classmethod
    def buried(cls, date: Date) -> 'Burial':
        """Constructeur Buried restauré"""
        return cls("Buried", date)
    
    @classmethod
    def cremated(cls, date: Date) -> 'Burial':
        """Constructeur Cremated restauré"""
        return cls("Cremated", date)


@dataclass
class Title:
    """Structure title restaurée depuis OCaml"""
    title: str
    place: str
    date_start: Optional[Date]
    date_end: Optional[Date]
    nth: int


@dataclass
class Relation:
    """Structure relation restaurée depuis OCaml"""
    r_type: str
    r_fath: Optional[int]  # iper
    r_moth: Optional[int]  # iper
    r_sources: str


@dataclass
class Event:
    """Structure event restaurée depuis OCaml"""
    event_type: str
    date: Optional[Date]
    place: str
    reason: str
    note: str
    src: str
    witnesses: List[int]  # List of iper


class RelationType(Enum):
    """Type relation_type restauré depuis OCaml"""
    MARRIED = "Married"
    NOT_MARRIED = "NotMarried"
    ENGAGED = "Engaged"
    NO_SEXES_CHECKED = "NoSexesChecked"
    NO_MENTION = "NoMention"
    MARRIAGE_BANN = "MarriageBann"
    MARRIAGE_CONTRACT = "MarriageContract"
    MARRIAGE_LICENSE = "MarriageLicense"
    PACS = "Pacs"
    RESIDENCE = "Residence"


class Divorce:
    """Type divorce restauré depuis OCaml"""
    
    def __init__(self, divorce_type: str, date: Optional[Date] = None):
        self.divorce_type = divorce_type  # "NotDivorced", "Divorced", "Separated"
        self.date = date
    
    @classmethod
    def not_divorced(cls) -> 'Divorce':
        """Constructeur NotDivorced restauré"""
        return cls("NotDivorced")
    
    @classmethod
    def divorced(cls, date: Date) -> 'Divorce':
        """Constructeur Divorced restauré"""
        return cls("Divorced", date)
    
    @classmethod
    def separated(cls, date: Date) -> 'Divorce':
        """Constructeur Separated restauré"""
        return cls("Separated", date)


# Types d'identifiants restaurés depuis OCaml
Iper = int  # Identifiant de personne
Ifam = int  # Identifiant de famille
Istr = int  # Identifiant de chaîne
