import os
from lib import database
from lib import iovalue
from lib import secure

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
        {'tag': 0, 'fields': [[0]]}
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
        for _ in range(persons_len):
            database.output_binary_int(f, 0)
        for _ in range(persons_len):
            database.output_binary_int(f, 0)
        for _ in range(persons_len):
            database.output_binary_int(f, 0)
        for _ in range(families_len):
            database.output_binary_int(f, 0)
        for _ in range(families_len):
            database.output_binary_int(f, 0)
        for _ in range(families_len):
            database.output_binary_int(f, 0)
        for _ in range(strings_len):
            database.output_binary_int(f, 0)

    return gwb_path
