# 凡人修仙传-人界篇 · 概率计算引擎 · 组件包
# 按游戏领域拆分为独立模块: 工具/战斗/角色/修炼/生产/灵兽/世界

from .calc_utils import clamp, weighted_choice
from .calc_battle import (
    calc_hit, calc_dodge, calc_crit,
    calc_physical_damage, calc_magical_damage, calc_crit_damage,
    calc_flee, calc_element_multiplier, calc_battle_scene_modifier, calc_status_application,
)
from .calc_character import (
    roll_spirit_root, roll_physique, generate_physique_detail, roll_stats, roll_origin,
)
from .calc_cultivation import (
    calc_breakthrough, calc_breakthrough_failure,
    calc_tribulation_trigger, calc_tribulation_type, calc_tribulation_damage,
    calc_karma_event, calc_luck_modifier,
    calc_mind_change, calc_mind_effect, calc_heart_demon, calc_heart_demon_resist,
    calc_possess,
    calc_probe_deception, calc_encounter, calc_possess_resist, calc_escape_discovery,
)
from .calc_crafting import (
    calc_alchemy, calc_alchemy_success_rate,
    calc_forging, calc_talisman,
    calc_formation, calc_formation_break,
)
from .calc_beast import calc_beast_taming, calc_beast_loyalty, calc_beast_betray
from .calc_world import generate_world_intro
