# 凡人修仙传-人界篇 · 概率计算引擎 · 工具函数

import random


def clamp(value, lo, hi):
    """clamp: 限制值在[lo,hi]范围内"""
    return max(lo, min(hi, value))


def weighted_choice(items, weight_key=1):
    """加权随机选择: items=[(name,weight,...),...], weight_key=权重索引(默认1)"""
    total = sum(item[weight_key] for item in items)
    r = random.random() * total
    cum = 0
    for item in items:
        cum += item[weight_key]
        if r < cum:
            return item
    return items[-1]
