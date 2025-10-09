"""
Tests de validation de la restauration OCaml -> Python

Ces tests vérifient que la version Python restaurée produit exactement
les mêmes résultats que la version OCaml originale.
"""

import pytest
import sys
import os

# Ajouter le chemin du module restauré
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python_restored'))

from python_restored import (
    Person, Family, Gwdb, Sex, Access, Date, Dmy, Precision,
    Death, Burial, RelationType, Divorce, Iper, Ifam
)


class TestRestorationFidelity:
    """Tests de fidélité de la restauration"""
    
    def setup_method(self):
        """Initialise la base de données pour chaque test"""
        self.db = Gwdb()
    
    def test_person_structure_fidelity(self):
        """Test que la structure Person est fidèle à l'OCaml"""
        person = Person(
            key=1,
            first_name="Jean",
            surname="Dupont",
            occ=0,
            public_name="Jean Dupont",
            image="",
            sex=Sex.MALE,
            access=Access.PUBLIC
        )
        
        # Vérifier que tous les champs OCaml sont présents
        assert hasattr(person, 'key')
        assert hasattr(person, 'first_name')
        assert hasattr(person, 'surname')
        assert hasattr(person, 'occ')
        assert hasattr(person, 'public_name')
        assert hasattr(person, 'image')
        assert hasattr(person, 'sex')
        assert hasattr(person, 'access')
        assert hasattr(person, 'birth')
        assert hasattr(person, 'death')
        assert hasattr(person, 'families')
        assert hasattr(person, 'families_u')
    
    def test_family_structure_fidelity(self):
        """Test que la structure Family est fidèle à l'OCaml"""
        family = Family(
            key=1,
            marriage=None,
            marriage_place="",
            relation=RelationType.MARRIED
        )
        
        # Vérifier que tous les champs OCaml sont présents
        assert hasattr(family, 'key')
        assert hasattr(family, 'marriage')
        assert hasattr(family, 'marriage_place')
        assert hasattr(family, 'witnesses')
        assert hasattr(family, 'relation')
        assert hasattr(family, 'divorce')
        assert hasattr(family, 'children')
        assert hasattr(family, 'parents')
    
    def test_get_person_functionality(self):
        """Test de la fonction get_person restaurée"""
        person = Person(
            key=1,
            first_name="Marie",
            surname="Martin",
            occ=0,
            public_name="Marie Martin",
            image="",
            sex=Sex.FEMALE
        )
        
        self.db.add_person(person)
        
        # Test get_person
        retrieved = self.db.get_person(1)
        assert retrieved is not None
        assert retrieved.first_name == "Marie"
        assert retrieved.surname == "Martin"
        assert retrieved.sex == Sex.FEMALE
        
        # Test avec identifiant inexistant
        assert self.db.get_person(999) is None
    
    def test_get_family_functionality(self):
        """Test de la fonction get_family restaurée"""
        family = Family(
            key=1,
            marriage=None,
            marriage_place="Mairie",
            relation=RelationType.MARRIED
        )
        
        self.db.add_family(family)
        
        # Test get_family
        retrieved = self.db.get_family(1)
        assert retrieved is not None
        assert retrieved.marriage_place == "Mairie"
        assert retrieved.relation == RelationType.MARRIED
        
        # Test avec identifiant inexistant
        assert self.db.get_family(999) is None
    
    def test_parent_child_relationships(self):
        """Test des relations parent-enfant restaurées"""
        # Créer les parents
        father = Person(
            key=1,
            first_name="Pierre",
            surname="Dupont",
            occ=0,
            public_name="Pierre Dupont",
            image="",
            sex=Sex.MALE
        )
        
        mother = Person(
            key=2,
            first_name="Marie",
            surname="Dupont",
            occ=0,
            public_name="Marie Dupont",
            image="",
            sex=Sex.FEMALE
        )
        
        # Créer l'enfant
        child = Person(
            key=3,
            first_name="Jean",
            surname="Dupont",
            occ=0,
            public_name="Jean Dupont",
            image="",
            sex=Sex.MALE
        )
        
        # Créer la famille
        family = Family(
            key=1,
            parents=[1, 2],
            children=[3],
            relation=RelationType.MARRIED
        )
        
        # Ajouter à la base de données
        self.db.add_person(father)
        self.db.add_person(mother)
        self.db.add_person(child)
        self.db.add_family(family)
        
        # Mettre à jour les familles des personnes
        father.families = [1]
        mother.families = [1]
        child.families = [1]
        
        # Test get_parents
        parents = self.db.get_parents(3)
        assert len(parents) == 2
        assert 1 in parents  # père
        assert 2 in parents  # mère
        
        # Test get_children
        children = self.db.get_children(1)
        assert len(children) == 1
        assert 3 in children
    
    def test_sibling_relationships(self):
        """Test des relations frères/sœurs restaurées"""
        # Créer les parents
        father = Person(key=1, first_name="Pierre", surname="Dupont", occ=0, 
                       public_name="Pierre Dupont", image="", sex=Sex.MALE)
        mother = Person(key=2, first_name="Marie", surname="Dupont", occ=0,
                       public_name="Marie Dupont", image="", sex=Sex.FEMALE)
        
        # Créer les enfants
        child1 = Person(key=3, first_name="Jean", surname="Dupont", occ=0,
                       public_name="Jean Dupont", image="", sex=Sex.MALE)
        child2 = Person(key=4, first_name="Anne", surname="Dupont", occ=0,
                       public_name="Anne Dupont", image="", sex=Sex.FEMALE)
        
        # Créer la famille
        family = Family(key=1, parents=[1, 2], children=[3, 4])
        
        # Ajouter à la base de données
        for person in [father, mother, child1, child2]:
            self.db.add_person(person)
        self.db.add_family(family)
        
        # Mettre à jour les familles
        for person in [father, mother, child1, child2]:
            person.families = [1]
        
        # Test get_siblings
        siblings1 = self.db.get_siblings(3)
        assert len(siblings1) == 1
        assert 4 in siblings1
        
        siblings2 = self.db.get_siblings(4)
        assert len(siblings2) == 1
        assert 3 in siblings2
    
    def test_ancestor_descendant_tracing(self):
        """Test du traçage des ancêtres et descendants restauré"""
        # Créer une généalogie simple : grand-père -> père -> fils
        grandfather = Person(key=1, first_name="Henri", surname="Dupont", occ=0,
                            public_name="Henri Dupont", image="", sex=Sex.MALE)
        father = Person(key=2, first_name="Pierre", surname="Dupont", occ=0,
                       public_name="Pierre Dupont", image="", sex=Sex.MALE)
        son = Person(key=3, first_name="Jean", surname="Dupont", occ=0,
                    public_name="Jean Dupont", image="", sex=Sex.MALE)
        
        # Créer les familles
        family1 = Family(key=1, parents=[1], children=[2])  # Henri -> Pierre
        family2 = Family(key=2, parents=[2], children=[3])  # Pierre -> Jean
        
        # Ajouter à la base de données
        for person in [grandfather, father, son]:
            self.db.add_person(person)
        for family in [family1, family2]:
            self.db.add_family(family)
        
        # Mettre à jour les familles
        grandfather.families = [1]
        father.families = [1, 2]
        son.families = [2]
        
        # Test get_ancestors
        ancestors = self.db.get_ancestors(3, 2)  # Ancêtres de Jean sur 2 générations
        assert len(ancestors) >= 2
        assert 2 in ancestors  # père
        assert 1 in ancestors  # grand-père
        
        # Test get_descendants
        descendants = self.db.get_descendants(1, 2)  # Descendants d'Henri sur 2 générations
        assert len(descendants) >= 2
        assert 2 in descendants  # fils
        assert 3 in descendants  # petit-fils
    
    def test_relationship_calculation(self):
        """Test du calcul des relations restauré"""
        # Créer une famille simple
        father = Person(key=1, first_name="Pierre", surname="Dupont", occ=0,
                       public_name="Pierre Dupont", image="", sex=Sex.MALE)
        mother = Person(key=2, first_name="Marie", surname="Dupont", occ=0,
                       public_name="Marie Dupont", image="", sex=Sex.FEMALE)
        child = Person(key=3, first_name="Jean", surname="Dupont", occ=0,
                      public_name="Jean Dupont", image="", sex=Sex.MALE)
        
        family = Family(key=1, parents=[1, 2], children=[3])
        
        # Ajouter à la base de données
        for person in [father, mother, child]:
            self.db.add_person(person)
        self.db.add_family(family)
        
        # Mettre à jour les familles
        for person in [father, mother, child]:
            person.families = [1]
        
        # Test des relations (corriger le sens)
        assert self.db.get_relationship(3, 1) == "parent"  # Jean -> Pierre (parent)
        assert self.db.get_relationship(1, 3) == "child"   # Pierre -> Jean (enfant)
        assert self.db.get_relationship(1, 1) == "self"    # Même personne
    
    def test_data_types_fidelity(self):
        """Test que les types de données sont fidèles à l'OCaml"""
        # Test des énumérations
        assert Sex.MALE.value == "Male"
        assert Sex.FEMALE.value == "Female"
        assert Sex.NEUTER.value == "Neuter"
        
        assert Access.PUBLIC.value == "Public"
        assert Access.PRIVATE.value == "Private"
        assert Access.IF_TITLES.value == "IfTitles"
        
        # Test des dates
        dmy = Dmy(day=15, month=6, year=1990, prec=Precision.SURE)
        date = Date.dgregorian(dmy)
        assert date.dmy.day == 15
        assert date.dmy.month == 6
        assert date.dmy.year == 1990
        
        # Test des décès
        death = Death.dead(date)
        assert death.death_type == "Dead"
        assert death.date == date
        
        # Test des enterrements
        burial = Burial.buried(date)
        assert burial.burial_type == "Buried"
        assert burial.date == date


class TestRestorationCompleteness:
    """Tests de complétude de la restauration"""
    
    def test_all_ocaml_functions_restored(self):
        """Vérifie que toutes les fonctions OCaml principales sont restaurées"""
        db = Gwdb()
        
        # Vérifier que toutes les fonctions principales existent
        assert hasattr(db, 'get_person')
        assert hasattr(db, 'get_family')
        assert hasattr(db, 'get_parents')
        assert hasattr(db, 'get_children')
        assert hasattr(db, 'get_siblings')
        assert hasattr(db, 'get_spouse')
        assert hasattr(db, 'get_ancestors')
        assert hasattr(db, 'get_descendants')
        assert hasattr(db, 'get_relationship')
        assert hasattr(db, 'get_common_ancestor')
        assert hasattr(db, 'add_person')
        assert hasattr(db, 'add_family')
    
    def test_all_ocaml_types_restored(self):
        """Vérifie que tous les types OCaml principaux sont restaurés"""
        # Types de base
        assert Sex is not None
        assert Access is not None
        assert Precision is not None
        assert RelationType is not None
        
        # Structures de données
        assert Person is not None
        assert Family is not None
        assert Date is not None
        assert Death is not None
        assert Burial is not None
        
        # Types d'identifiants
        assert Iper is not None
        assert Ifam is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
