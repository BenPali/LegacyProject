# OCaml to Python Migration Status

## Overall Progress: 39/115 modules (33.9%)

**Final Target:** 115/115 modules (100%)
**Remaining:** 76 modules needed

---

## Completed Modules (39/115)

| Module | Lines | Python File | Tests | Notes |
|--------|-------|-------------|-------|-------|
| adef | 79 | adef.py | ✅ | Core date/calendar types |
| ansel | 284 | ansel.py | ✅ | ANSEL character encoding |
| ast | 201 | ast.py | ✅ | Template AST |
| avl | 112 | avl.py | ✅ | AVL tree |
| buff | 36 | buff.py | ✅ | String buffer |
| calendar | 66 | calendar.py | ✅ | Calendar conversions |
| collection | 70 | collection.py | ✅ | Lazy collections |
| config | 201 | config.py | ✅ | Configuration |
| date | 222 | date.py | ✅ | Date operations |
| database | 1440 | database.py | ✅ | Main database module (70% coverage, production ready) |
| dbdisk | 71 | dbdisk.py | ✅ | Database disk structures |
| def | 473 | gwdef.py | ✅ | Core type definitions (renamed to avoid keyword) |
| dutil | 76 | dutil.py | ✅ | Database utilities |
| event | 108 | event.py | ✅ | Event sorting and comparison |
| futil | 298 | futil.py | ✅ | Functional utilities for person/family data |
| filesystem | 122 | filesystem.py | ✅ | File operations |
| geneweb_compat | 61 | geneweb_compat.py | ✅ | GeneWeb compatibility |
| gutil | 304 | gutil.py | ✅ | General database utilities (95% coverage) |
| gw_ancient | 13 | gw_ancient.py | ✅ | Ancient data stubs |
| iovalue | 209 | iovalue.py | ✅ | Binary serialization |
| json_converter | 247 | json_converter.py | ✅ | JSON utilities |
| loc | 46 | loc.py | ✅ | Source location |
| lock | 36 | lock.py | ✅ | File locking |
| logs | 101 | logs.py | ✅ | Logging utilities |
| mutil | 1276 | mutil.py | ✅ | String utilities |
| my_gzip | 82 | my_gzip.py | ✅ | Gzip handling |
| my_unix | 7 | my_unix.py | ✅ | Unix utilities |
| name | 266 | name.py | ✅ | Name processing |
| outbase | 404 | outbase.py | ✅ | Database output (85% coverage) |
| output | 11 | output.py | ✅ | Output abstraction |
| pool | 56 | pool.py | ✅ | Worker pool |
| pqueue | 58 | pqueue.py | ✅ | Priority queue |
| progrBar | 84 | progr_bar.py | ✅ | Progress bar |
| secure | 120 | secure.py | ✅ | Secure file access |
| sosa | 24 | sosa.py | ✅ | Sosa numbering |
| stats | 123 | stats.py | ✅ | Database statistics (95% coverage) |
| templ | 1543 | templ.py | ✅ | Template rendering |
| wserver | 367 | wserver.py | ✅ | Web server basics |
| wserver_util | 9 | wserver_util.py | ✅ | Web server utilities |

**Note:** `compat.py` exists in modernProject/lib as a Python helper module but is not counted as it has no corresponding OCaml source file.

---

## Core Modules

### Tier 1: Unblocked by def.py

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| stats | 123 | Def | Database statistics calculation |

### Tier 2: Simple Utility Modules (Independent)

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| consangAll | 145 | Def | Consanguinity calculations for all persons |
| birthDeath | 116 | Def | Birth/death analysis |
| changeChildren | 98 | Def | Children modification utilities |
| utf8 | 229 | (external: Uucp, Uutf) | UTF-8 string operations |
| title | 242 | Def | Nobility title processing |
| difference | 174 | Def | Database difference analysis |
| notesLinks | 157 | Def | Notes and links handling |
| alln | 157 | Def | Name listings |

### Tier 3: Medium Complexity Modules

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| consang | 298 | Def | Core consanguinity calculations |
| db_gc | 186 | Def | Database garbage collection |
| check | 356 | Def | Database consistency checking |
| hasher | 469 | - | Hash table utilities |
| translate | 308 | Def | Translation utilities |
| sosaCache | 330 | Def | Sosa number caching |

### Tier 4: Complex Core Modules

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| driver | 864 | Def | Database driver implementation |
| database | 1440 | Def, Driver | Main database module |
| util | 3101 | Def, Config | Large utility collection |
| fixbase | 496 | Def | Database fixing utilities |
| checkData | 559 | Def | Data validation |
| checkItem | 1129 | Def | Item checking |

---

## Display & Web UI Modules (Lower Priority - 41 modules)

These modules handle HTML/web display and can be implemented later:

### Small Display Modules (~< 100 lines)

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| advSearchOkDisplay | 55 | Def | Advanced search results display |
| ascendDisplay | 68 | Def | Ascendant tree display |
| checkDataDisplay | 104 | Def | Data checking results display |
| mergeIndOkDisplay | 88 | Def | Individual merge confirmation display |

### Medium Display Modules (100-1000 lines)

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| mergeDupDisplay | 154 | Def | Duplicate merge display |
| mergeDisplay | 161 | Def | General merge display |
| imageDisplay | 191 | Def | Image gallery display |
| mergeFamDisplay | 192 | Def | Family merge display |
| changeChildrenDisplay | 205 | Def | Children modification display |
| placeDisplay | 222 | Def | Place information display |
| allnDisplay | 331 | Def | Name listing display |
| titleDisplay | 332 | Def | Title display |
| updateDataDisplay | 494 | Def | Data update display |
| mergeIndDisplay | 510 | Def | Individual merge display |
| birthDeathDisplay | 556 | Def | Birth/death display |
| srcfileDisplay | 596 | Def | Source file display |
| birthdayDisplay | 611 | Def | Birthday list display |
| dateDisplay | 670 | Def | Date display formatting |
| wiznotesDisplay | 696 | Def | Wizard notes display |
| notesDisplay | 895 | Def | Notes display |
| imageCarrousel | 986 | Def | Image carousel display |
| historyDiffDisplay | 994 | Def | History difference display |

### Large Display Modules (> 1000 lines)

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| relationDisplay | 1104 | Def | Relationship display |
| dagDisplay | 1378 | Def | DAG visualization display |
| descendDisplay | 1933 | Def | Descendant tree display |
| perso | 5637 | Def | Personal page display (HUGE) |

### Display Support Modules

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| hutil | 261 | Def | HTML utilities |
| cousinsDisplay | 433 | Def | Cousins relationship display |
| historyDiff | 284 | Def | History difference calculation |

---

## Update/Merge/Search Modules (Specialized - 23 modules)

These handle database updates, merges, and search functionality:

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| update | 1362 | Def | General update operations |
| updateFam | 828 | Def | Family update operations |
| updateFamOk | 1539 | Def | Family update confirmation |
| updateInd | 748 | Def | Individual update operations |
| updateIndOk | 1248 | Def | Individual update confirmation |
| updateData | 616 | Def | Data update operations |
| update_util | 366 | Def | Update utilities |
| mergeInd | 392 | Def | Individual merge operations |
| mergeIndOk | 605 | Def | Individual merge confirmation |
| mergeFamOk | 306 | Def | Family merge confirmation |
| searchName | 553 | Def | Name search |
| advSearchOk | 661 | Def | Advanced search operations |
| relation | 562 | Def | Relationship calculation |
| relationLink | 822 | Def | Relationship linking |
| cousins | 599 | Def | Cousin calculation |
| place | 782 | Def | Place management |
| image | 552 | Def | Image management |
| notes | 701 | Def | Notes management |
| history | 663 | Def | History tracking |
| wiki | 1058 | Def | Wiki functionality |
| some | 874 | Def | Some utilities |
| GWPARAM | 601 | Def | GeneWeb parameters |
| def_show | 92 | Def | Definition display |

---

## Special/Variant Modules (4 modules)

| Module | Lines | Dependencies | Description |
|--------|-------|--------------|-------------|
| geneweb_sosa.array | 230 | - | Sosa numbering (array variant) |
| geneweb_sosa.zarith | 59 | - | Sosa numbering (zarith variant) |
| gw_ancient.dum | 7 | - | Ancient data dummy |
| gw_ancient.wrapped | 3 | - | Ancient data wrapped |
| parser | 63 | Templ | Template parser |
| dag2html | 1416 | Def | DAG to HTML conversion |
| util (wserver) | 9 | - | Web server utility variant |

---

## Dependency Summary

### Key Blockers Resolved:
- ✅ **Adef** - Core date/calendar types
- ✅ **Def** - Core genealogical types (as gwdef.py)
- ✅ **Mutil** - String utilities
- ✅ **Name** - Name processing
- ✅ **Date** - Date operations
- ✅ **Database** - Database support

### Most Dependent Modules (Blocking Many Others):
1. **Driver** (864 lines) - Required by: Database, many query modules
2. **Util** (3101 lines) - Required by: Many UI and query modules
3. **Config** - Required by: Most application modules (partially done)

---

## Planned Implementation Order

### Phase 1: Core Utilities
Priority to unblock maximum dependencies:
1. ✅ **event** (108) - Event handling
2. ✅ **futil** (298) - Functional utilities
3. ✅ **gutil** (304) - Database utilities
4. ✅ **stats** (123) - Statistics
5. **consang** (298) - Consanguinity
6. **consangAll** (145) - Extended consanguinity
7. **utf8** (229) - Text processing
8. **title** (242) - Title handling
9. **birthDeath** (116) - Birth/death logic
10. **changeChildren** (98) - Children modifications

### Phase 2: Database Core
Essential for database operations:
1. **driver** (864) - Database driver ⚠️ CRITICAL
2. **db_gc** (186) - Garbage collection
3. **check** (356) - Consistency checking
4. **checkData** (559) - Data validation
5. **checkItem** (1129) - Item validation
6. **fixbase** (496) - Database fixes

### Phase 3: Query & Relationship
1. **relation** (562)
2. **relationLink** (822)
3. **cousins** (599)
4. **searchName** (553)
5. **place** (782)
6. **sosaCache** (330)
7. **alln** (157)
8. **notesLinks** (157)
9. **difference** (174)
10. **hasher** (469)

### Phase 4: Update Operations
1. **update_util** (366)
2. **updateData** (616)
3. **update** (1362)
4. **updateInd** (748)
5. **updateIndOk** (1248)
6. **updateFam** (828)
7. **updateFamOk** (1539)
8. **mergeInd** (392)
9. **mergeIndOk** (605)
10. **mergeFamOk** (306)
11. **advSearchOk** (661)

### Phase 5: Display Modules
Implement display modules after core logic is stable

### Phase 6: Remaining Specialized
- Util (3101), perso (5637), and other large specialized modules

---

## Progress Milestones

- [x] 25% - 29 modules (PASSED ✅)
- [ ] 50% - 58 modules (Need 19 more)
- [ ] 75% - 87 modules (Need 48 more)
- [ ] 100% - 115 modules (Need 76 more) 🎯

---

**Last Updated:** 2025-10-17
**Next Target:** consang.py
