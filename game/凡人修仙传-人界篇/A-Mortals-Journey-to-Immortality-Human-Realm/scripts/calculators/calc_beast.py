# 凡人修仙传-人界篇 · 概率计算引擎 · 灵兽系统 §9
#
# 本文件为概率计算框架。灵兽的品质、种类、名称、特殊能力均由AI根据
# 角色所处环境动态创造——可以是常见灵兽，也可以是独一无二的珍兽。

import random
from .calc_utils import clamp


def calc_beast_taming(player_sense: int, beast_sense: int) -> bool:
    """灵兽契约判定 §9.1/§21: rate=30%+sense_diff*2%"""
    rate = 0.30 + (player_sense - beast_sense) * 0.02
    rate = clamp(rate, 0.01, 0.95)
    return random.random() < rate


def calc_beast_loyalty(base_loyalty: int = 60) -> int:
    """灵兽初始忠诚度 §9.4: 随机60-100"""
    return random.randint(base_loyalty, 100)


def calc_beast_betray(loyalty: int) -> bool:
    """灵兽叛逃判定 §9.4: 忠诚<30时可能叛逃"""
    if loyalty >= 30:
        return False
    rate = (30 - loyalty) * 0.05
    return random.random() < rate
