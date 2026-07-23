# 凡人修仙传-人界篇 · 概率计算引擎 · 战斗系统 §4
# 
# 本文件为概率计算框架。所有硬编码（场景类型、状态效果、五行相克）仅为数值参考，
# AI在叙事中可自由创造新场景、新状态、新元素，只需传入对应的 element/scene/status 参数即可。
# 例如：某个秘境可能有"幽冥之力"增强所有暗属性，AI直接传参调用即可。

import random
from .calc_utils import clamp


# == 命中/闪避/暴击 §4.2 ==
def calc_hit(atk_spd: int, def_spd: int) -> bool:
    """命中判定: hit=75%+(atk_spd-def_spd)*3%, [5%,99%]"""
    hit_rate = 0.75 + (atk_spd - def_spd) * 0.03
    hit_rate = clamp(hit_rate, 0.05, 0.99)
    return random.random() < hit_rate


def calc_dodge(atk_spd: int, def_spd: int) -> bool:
    """闪避判定: dodge=max(0,(def_spd-atk_spd)*2%)"""
    dodge_rate = max(0, (def_spd - atk_spd) * 0.02)
    return random.random() < dodge_rate


def calc_crit(ji_yuan: int) -> bool:
    """暴击判定: crit=5%+ji_yuan*0.05%"""
    crit_rate = 0.05 + ji_yuan * 0.0005
    return random.random() < crit_rate


# == 伤害计算 §4.2 ==
def calc_physical_damage(atk: int, defense: int) -> int:
    """物理伤害: dmg=max(1,ATK-DEF+随机(-1~3))"""
    return max(1, atk - defense + random.randint(-1, 3))


def calc_magical_damage(base_dmg: int, atk: int, defense: int) -> int:
    """法术伤害: dmg=max(1,base+ATK*0.5-DEF*0.5+随机(-1~3))"""
    return max(
        1, base_dmg + int(atk * 0.5) - int(defense * 0.5) + random.randint(-1, 3)
    )


def calc_crit_damage(base_damage: int) -> int:
    """暴击伤害: crit_dmg=base*(1.5~3.0)"""
    multiplier = 1.5 + random.random() * 1.5
    return int(base_damage * multiplier)


def calc_flee(atk_spd: int, def_spd: int, realm_gap: int = 0) -> bool:
    """逃跑判定 §21: rate=20%+spd_diff*5%-realm_gap*30%, [1%,90%]"""
    rate = 0.20 + (atk_spd - def_spd) * 0.05 - realm_gap * 0.30
    rate = clamp(rate, 0.01, 0.90)
    return random.random() < rate


# == 五行相克 §4.3 ==
def calc_element_multiplier(atk_element: str, def_element: str) -> float:
    """五行相克: 金克木/木克土/土克水/水克火/火克金, 克*1.5/被克*0.7/同*1.0"""
    element_map = {
        ("金", "木"): 1.5,
        ("木", "土"): 1.5,
        ("土", "水"): 1.5,
        ("水", "火"): 1.5,
        ("火", "金"): 1.5,
        ("木", "金"): 0.7,
        ("土", "木"): 0.7,
        ("水", "土"): 0.7,
        ("火", "水"): 0.7,
        ("金", "火"): 0.7,
    }
    return element_map.get((atk_element, def_element), 1.0)


# == 战斗场景加成 §4.5 ==
def calc_battle_scene_modifier(scene: str, element: str) -> float:
    """战斗场景元素加成"""
    modifiers = {
        "山地": {"土": 0.20},
        "水域": {"水": 0.20, "火": -0.20},
        "森林": {"木": 0.20},
        "火山": {"火": 0.30},
        "雪地": {"水": 0.20, "火": -0.30},
        "夜间": {"暗": 0.20},
    }
    return modifiers.get(scene, {}).get(element, 0.0)


# == 特殊状态效果 §4.4 ==
def calc_status_application(status_name: str, status_level: int = 1) -> dict:
    """特殊状态效果: 返回每回合效果字典"""
    statuses = {
        "中毒": {"per_turn_dmg": status_level * 2, "duration": 5, "max_stack": 5},
        "燃烧": {
            "per_turn_dmg": status_level * 3,
            "def_reduce": 0.20,
            "duration": 5,
            "max_stack": 3,
        },
        "冰冻": {"spd_reduce": 0.50, "skip_chance": 0.30, "duration": 3},
        "眩晕": {"skip_turns": random.randint(1, 2)},
        "重伤": {"all_stat_reduce": 0.30, "no_movement": True},
        "恐惧": {"atk_reduce": 0.30, "flee_chance": 0.20},
        "魅惑": {"confuse_chance": 0.50},
        "封印": {"no_skills": True},
    }
    return statuses.get(status_name, {})
