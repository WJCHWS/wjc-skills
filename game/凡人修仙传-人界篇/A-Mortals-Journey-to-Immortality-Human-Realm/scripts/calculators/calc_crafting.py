# 凡人修仙传-人界篇 · 概率计算引擎 · 生产技能（炼丹§5 / 炼器§6 / 制符§8 / 阵法§7）
#
# 本文件为概率计算框架。硬编码的品质加成（herb_bonuses/furnace_bonuses等）
# 仅为默认参考值，AI可根据世界设定动态调整——例如某区域的"地火"可能比普通地火更强。
# 丹药/法器/符箓/阵法的具体名称、效果、材料，均由AI根据角色环境和剧情创造。

import random
from .calc_utils import clamp


# == 炼丹 §5 ==
def calc_alchemy(
    level: int,
    wu_xing: int,
    herb_q: str = "普通",
    years: int = 0,
    furnace: str = "法器",
    fire: str = "地火",
    aux: int = 0,
    phys_bonus: float = 0.0,
) -> str:
    """炼丹结果（返回品质标签，AI据此创造具体的丹药名称和外观描述）"""
    base = 0.10 + level * 0.04 + wu_xing * 0.0015 + phys_bonus

    herb_bonuses = {"普通": 0, "灵草": 0.05, "珍稀": 0.10}
    total = base + herb_bonuses.get(herb_q, 0)

    year_bonus = 0
    if years >= 1000:
        year_bonus = 0.25
    elif years >= 500:
        year_bonus = 0.15
    elif years >= 100:
        year_bonus = 0.10
    elif years >= 50:
        year_bonus = 0.05
    elif years >= 10:
        year_bonus = 0.02
    total += year_bonus

    furnace_bonuses = {"凡器": -0.05, "法器": 0, "灵器": 0.08, "法宝": 0.15}
    fire_bonuses = {"凡火": -0.10, "地火": 0, "灵火": 0.10, "异火": 0.20}
    total += furnace_bonuses.get(furnace, 0) + fire_bonuses.get(fire, 0)
    total += min(aux * 0.02, 0.10)
    total = clamp(total, 0.01, 0.95)

    r = random.random()
    if r < 0.05:
        return "炸炉"
    if r < 0.25:
        return "废丹"
    if r < 0.70:
        return "普通"
    if r < 0.88:
        return "上品"
    if r < 0.96:
        return "极品"
    return "绝品"


def calc_alchemy_success_rate(
    level: int,
    wu_xing: int,
    herb_q: str = "普通",
    years: int = 0,
    furnace: str = "法器",
    fire: str = "地火",
    aux: int = 0,
    phys_bonus: float = 0.0,
) -> dict:
    """炼丹成功率明细 §5.3: 返回各步骤加成明细"""
    base = 0.10 + level * 0.04 + wu_xing * 0.0015 + phys_bonus
    herb_b = {"普通": 0, "灵草": 0.05, "珍稀": 0.10}.get(herb_q, 0)
    year_b = 0
    if years >= 1000:
        year_b = 0.25
    elif years >= 500:
        year_b = 0.15
    elif years >= 100:
        year_b = 0.10
    elif years >= 50:
        year_b = 0.05
    elif years >= 10:
        year_b = 0.02
    furnace_b = {"凡器": -0.05, "法器": 0, "灵器": 0.08, "法宝": 0.15}.get(furnace, 0)
    fire_b = {"凡火": -0.10, "地火": 0, "灵火": 0.10, "异火": 0.20}.get(fire, 0)
    aux_b = min(aux * 0.02, 0.10)

    total = min(0.95, base + herb_b + year_b + furnace_b + fire_b + aux_b)
    return {
        "基础成功率": base,
        "药材加成": herb_b,
        "年份加成": year_b,
        "丹炉加成": furnace_b,
        "地火加成": fire_b,
        "辅材加成": aux_b,
        "最终成功率": total,
    }


# == 炼器 §6 ==
def calc_forging(
    level: int,
    wu_xing: int,
    material_q: str = "普通",
    fire: str = "地火",
    phys_bonus: float = 0.0,
) -> str:
    """炼器结果（返回品质标签，AI据此创造具体法器名称和外观描述）"""
    base = 0.15 + level * 0.03 + wu_xing * 0.001 + phys_bonus
    material_bonus = {"普通": 0, "灵材": 0.05, "珍稀": 0.12}
    fire_bonus = {"凡火": -0.10, "地火": 0, "灵火": 0.08, "异火": 0.15}
    total = base + material_bonus.get(material_q, 0) + fire_bonus.get(fire, 0)
    total = clamp(total, 0.01, 0.95)

    r = random.random()
    if r < 0.20:
        return "失败"
    if r < 0.45:
        return "次品"
    if r < 0.75:
        return "良品"
    if r < 0.92:
        return "精品"
    return "极品"


# == 符箓 §8 ==
def calc_talisman(level: int, wu_xing: int) -> bool:
    """制符判定 §8.3: rate=10%+lv*3%+wu_xing*0.1%"""
    rate = 0.10 + level * 0.03 + wu_xing * 0.001
    rate = clamp(rate, 0.01, 0.95)
    return random.random() < rate


# == 阵法 §7 ==
def calc_formation(formation_level: int, wu_xing: int) -> bool:
    """布阵判定 §21: rate=20%+lv*5%+wu_xing*0.2%"""
    rate = 0.20 + formation_level * 0.05 + wu_xing * 0.002
    rate = clamp(rate, 0.01, 0.99)
    return random.random() < rate


def calc_formation_break(sense: int, formation_tier: int, force: bool = False) -> bool:
    """破阵判定 §7.3: 神识探测或强行攻破"""
    if force:
        rate = max(0.05, 0.50 - formation_tier * 0.05)
    else:
        rate = 0.20 + sense * 0.01 - formation_tier * 0.03
    rate = clamp(rate, 0.01, 0.90)
    return random.random() < rate
