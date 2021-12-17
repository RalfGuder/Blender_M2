from dataclasses import make_dataclass
from dbcpy.loc import Loc, NString, Vec3F


_fields = {
    'ID': int,
    'Name': NString,
    'WeaponFlags': int,
    'BodyFlags': int,
    'Scale': int,
    'Fallback_ID': int,
    'BehaviorID': int,
    'BehaviorTier': int
}

_record = make_dataclass('AnimationDataRec', zip(_fields.keys(), _fields.values()))
_record.field_types = staticmethod(_fields.values())