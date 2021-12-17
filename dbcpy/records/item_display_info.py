from dataclasses import make_dataclass
from dbcpy.loc import Loc, NString

_fields = {
    'ID': int,
    'LeftModel': NString,
    'RightModel': NString,
    'LeftModelTexture': NString,
    'RightModelTexture': NString,
    'Icon1': NString,
    'Icon2': NString,
    'geosetGroup1': int,
    'geosetGroup2': int,
    'geosetGroup3': int,
    'flags': int,
    'spellVisualID': int,
    'groupSoundIndex': int,
    'helmetGeosetVis1': int,
    'helmetGeosetVis2': int,
    'UpperArmTexture': NString,
    'LowerArmTexture': NString,
    'HandsTexture': NString,
    'UpperTorsoTexture': NString,
    'LowerTorsoTexture': NString,
    'UpperLegTexture': NString,
    'LowerLegTexture': NString,
    'FootTexture': NString,
    'itemVisual': NString,
    'particleColorID': NString
}

_record = make_dataclass('ItemDisplayInfoRecord', zip(_fields.keys(), _fields.values()))
_record.field_types = staticmethod(_fields.values())