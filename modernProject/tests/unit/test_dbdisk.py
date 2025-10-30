import pytest
from lib.dbdisk import (
    Perm, BaseVersion, DskBase, BaseData, BaseFunc,
    RecordAccess, StringPersonIndex, VisibleRecordAccess
)


class TestEnums:
    def test_perm_enum(self):
        assert Perm.RDONLY != Perm.RDRW
        assert Perm.RDONLY.name == "RDONLY"
        assert Perm.RDRW.name == "RDRW"

    def test_base_version_enum(self):
        assert BaseVersion.GNWB0020 != BaseVersion.GNWB0024
        assert len([v for v in BaseVersion]) == 5


class TestDataclasses:
    def test_record_access_creation(self):
        rec = RecordAccess(
            load_array=lambda: None,
            get=lambda x: x,
            get_nopending=lambda x: x,
            len=10,
            output_array=lambda x: None,
            clear_array=lambda: None
        )
        assert rec.len == 10
        assert rec.get(5) == 5

    def test_string_person_index_creation(self):
        idx = StringPersonIndex(
            find=lambda x: [x],
            cursor=lambda s: len(s),
            next=lambda x: x + 1
        )
        assert idx.find(5) == [5]
        assert idx.cursor("test") == 4
        assert idx.next(10) == 11
