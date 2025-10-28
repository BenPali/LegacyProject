# Python Modules — Overview and Behavior

This document summarizes the implemented Python modules, their responsibilities, and how they work. Descriptions are based on the actual code.

## Core and Types

- `gwdef.py` — Genealogical data structures (persons, families, events, titles, warnings). Provides enums (`Sex`, `Access`, `GenPersEventName`, `GenFamEventName`, etc.) and dataclasses `GenPerson`, `GenFamily`, `GenPersEvent`, `GenFamEvent`, plus `BaseNotes`.
- `adef.py` — Generic types and helpers (dates, calendars, pairs, constants). Underpins date conversions and representations.
- `date.py` — Date conversions and comparisons. Implements compression/decompression of `Dmy`, conversion between `Date` and `Cdate`, and helpers for strict/non‑strict date comparison.
- `calendar.py` — Calendar conversions and wrappers for `Dmy`/`Dmy2`.
- `name.py` — Name normalization: abbreviations, diacritics removal, lowercase, concatenation, and forbidden character checks.
- `utf8.py` — UTF‑8 helpers (iteration, length) used by name normalization.

## Database

- `dbdisk.py` — Disk‑layer contracts and interfaces: `RecordAccess`, `StringPersonIndex`, `BaseData`, `BaseFunc`, `BaseVersion`, `DskBase`, and `Perm`. Defines data shapes and functions consumed by the base.
- `database.py` — Opening and reading a GeneWeb base. `with_database` checks magic numbers to determine `BaseVersion`, builds immutable table accessors, applies patches (`input_patches`/`commit_patches`), loads synchronization (`input_synchro`) and `particles.txt`. Exposes name/firstname indexes according to version and runs a callback with `DskBase`.
- `driver.py` — High‑level access to persons/families. Lazily loads `GenPerson`, `GenFamily`, `GenAscend`, `GenUnion` from disk access and exposes helpers to navigate (e.g., `gen_person_of_person`, `no_person`).
- `dutil.py` — Conversions between disk structures and generic ones (e.g., `person_to_gen_person`, `ascend_to_gen_ascend`) and small index/sort utilities.
- `outbase.py` — Writing a base and its indexes. Produces `base`, `base.acc`, `names.inx/acc`, `snames.dat/inx`, `fnames.dat/inx`, `nb_persons`, notes, and `particles.txt`. Uses `secure`/`iovalue` and atomic renames of temporary files.
- `filesystem.py` — Safe file operations: directory creation with permissions, copy, remove, type/permission checks.
- `secure.py` — Guardrails for file access: checks allowed paths and provides open wrappers (`open_in_bin`, `open_out_bin`, etc.).

## I/O

- `iovalue.py` — Binary serialization of values: read (`input_value`) and write (`output`) integers, strings, blocks, lists/dicts via a simple binary protocol. Provides `SIZEOF_LONG` and `output_array_access` for indexed tables.
- `output.py` — Bridge to configured output: writes headers and content via `conf.output_conf`.
- `json_converter.py` — JSON conversions for interchange and debugging.

## Events and Data

- `event.py` — Event comparison and sort. Defines logical ordering (birth before death, etc.) and sorts by date then type via `sort_events`.
- `futil.py` — Mapping functions for events/persons/families: field remapping and name transforms (generic) with date conversions when applicable.
- `hasher.py` — Builds hashes (SHA256) from `gwdef` structures: dedicated feeders for events and fields.
- `notes_links.py` — Notes and links handling (association and cleanup).

## General Utilities

- `util.py` — UI and logic helpers (translations via `transl`, HTML helpers, paths via `etc`, list/string ops, event formatting). Cross‑cutting utility layer.
- `mutil.py` — String utilities; normalization support.
- `loc.py` — Provenance references for messages/errors.
- `lock.py` — Basic file locking.
- `collection.py`, `buff.py`, `pqueue.py`, `gutil.py` — Complementary structures/utilities (buffers, priority queues, traversal/sort).

## Diff, Compatibility, Compression

- `difference.py` — Myers‑style diff for comparing arrays/structures.
- `compat.py`, `geneweb_compat.py` — Compatibility helpers with GeneWeb formats and legacy schemas.
- `my_gzip.py` — Gzip read/write.
- `my_unix.py` — Unix helpers (platform‑specific).

## Web Layer and Daemon

- `wserver.py` — Web server skeleton and generic handlers.
- `wserver_util.py` — Response/rendering utilities.
- `modernProject/bin` — Startup/routing scripts (if present).

## UI and Display

- `templ.py` — Template engine.
- `ast.py` — Template AST (nodes and validations).
- `progr_bar.py` — Progress display.

## Operational Notes

- Base opening: use `with_database(bname, k)` which verifies version via magic numbers and builds disk accessors.
- Patches: loaded via `input_patches` (checks `MAGIC_PATCH`) and committed by `commit_patches` with atomic writes to `patches`.
- Synchronization: `input_synchro` reads `synchro_patches` and returns `SynchroPath` (empty on error).
- Name/firstname indexes: produced in `outbase.py` (inx/dat creation) and consumed in `database.py` via `persons_of_surname`/`persons_of_first_name` according to `BaseVersion`.
- Files: `secure` ensures safe paths; `filesystem` handles permissions/moves.
- Serialization: `iovalue` encodes/decodes structures using a dedicated binary protocol.

## Usage Tips

- Access bases via `with_database`; avoid raw file I/O without `secure`.
- Normalize names and dates consistently (`name`, `mutil`, `date`).
- Use indexes (`StringPersonIndex`) for efficient lookups.
- Keep core (base/logic) separated from UI/web modules to avoid tight coupling.

---

This guide intentionally remains concise and reflects observed behavior in code. For details, refer to docstrings and unit tests.
