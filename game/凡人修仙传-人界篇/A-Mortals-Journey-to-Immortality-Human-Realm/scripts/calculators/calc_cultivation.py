# 凡人修仙传-人界篇 · 概率计算引擎 · 修炼体系
# 包含: 突破§2.3 / 天劫§12 / 业力气运§13 / 心境心魔§15 / 夺舍§18 / 常用判定速查§21

import random
from .calc_utils import clamp


# == 突破 §2.3 ==
def calc_breakthrough(base_rate: float, difficulty: float, bonuses: dict) -> tuple:
    """突破判定: rate=base*(1/diff)*Πbonus, [1%,99%], returns(success,rate)"""
    # 兼容 CLI 字符串格式: key=value,key=value
    if isinstance(bonuses, str):
        parsed = {}
        for part in bonuses.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                try:
                    parsed[k] = float(v)
                except ValueError:
                    parsed[k] = v
        bonuses = parsed
    rate = base_rate * (1.0 / difficulty)
    for b in bonuses.values():
        rate *= b
    rate = clamp(rate, 0.01, 0.99)
    return (random.random() < rate, rate)


def calc_breakthrough_failure() -> str:
    """突破失败后果: 轻伤40%/重伤25%/修为尽失20%/走火入魔10%/死亡5%"""
    r = random.random()
    if r < 0.40:
        return "轻伤"
    if r < 0.65:
        return "重伤"
    if r < 0.85:
        return "修为尽失"
    if r < 0.95:
        return "走火入魔"
    return "死亡"


# == 天劫 §12 ==
def calc_tribulation_trigger() -> bool:
    """天劫触发 §12.1/§21: 大境界突破时30%概率触发"""
    return random.random() < 0.30


def calc_tribulation_type(karma: int = 0, fire_affinity: float = 0.0) -> str:
    """天劫类型判定 §12.2"""
    if karma < -50:
        return random.choices(["雷劫", "心魔劫", "双重劫"], weights=[0.20, 0.50, 0.30])[
            0
        ]
    if fire_affinity > 0.5:
        return random.choices(["雷劫", "火劫", "心魔劫"], weights=[0.40, 0.40, 0.20])[0]
    return random.choices(
        ["雷劫", "火劫", "心魔劫", "双重劫"], weights=[0.60, 0.10, 0.20, 0.10]
    )[0]


def calc_tribulation_damage(realm_tier: int, tribulation_type: str) -> int:
    """天劫威力 §12: realm_tier境界等级(炼气1~化神5)"""
    base_dmg = realm_tier * 50
    multipliers = {"雷劫": 1.0, "火劫": 1.3, "心魔劫": 0.8, "双重劫": 1.8}
    return int(base_dmg * multipliers.get(tribulation_type, 1.0))


# == 因果/业力/气运 §13 ==
def calc_karma_event(karma: int) -> str:
    """业力触发事件 §13.1: |karma|>50触发"""
    abs_karma = abs(karma)
    if abs_karma < 50:
        return "无事件"

    if karma > 0:
        events = [
            "遇贵人相助",
            "意外获得机缘",
            "天劫威力减弱",
            "有人暗中相救",
        ]
        return random.choice(events)
    else:
        events = [
            "遭天谴(被雷劈)",
            "心魔入侵",
            "修炼走火入魔",
            "仇家寻上门",
            "运势骤降",
        ]
        return random.choice(events)


def calc_luck_modifier(qi_yun: int) -> float:
    """气运修正 §13.2: qi_yun≤0时-10%"""
    if qi_yun <= 0:
        return -0.10
    return 0.0


# == 心魔/心境 §15 ==
def calc_mind_change(event_type: str) -> int:
    """心境变化 §15.1: 返回变化值"""
    changes = {
        "突破成功": random.randint(5, 10),
        "突破失败": random.randint(-15, -5),
        "杀人(善)": random.randint(-10, -2),
        "杀人(恶)": random.randint(-5, 0),
        "被杀/重伤": random.randint(-20, -10),
        "获得重宝": random.randint(3, 8),
        "失去重宝": random.randint(-15, -5),
        "道侣死亡": -30,
        "闭关太久": -1,
        "游历山水": 1,
        "完成心愿": random.randint(10, 20),
    }
    return changes.get(event_type, 0)


def calc_mind_effect(mind: int) -> dict:
    """心境等级效果 §15.2"""
    if mind >= 100:
        return {"label": "通明", "breakthrough_bonus": 0.15, "immune_heart_demon": True}
    if mind >= 80:
        return {
            "label": "平和",
            "breakthrough_bonus": 0.10,
            "immune_heart_demon": False,
        }
    if mind >= 60:
        return {"label": "正常", "breakthrough_bonus": 0, "immune_heart_demon": False}
    if mind >= 40:
        return {
            "label": "烦躁",
            "breakthrough_bonus": -0.10,
            "demon_chance_bonus": 0.05,
        }
    if mind >= 20:
        return {
            "label": "混乱",
            "breakthrough_bonus": -0.20,
            "demon_chance_bonus": 0.15,
        }
    return {
        "label": "疯魔",
        "breakthrough_bonus": 0,
        "can_cultivate": False,
        "self_harm_chance": 0.50,
    }


def calc_heart_demon(mind: int, karma: int = 0) -> bool:
    """心魔入侵判定 §15.3/§21: base=8%(<40→15%,<20→30%), +负业力加成"""
    if mind < 20:
        rate = 0.30
    elif mind < 40:
        rate = 0.15
    else:
        rate = 0.08
    if karma < 0:
        rate += min(abs(karma) * 0.002, 0.20)
    rate = clamp(rate, 0.01, 0.80)
    return random.random() < rate


def calc_heart_demon_resist(sense: int, mind: int) -> bool:
    """心魔抵抗判定 §15.3: rate=sense*1%+mind*0.5%"""
    rate = sense * 0.01 + mind * 0.005
    rate = clamp(rate, 0.05, 0.90)
    return random.random() < rate


# == 夺舍 §18 ==
def calc_possess(
    attacker_sense: int, target_sense: int, target_has_protection: bool = False
) -> tuple:
    """夺舍判定 §18.1: rate=sense_diff*2%, 护魂减半, [1%,80%]"""
    rate = (attacker_sense - target_sense) * 0.02
    if target_has_protection:
        rate *= 0.5
    rate = clamp(rate, 0.01, 0.80)
    return (random.random() < rate, rate)


# == 常用判定速查 §21 ==
def calc_probe_deception(sense: int, wu_xing: int) -> bool:
    """识破骗局 §21: rate=30%+sense*0.5%+wu_xing*0.3%"""
    rate = 0.30 + sense * 0.005 + wu_xing * 0.003
    return random.random() < rate


def calc_encounter(ji_yuan: int) -> bool:
    """遇到机缘 §21: rate=5%+ji_yuan*0.1%"""
    rate = 0.05 + ji_yuan * 0.001
    return random.random() < rate


def calc_possess_resist(sense: int, has_protection: bool = False) -> bool:
    """被夺舍抵抗 §21: rate=sense*1%+保护加成"""
    rate = sense * 0.01
    if has_protection:
        rate += 0.30
    rate = clamp(rate, 0.05, 0.95)
    return random.random() < rate


def calc_escape_discovery(stealth_level: int, detector_sense: int) -> bool:
    """隐匿/被发现判定(通用)"""
    rate = 0.30 + stealth_level * 0.05 - detector_sense * 0.005
    rate = clamp(rate, 0.05, 0.95)
    return random.random() < rate
