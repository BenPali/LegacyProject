from typing import Any, List
from lib import iovalue
from lib import name
from lib import mutil


def array_forall(f, arr):
    return all(f(x) for x in arr)


def array_exists(f, arr):
    return any(f(x) for x in arr)


def array_associ(f, arr):
    for i, x in enumerate(arr):
        if f(x):
            return i
    raise ValueError("Not found")


def array_find_all(f, arr):
    return [x for x in arr if f(x)]


def sort_uniq(cmp, lst):
    if not lst:
        return []
    sorted_list = sorted(lst, key=lambda x: (x, id(x)))
    result = [sorted_list[0]]
    for item in sorted_list[1:]:
        if item != result[-1]:
            result.append(item)
    return result


def output_value_no_sharing(oc, v: Any) -> None:
    iovalue.output(oc, v)


def name_index(s: str) -> int:
    from lib.database import TABLE_SIZE
    return hash(name.crush_lower(s)) % TABLE_SIZE


def compare_snames(base_data, s1: str, s2: str) -> int:
    particles = base_data.particles if base_data.particles else []
    return mutil.compare_after_particle(particles, s1, s2)


def compare_snames_i(base_data, is1: int, is2: int) -> int:
    if is1 == is2:
        return 0
    return compare_snames(base_data, base_data.strings.get(is1), base_data.strings.get(is2))


def compare_fnames(s1: str, s2: str) -> int:
    if s1 < s2:
        return -1
    elif s1 > s2:
        return 1
    return 0


def compare_fnames_i(base_data, is1: int, is2: int) -> int:
    if is1 == is2:
        return 0
    return compare_fnames(base_data.strings.get(is1), base_data.strings.get(is2))


def person_to_gen_person(dsk_person, strings_get, iper):
    from lib.gwdef import GenPerson
    if isinstance(dsk_person, GenPerson):
        return dsk_person
    if isinstance(dsk_person, dict):
        return GenPerson(**dsk_person)
    if isinstance(dsk_person, (list, tuple)) and len(dsk_person) >= 34:
        return GenPerson(
            first_name=dsk_person[0],
            surname=dsk_person[1],
            occ=dsk_person[2],
            image=dsk_person[3],
            public_name=dsk_person[4],
            qualifiers=dsk_person[5],
            aliases=dsk_person[6],
            first_names_aliases=dsk_person[7],
            surnames_aliases=dsk_person[8],
            titles=dsk_person[9],
            rparents=dsk_person[10],
            related=dsk_person[11],
            occupation=dsk_person[12],
            sex=dsk_person[13],
            access=dsk_person[14],
            birth=dsk_person[15],
            birth_place=dsk_person[16],
            birth_note=dsk_person[17],
            birth_src=dsk_person[18],
            baptism=dsk_person[19],
            baptism_place=dsk_person[20],
            baptism_note=dsk_person[21],
            baptism_src=dsk_person[22],
            death=dsk_person[23],
            death_place=dsk_person[24],
            death_note=dsk_person[25],
            death_src=dsk_person[26],
            burial=dsk_person[27],
            burial_place=dsk_person[28],
            burial_note=dsk_person[29],
            burial_src=dsk_person[30],
            pevents=dsk_person[31],
            notes=dsk_person[32],
            psources=dsk_person[33],
            key_index=iper
        )
    return dsk_person


def ascend_to_gen_ascend(dsk_ascend):
    from lib.gwdef import GenAscend
    if isinstance(dsk_ascend, GenAscend):
        return dsk_ascend
    if isinstance(dsk_ascend, dict):
        parents = dsk_ascend.get('parents')
        if isinstance(parents, dict) and 'tag' in parents:
            if parents['tag'] == 0:
                parents = None
            elif parents['tag'] == 1 and 'fields' in parents:
                parents = parents['fields'][0] if parents['fields'] else None
        consang = dsk_ascend.get('consang', {'tag': 'Fix', 'value': -1})
        return GenAscend(parents=parents, consang=consang)
    if isinstance(dsk_ascend, (list, tuple)) and len(dsk_ascend) >= 2:
        parents = dsk_ascend[0]
        if isinstance(parents, dict) and 'tag' in parents:
            if parents['tag'] == 0:
                parents = None
            elif parents['tag'] == 1 and 'fields' in parents:
                parents = parents['fields'][0] if parents['fields'] else None
        return GenAscend(
            parents=parents,
            consang=dsk_ascend[1]
        )
    return dsk_ascend


def union_to_gen_union(dsk_union):
    from lib.gwdef import GenUnion
    if isinstance(dsk_union, GenUnion):
        return dsk_union
    if isinstance(dsk_union, dict):
        family = dsk_union.get('family', [])
        if isinstance(family, list):
            decoded_family = []
            for fam_item in family:
                if isinstance(fam_item, dict) and 'tag' in fam_item:
                    if fam_item['tag'] == 1 and 'fields' in fam_item:
                        decoded_family.append(fam_item['fields'][0] if fam_item['fields'] else None)
                else:
                    decoded_family.append(fam_item)
            family = decoded_family
        return GenUnion(family=family)
    if isinstance(dsk_union, (list, tuple)) and len(dsk_union) >= 1:
        family = dsk_union[0]
        if isinstance(family, list):
            decoded_family = []
            for fam_item in family:
                if isinstance(fam_item, dict) and 'tag' in fam_item:
                    if fam_item['tag'] == 1 and 'fields' in fam_item:
                        decoded_family.append(fam_item['fields'][0] if fam_item['fields'] else None)
                else:
                    decoded_family.append(fam_item)
            family = decoded_family
        return GenUnion(family=family)
    return dsk_union


def family_to_gen_family(dsk_family, strings_get, ifam):
    from lib.gwdef import GenFamily
    if isinstance(dsk_family, GenFamily):
        return dsk_family
    if isinstance(dsk_family, dict):
        return GenFamily(**dsk_family)
    if isinstance(dsk_family, (list, tuple)) and len(dsk_family) >= 11:
        return GenFamily(
            marriage=dsk_family[0],
            marriage_place=dsk_family[1],
            marriage_note=dsk_family[2],
            marriage_src=dsk_family[3],
            witnesses=dsk_family[4],
            relation=dsk_family[5],
            divorce=dsk_family[6],
            fevents=dsk_family[7],
            comment=dsk_family[8],
            origin_file=dsk_family[9],
            fsources=dsk_family[10],
            fam_index=ifam
        )
    return dsk_family


def couple_to_gen_couple(dsk_couple):
    from lib.adef import Couple
    if isinstance(dsk_couple, Couple):
        return dsk_couple
    if isinstance(dsk_couple, dict):
        father = dsk_couple.get('father')
        mother = dsk_couple.get('mother')
        if isinstance(father, dict) and 'tag' in father:
            if father['tag'] == 0:
                father = None
            elif father['tag'] == 1 and 'fields' in father:
                father = father['fields'][0] if father['fields'] else None
        if isinstance(mother, dict) and 'tag' in mother:
            if mother['tag'] == 0:
                mother = None
            elif mother['tag'] == 1 and 'fields' in mother:
                mother = mother['fields'][0] if mother['fields'] else None

        return Couple(father=father, mother=mother)
    if isinstance(dsk_couple, (list, tuple)) and len(dsk_couple) >= 2:
        return Couple(father=dsk_couple[0], mother=dsk_couple[1])
    return dsk_couple


def descend_to_gen_descend(dsk_descend):
    from lib.gwdef import GenDescend
    if isinstance(dsk_descend, GenDescend):
        return dsk_descend
    if isinstance(dsk_descend, dict):
        children = dsk_descend.get('children', [])
        if isinstance(children, list):
            decoded_children = []
            for child in children:
                if isinstance(child, dict) and 'tag' in child:
                    if child['tag'] == 1 and 'fields' in child:
                        decoded_children.append(child['fields'][0] if child['fields'] else None)
                else:
                    decoded_children.append(child)
            children = decoded_children

        return GenDescend(children=children)
    if isinstance(dsk_descend, (list, tuple)) and len(dsk_descend) >= 1:
        return GenDescend(children=dsk_descend[0])
    return dsk_descend
