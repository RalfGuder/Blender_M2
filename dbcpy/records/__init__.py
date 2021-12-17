"""
stores different representations of dbc file structures,
for different types of dbcs @see https://wowdev.wiki/Category:DBC_WotLK
"""
from dbcpy.records.item_display_info import _record as _ItemDisplayInfoRec
from dbcpy.records.creature_model_data import _record as _CreatureModelDataRec
from dbcpy.records.creature_display_info import _record as _CreatureDisplayInfoRec
from dbcpy.records.animation_data import _record as _AnimationDataRec


ItemDisplayInfoRec = _ItemDisplayInfoRec
CreatureModelDataRec = _CreatureModelDataRec
CreatureDisplayInfoRec = _CreatureDisplayInfoRec
AnimationDataRec = _AnimationDataRec