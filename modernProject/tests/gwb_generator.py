import os
from lib import database
from lib import iovalue
from lib import secure
from lib import name
from lib import dutil

def create_minimal_gwb(base_dir, db_name="test"):
    gwb_path = os.path.join(base_dir, f"{db_name}.gwb")
    os.makedirs(gwb_path, exist_ok=True)
    secure.add_assets(gwb_path)

    os.makedirs(os.path.join(gwb_path, "notes_d"), exist_ok=True)
    os.makedirs(os.path.join(gwb_path, "wiznotes"), exist_ok=True)
    open(os.path.join(gwb_path, "notes"), 'w').close()

    base_file = os.path.join(gwb_path, "base")

    persons_len = 2
    families_len = 1
    strings_len = 5

    strings = ["", "John", "Doe", "Jane", "Smith"]

    persons = [
        {
            'tag': 0,
            'fields': [
                1, 2, 0, 0, 0, [], [], [], [], [], [], [], 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [],
                0, 0, 0
            ]
        },
        {
            'tag': 0,
            'fields': [
                3, 4, 0, 0, 0, [], [], [], [], [], [], [], 0, 1, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [],
                0, 0, 1
            ]
        }
    ]

    ascends = [
        {'tag': 0, 'fields': [{'tag': 0, 'fields': []}, {'tag': 0, 'fields': []}]},
        {'tag': 0, 'fields': [{'tag': 0, 'fields': []}, {'tag': 0, 'fields': []}]}
    ]

    unions = [
        {'tag': 0, 'fields': [[0]]},
        {'tag': 0, 'fields': [[]]}
    ]

    families = [
        {
            'tag': 0,
            'fields': [
                0, 0, 0, 0, [], 0, 0, [], 0, 0, 0, 0
            ]
        }
    ]

    couples = [
        {'tag': 0, 'fields': [0, {'tag': 0, 'fields': []}]}
    ]

    descends = [
        {'tag': 0, 'fields': [[]]}
    ]

    with open(base_file, 'wb') as f:
        f.write(database.MAGIC_GNWB0024)

        database.output_binary_int(f, persons_len)
        database.output_binary_int(f, families_len)
        database.output_binary_int(f, strings_len)

        header_end = f.tell()

        database.output_binary_int(f, 0)
        database.output_binary_int(f, 0)
        database.output_binary_int(f, 0)
        database.output_binary_int(f, 0)
        database.output_binary_int(f, 0)
        database.output_binary_int(f, 0)
        database.output_binary_int(f, 0)

        iovalue.output(f, "")

        persons_pos = f.tell()
        iovalue.output(f, persons)

        ascends_pos = f.tell()
        iovalue.output(f, ascends)

        unions_pos = f.tell()
        iovalue.output(f, unions)

        families_pos = f.tell()
        iovalue.output(f, families)

        couples_pos = f.tell()
        iovalue.output(f, couples)

        descends_pos = f.tell()
        iovalue.output(f, descends)

        strings_pos = f.tell()
        iovalue.output(f, strings)

        end_pos = f.tell()

        persons_offsets = []
        current_pos = persons_pos + iovalue.array_header_size(len(persons))
        for person in persons:
            persons_offsets.append(current_pos)
            current_pos += iovalue.size(person)

        ascends_offsets = []
        current_pos = ascends_pos + iovalue.array_header_size(len(ascends))
        for ascend in ascends:
            ascends_offsets.append(current_pos)
            current_pos += iovalue.size(ascend)

        unions_offsets = []
        current_pos = unions_pos + iovalue.array_header_size(len(unions))
        for union in unions:
            unions_offsets.append(current_pos)
            current_pos += iovalue.size(union)

        families_offsets = []
        current_pos = families_pos + iovalue.array_header_size(len(families))
        for family in families:
            families_offsets.append(current_pos)
            current_pos += iovalue.size(family)

        couples_offsets = []
        current_pos = couples_pos + iovalue.array_header_size(len(couples))
        for couple in couples:
            couples_offsets.append(current_pos)
            current_pos += iovalue.size(couple)

        descends_offsets = []
        current_pos = descends_pos + iovalue.array_header_size(len(descends))
        for descend in descends:
            descends_offsets.append(current_pos)
            current_pos += iovalue.size(descend)

        strings_offsets = []
        current_pos = strings_pos + iovalue.array_header_size(len(strings))
        for string in strings:
            strings_offsets.append(current_pos)
            current_pos += iovalue.size(string)

        f.seek(header_end)
        database.output_binary_int(f, persons_pos)
        database.output_binary_int(f, ascends_pos)
        database.output_binary_int(f, unions_pos)
        database.output_binary_int(f, families_pos)
        database.output_binary_int(f, couples_pos)
        database.output_binary_int(f, descends_pos)
        database.output_binary_int(f, strings_pos)

    base_acc_file = os.path.join(gwb_path, "base.acc")
    with open(base_acc_file, 'wb') as f:
        for offset in persons_offsets:
            database.output_binary_int(f, offset)
        for offset in ascends_offsets:
            database.output_binary_int(f, offset)
        for offset in unions_offsets:
            database.output_binary_int(f, offset)
        for offset in families_offsets:
            database.output_binary_int(f, offset)
        for offset in couples_offsets:
            database.output_binary_int(f, offset)
        for offset in descends_offsets:
            database.output_binary_int(f, offset)
        for offset in strings_offsets:
            database.output_binary_int(f, offset)

    generate_name_indexes(gwb_path, persons, strings)

    return gwb_path

def generate_name_indexes(gwb_path, persons, strings):
    names_inx_file = os.path.join(gwb_path, "names.inx")
    snames_inx_file = os.path.join(gwb_path, "snames.inx")
    snames_dat_file = os.path.join(gwb_path, "snames.dat")
    fnames_inx_file = os.path.join(gwb_path, "fnames.inx")
    fnames_dat_file = os.path.join(gwb_path, "fnames.dat")

    names_table = [[] for _ in range(database.TABLE_SIZE)]
    snames_table = {}
    fnames_table = {}

    for i, person in enumerate(persons):
        if isinstance(person, dict) and 'fields' in person:
            fields = person['fields']
            fname_idx = fields[0] if len(fields) > 0 else 0
            sname_idx = fields[1] if len(fields) > 1 else 0
        elif isinstance(person, list):
            fname_idx = person[0] if len(person) > 0 else 0
            sname_idx = person[1] if len(person) > 1 else 0
        else:
            continue

        if fname_idx >= len(strings) or sname_idx >= len(strings):
            continue

        fname = strings[fname_idx] if isinstance(strings[fname_idx], str) else strings[fname_idx].decode('utf-8', errors='ignore')
        sname = strings[sname_idx] if isinstance(strings[sname_idx], str) else strings[sname_idx].decode('utf-8', errors='ignore')

        if fname and sname and fname != "?" and sname != "?":
            full_name = f"{fname} {sname}"
            idx = hash(name.crush_lower(full_name)) % database.TABLE_SIZE
            if i not in names_table[idx]:
                names_table[idx].append(i)

            if sname_idx not in snames_table:
                snames_table[sname_idx] = []
            if i not in snames_table[sname_idx]:
                snames_table[sname_idx].append(i)

            if fname_idx not in fnames_table:
                fnames_table[fname_idx] = []
            if i not in fnames_table[fname_idx]:
                fnames_table[fname_idx].append(i)

    with open(names_inx_file, 'wb') as f:
        database.output_binary_int(f, 0)
        iovalue.output(f, names_table)

    snames_bt = sorted(snames_table.items(), key=lambda x: strings[x[0]] if x[0] < len(strings) else "")
    with open(snames_dat_file, 'wb') as f:
        snames_inx_data = []
        for istr, ipers in snames_bt:
            pos = f.tell()
            database.output_binary_int(f, len(ipers))
            for ip in ipers:
                database.output_binary_int(f, ip)
            snames_inx_data.append([istr, pos])

    with open(snames_inx_file, 'wb') as f:
        iovalue.output(f, snames_inx_data)

    fnames_bt = sorted(fnames_table.items(), key=lambda x: strings[x[0]] if x[0] < len(strings) else "")
    with open(fnames_dat_file, 'wb') as f:
        fnames_inx_data = []
        for istr, ipers in fnames_bt:
            pos = f.tell()
            database.output_binary_int(f, len(ipers))
            for ip in ipers:
                database.output_binary_int(f, ip)
            fnames_inx_data.append([istr, pos])

    with open(fnames_inx_file, 'wb') as f:
        iovalue.output(f, fnames_inx_data)
