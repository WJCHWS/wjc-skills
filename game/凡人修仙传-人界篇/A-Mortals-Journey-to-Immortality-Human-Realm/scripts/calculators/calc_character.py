# 凡人修仙传-人界篇 · 概率计算引擎 · 角色创建 §2
#
# 本文件为角色创建的概率引擎。灵根类型、五行属性、体质框架为系统数值基础，
# 但AI在叙事中可自由创造：家族的具体故事、出生地的详细地貌、特殊事件的起因经过、
# 体质的命名和表现方式——这些都不是固定列表，AI应根据数值结果自行发挥。

import random
from .calc_utils import weighted_choice, clamp


# == 灵根随机抽取 §2.1 ==
def roll_spirit_root() -> dict:
    """灵根随机抽取+属性确认: 加权随机, 返回{name,element,affinity,counter:{克,被克}}"""
    FIVE_ELEMENTS = ["金", "木", "水", "火", "土"]
    VARIANT_ELEMENTS = ["风", "雷", "冰", "暗"]
    ELEMENT_COUNTER = {
        "金": ("克木", "被火克"),
        "木": ("克土", "被金克"),
        "土": ("克水", "被木克"),
        "水": ("克火", "被土克"),
        "火": ("克金", "被水克"),
    }

    roots = [
        ("伪灵根·五行", 15, {"修炼速度": 0.30, "突破难度": 1.6}),
        ("伪灵根·四属性", 20, {"修炼速度": 0.40, "突破难度": 1.4}),
        ("真灵根·三属性", 20, {"修炼速度": 0.55, "突破难度": 1.2}),
        ("真灵根·双属性", 18, {"修炼速度": 0.80, "突破难度": 1.0}),
        ("天灵根", 12, {"修炼速度": 1.60, "突破难度": 0.60}),
        ("变异灵根", 4, {"修炼速度": 1.35, "突破难度": 0.70}),
        ("隐灵根", 3, {"修炼速度": 0.90, "突破难度": 1.1}),
        ("混沌灵根", 0.5, {"修炼速度": 1.80, "突破难度": 0.50}),
    ]
    chosen = weighted_choice(roots)
    name = chosen[0]
    stats = chosen[2]

    if name == "伪灵根·五行":
        elements = FIVE_ELEMENTS.copy()
        affinity = {e: 1 for e in FIVE_ELEMENTS}
    elif name == "伪灵根·四属性":
        elements = random.sample(FIVE_ELEMENTS, 4)
        affinity = {e: 1 for e in elements}
    elif name == "真灵根·三属性":
        elements = random.sample(FIVE_ELEMENTS, 3)
        affinity = {e: 2 for e in elements}
    elif name == "真灵根·双属性":
        elements = random.sample(FIVE_ELEMENTS, 2)
        affinity = {e: 3 for e in elements}
    elif name == "天灵根":
        elements = [random.choice(FIVE_ELEMENTS)]
        affinity = {elements[0]: 8}
    elif name == "变异灵根":
        elements = [random.choice(VARIANT_ELEMENTS)]
        affinity = {elements[0]: 6}
    elif name == "隐灵根":
        main = random.choice(FIVE_ELEMENTS)
        elements = FIVE_ELEMENTS.copy()
        affinity = {e: 1 for e in FIVE_ELEMENTS}
        affinity[main] = 5
    else:  # 混沌灵根
        elements = FIVE_ELEMENTS.copy()
        affinity = {e: 5 for e in FIVE_ELEMENTS}

    counter = {}
    for e in elements:
        if e in ELEMENT_COUNTER:
            counter[e] = {"克": ELEMENT_COUNTER[e][0], "被克": ELEMENT_COUNTER[e][1]}

    display_name = f"{name}·{'+'.join(elements)}" if elements else name
    return {
        "name": display_name,
        "灵根类型": name,
        "灵根属性": elements,
        "五行亲和": affinity,
        "五行相克": counter,
        "stats": stats,
    }


# == 体质判定 §2.2 ==
def roll_physique(spirit_root_name: str, birthplace: str = "") -> dict:
    """体质触发判定 §2.2.1: 触发率=10%+灵根加成+出生地加成±5%, [1%,50%]"""
    base_chance = 0.10
    if "天灵根" in spirit_root_name:
        base_chance += 0.10
    elif "变异" in spirit_root_name:
        base_chance += 0.05
    elif "混沌" in spirit_root_name:
        base_chance += 0.15
    elif "隐灵根" in spirit_root_name:
        base_chance += 0.05
    elif "伪灵根" in spirit_root_name:
        base_chance -= 0.05

    birthplace_bonuses = {
        "绝境险地": 0.15,
        "古战场遗址旁": 0.10,
        "灵气浓郁之地": 0.08,
        "妖兽山脉边缘": 0.05,
        "边境战区": 0.05,
    }
    base_chance += birthplace_bonuses.get(birthplace, 0)

    base_chance += random.uniform(-0.05, 0.05)
    base_chance = clamp(base_chance, 0.01, 0.50)

    triggered = random.random() < base_chance
    return {"triggered": triggered, "chance": base_chance}


def generate_physique_detail() -> dict:
    """体质详情生成 §2.2.2-2.2.4: 四维度动态生成(name/source/effects/rarity/cost/awaken)"""
    # 维度1：来源类型
    sources = [
        (
            "先天遗传",
            0.30,
            {"name_prefix": ("先天", "玄", "天"), "suffix": ("之体", "之体", "之骨")},
        ),
        ("后天异变", 0.25, {"name_prefix": ("", "", ""), "suffix": ("身", "躯", "体")}),
        (
            "血脉觉醒",
            0.20,
            {"name_prefix": ("", "古", "灵"), "suffix": ("血脉", "血脉", "后裔")},
        ),
        (
            "灵魂特质",
            0.15,
            {"name_prefix": ("不灭", "七窍", ""), "suffix": ("魂", "心", "灵")},
        ),
        (
            "天地馈赠",
            0.08,
            {"name_prefix": ("天道", "道", "天"), "suffix": ("之体", "之体", "胎")},
        ),
        (
            "诅咒/异化",
            0.02,
            {"name_prefix": ("诅咒", "厄", "灾"), "suffix": ("之体", "之躯", "之身")},
        ),
    ]
    source = weighted_choice(sources)

    directions = [
        (
            "修炼向",
            0.25,
            {
                "speed_bonus": random.uniform(0.10, 0.50),
                "breakthrough_bonus": random.uniform(-0.20, 0.20),
                "qi_recovery": random.uniform(0.10, 0.30),
            },
        ),
        (
            "战斗向",
            0.25,
            {
                "atk_bonus": random.uniform(0.10, 0.40),
                "crit_bonus": random.uniform(0.05, 0.15),
                "element_dmg": random.uniform(0.20, 0.60),
            },
        ),
        (
            "防御向",
            0.15,
            {
                "def_bonus": random.uniform(0.10, 0.30),
                "hp_bonus": random.uniform(0.15, 0.50),
                "dmg_reduce": random.uniform(0.05, 0.20),
            },
        ),
        (
            "恢复向",
            0.12,
            {
                "heal_rate": random.uniform(0.20, 1.00),
                "status_recovery": random.uniform(0.30, 0.80),
            },
        ),
        (
            "感知向",
            0.10,
            {
                "sense_bonus": random.uniform(0.20, 0.60),
                "illusion_detect": random.uniform(0.20, 0.50),
                "detect_range": random.uniform(0.30, 1.00),
            },
        ),
        ("特殊向", 0.08, {"special": True}),
        ("代价向", 0.05, {"penalty": True}),
    ]

    num_dirs = 1 if random.random() < 0.6 else 2
    chosen_dirs = random.sample(directions, min(num_dirs, len(directions)))
    effects = [{"direction": d[0], "params": d[2]} for d in chosen_dirs]

    rarities = [
        ("常见", 0.50, 1.0),
        ("稀有", 0.30, 1.3),
        ("史诗", 0.15, 1.6),
        ("传说", 0.04, 2.0),
        ("神话", 0.01, 2.5),
    ]
    rarity = weighted_choice(rarities)
    rarity_name = rarity[0]
    rarity_mult = rarity[2]

    cost = None
    total_strength = rarity_mult * (1.0 + len(chosen_dirs) * 0.3)
    if total_strength > 1.5 and random.random() < 0.70:
        costs = [
            {"type": "cultivation_penalty", "effect": "某属性功法速度降低"},
            {"type": "lifespan_penalty", "effect": "寿元上限减少"},
            {"type": "breakthrough_penalty", "effect": "突破难度增加"},
            {"type": "tribulation_risk", "effect": "天劫概率提升"},
            {"type": "beast_hostility", "effect": "某类妖兽仇恨增加"},
            {"type": "resource_dependency", "effect": "需定期消耗特定资源"},
            {"type": "emotional_instability", "effect": "心境易波动"},
        ]
        cost = random.choice(costs)

    dir_keywords = {
        "修炼向": ("灵", "道", "玄"),
        "战斗向": ("剑", "战", "斗"),
        "防御向": ("钢", "金", "山"),
        "恢复向": ("春", "命", "生"),
        "感知向": ("灵", "神", "魂"),
        "特殊向": ("异", "奇", "古"),
        "代价向": ("厄", "咒", "噬"),
    }

    prefix_pool = source[2]["name_prefix"]
    suffix_pool = source[2]["suffix"]
    keyword_pool = [kw for d in chosen_dirs for kw in dir_keywords.get(d[0], ("玄",))]

    prefix = random.choice(prefix_pool) if prefix_pool else ""
    keyword = random.choice(keyword_pool) if keyword_pool else "玄"
    suffix = random.choice(suffix_pool) if suffix_pool else "之体"
    name = f"{prefix}{keyword}{suffix}" if prefix else f"{keyword}{suffix}"

    awaken_conditions = [
        "筑基期觉醒",
        "经历生死危机后觉醒",
        "接触特定环境觉醒",
        "服用特定丹药觉醒",
        "十八岁自动觉醒",
    ]
    awaken = {
        "awakened": False,
        "awaken_condition": random.choice(awaken_conditions),
        "initial_effect": 0.3 + random.random() * 0.2,
    }

    return {
        "name": name,
        "source": source[0],
        "effects": effects,
        "rarity": rarity_name,
        "rarity_mult": rarity_mult,
        "cost": cost,
        "awaken": awaken,
    }


# == 基础属性 §2.4 ==
def roll_stats() -> dict:
    """基础属性随机"""
    return {
        "气血": 50,
        "灵气": 20,
        "攻击": 8,
        "防御": 5,
        "速度": 5,
        "神识": 6,
        "悟性": random.randint(40, 70),
        "机缘": random.randint(30, 70),
        "体魄": random.randint(40, 70),
        "心境": 60,
        "寿元": 80,
        "业力": 0,
        "气运": random.randint(20, 80),
    }


# == 出身 §2.5 ==
def roll_origin() -> dict:
    """出身随机生成: 家族背景+出生地+特殊事件三重判定

    本函数仅返回**类型标记 + 纯数值效果**，不含任何固定叙事文本。
    AI 应围绕这些种子自由创造：家族成员的具体故事、出生地的详细地貌、
    特殊事件的起因经过——只需保留本函数返回的数值效果即可（如体魄+10、财富+50）。
    相关的结构化叙事参考参数见 calc_world.py 的 _FAMILY_PARAMS / _AREA_PARAMS / _EVENT_PARAMS。

    返回结构:
      - family:        { type, effects }         → 家族类型 + 纯数值效果
      - birthplace:    { type, effects }         → 出生地类型 + 纯数值效果
      - special_event: { type, effects } | None  → 特殊事件 + 纯数值效果(30%概率触发)
      - 家族背景 / 出生地 / 特殊事件: 向后兼容的顶层 key
    """
    # ── 家族背景（共23种）──
    families = [
        # 凡人底层（高概率）
        ("孤儿/弃婴", 12, {"财富": 0, "知识": 0, "人脉": 0}),
        ("贫苦农家", 16, {"财富": 0, "知识": 0, "人脉": 1, "体魄加成": 5}),
        ("渔/樵民家", 8, {"财富": 0, "知识": 1, "人脉": 1, "地形适应": "水域/山地+10%"}),
        ("逃难流民", 6, {"财富": 0, "知识": 1, "人脉": 0, "体魄加成": 5, "神识加成": 3, "速度加成": 5}),
        # 凡人·一技之长
        ("猎户之家", 10, {"财富": 1, "知识": 1, "人脉": 1, "体魄加成": 10, "气血加成": 10, "物品": "短刀"}),
        ("铁匠之家", 5, {"财富": 10, "知识": 1, "人脉": 1, "体魄加成": 8, "锻造初始": 1, "物品": "铁锤"}),
        ("镖师之家", 5, {"财富": 15, "知识": 1, "人脉": 2, "atk加成": 3, "体魄加成": 8, "速度加成": 3}),
        ("戏班/卖艺人", 3, {"财富": 5, "知识": 1, "人脉": 2, "速度加成": 10, "伪装/易容": True}),
        ("马帮护卫", 4, {"财富": 10, "知识": 2, "人脉": 2, "体魄加成": 5, "地形适应": "商道/野外+5%"}),
        ("守墓人之后", 2, {"财富": 5, "知识": 2, "人脉": 0, "阴气抗性": 0.15, "通灵感知": True}),
        ("盗墓者之家", 2, {"财富": 20, "知识": 3, "人脉": 0, "机关/禁制知识": True, "业力初始": 3}),
        # 凡人中产
        ("商贾之家", 8, {"财富": 50, "知识": 2, "人脉": 1, "交易加成": 0.05}),
        ("书香门第", 6, {"财富": 20, "知识": 3, "人脉": 1, "悟性加成": 5}),
        ("没落贵族", 5, {"财富": 30, "知识": 3, "人脉": 1, "物品": "祖传物品"}),
        ("武林世家", 4, {"财富": 20, "知识": 1, "人脉": 1, "atk加成": 5, "体魄加成": 10, "物品": "凡器武器"}),
        ("江湖郎中/药师", 4, {"财富": 10, "知识": 3, "人脉": 1, "炼丹初始": 1}),
        ("灵植夫之家", 4, {"财富": 15, "知识": 2, "人脉": 1, "灵植初始": 1, "灵草辨识": True}),
        # 修仙相关
        ("修仙小族(旁支)", 4, {"财富": 50, "知识": 3, "人脉": 2, "初始修为": "炼气一层", "物品": "黄阶功法"}),
        ("修仙大族(嫡系)", 2, {"财富": 200, "知识": 4, "人脉": 4, "初始修为": "炼气二层", "物品": "黄阶功法"}),
        ("修仙大族(庶出)", 2, {"财富": 30, "知识": 2, "人脉": 0, "初始修为": "炼气一层"}),
        # 特殊/稀有
        ("被捡养/收养", 1, {"财富": 0, "知识": 0, "人脉": 1}),
        ("山中隐士之后", 2, {"财富": 5, "知识": 4, "人脉": 0, "悟性加成": 5, "心境加成": 10, "野外生存": True}),
        ("炼尸/赶尸世家", 1, {"财富": 15, "知识": 2, "人脉": 0, "阴气抗性": 0.20, "驭鬼初始": 1, "业力初始": 5}),
    ]
    chosen_family = weighted_choice(families, weight_key=1)
    family_type = chosen_family[0]
    family_effects = dict(chosen_family[2])

    # ── 出生地（共19种）──
    birthplaces = [
        # 凡人聚居
        ("偏远山村", 0.20, {}),
        ("凡人城镇", 0.15, {}),
        ("湖畔渔村", 0.06, {"水域亲和": True, "水性加成": 5}),
        ("古道驿站", 0.05, {"信息灵通": True, "人脉加成": 1}),
        # 修仙势力周边
        ("修仙坊市附近", 0.10, {}),
        ("宗门属地村落", 0.10, {"每5年宗门收徒": True}),
        ("灵矿矿区", 0.04, {"采矿知识": True, "残余灵石概率": True}),
        ("废弃宗门遗址", 0.03, {"残缺传承": True, "禁制风险": True}),
        # 极端环境
        ("妖兽山脉边缘", 0.04, {"灵草概率": True, "妖兽威胁": True}),
        ("边境战区", 0.04, {"死亡风险": "高", "遗落物品": True}),
        ("古战场遗址旁", 0.03, {"残缺法器": True, "阴气侵蚀": True}),
        ("灵气枯竭之地", 0.04, {"修炼速度": -0.20, "心境": 10}),
        ("灵气浓郁之地", 0.03, {"修炼速度": 0.20, "觊觎风险": True}),
        ("绝境险地", 0.02, {"体魄": 15, "随机抗性": 0.20}),
        ("沼泽毒瘴区", 0.03, {"毒抗": 0.10, "灵草概率": True, "瘴气威胁": True}),
        ("地下溶洞群", 0.02, {"暗视": True, "矿石概率": True, "迷路风险": True}),
        ("大漠绿洲", 0.03, {"耐热": True, "水源敏感": True, "商队往来": True}),
        ("海外孤岛", 0.02, {"水域亲和": True, "稀有海产": True, "与世隔绝": True}),
        # 漂泊
        ("流浪/无定所", 0.03, {"神识": 5, "速度": 3}),
    ]
    chosen_birth = weighted_choice(birthplaces, weight_key=1)
    birthplace_type = chosen_birth[0]
    birthplace_effects = dict(chosen_birth[2])

    # ── 特殊事件（30%概率触发，共26种）──
    special_event = None
    if random.random() < 0.30:
        specials = [
            # 天地异象/命运
            ("出生时天降异象", {"气运加成": 20}),
            ("血脉返祖觉醒", {"全属性加成": 5, "妖兽亲和": 0.30}),
            ("月圆之夜异变", {"月圆战力加成": 0.15, "体质异常": True}),
            # 遗弃/身世
            ("襁褓中放于宗门门口", {"物品": "信物/玉佩"}),
            ("被误认为他人之子", {"身世谜团": True, "养父母隐藏": True}),
            # 死里逃生
            ("幼年大病不死", {"毒抗": 0.10, "寿元修正": -5}),
            ("被魔物附身失败", {"神识加成": 8, "魔抗": 0.15, "残留意念": True}),
            ("坠崖得机缘", {"体魄加成": 5, "物品": "山洞遗物", "伤疤": True}),
            # 高人/机缘
            ("被路过高人点拨", {"悟性加成": 10, "心境加成": 5}),
            ("梦中得仙师指点", {"悟性加成": 8, "残缺功法": True, "梦境线索": True}),
            ("救下受伤修士", {"人脉加成": 2, "物品": "修士谢礼", "恩情": True}),
            ("偷听到修士密谈", {"情报": True, "悟性加成": 3, "风险": "被察觉"}),
            # 获得物品
            ("捡到残破玉简", {"物品": "残缺功法/法术"}),
            ("天降灵物", {"物品": "灵物/灵种"}),
            ("捡到残缺藏宝图", {"物品": "藏宝图残片", "线索": True}),
            ("河水冲来宝物", {"物品": "漂流之物", "随机": True}),
            ("挖出前人遗骸/遗物", {"物品": "前人遗物", "业力修正": -2}),
            # 奇异经历
            ("误食灵果/灵草", {"随机属性加成": 5, "体质微变": True}),
            ("被灵兽认主", {"妖兽亲和": 0.40, "灵兽伙伴": True}),
            ("天生亲近某种灵气", {"随机属性亲和": 5, "对应功法加成": 0.10}),
            ("天生阴阳眼", {"神识加成": 15}),
            ("被妖兽抚养长大", {"体魄加成": 20, "妖兽亲和": 0.50}),
            # 灾祸
            ("家族被灭门", {"财富": 100, "心境修正": -20, "业力初始": 5}),
            ("被当成炉鼎培养", {"灵气加成": 0.30, "寿元修正": -20}),
            ("被邪修标记", {"诅咒": True, "追踪风险": True, "灵力异常": True}),
            ("家乡遭天灾灭村", {"心境修正": -15}),
            # 引路
            ("被修士渡入仙途", {"初始修为": "炼气一层"}),
            ("目睹仙人斗法", {"悟性加成": 5}),
            ("出生在古墓/遗迹中", {"物品": "古物", "诅咒": True}),
        ]
        chosen_special = random.choice(specials)
        special_event = {
            "type": chosen_special[0],
            "effects": dict(chosen_special[1]),
        }

    return {
        # 新结构化字段（推荐使用）
        "family": {"type": family_type, "effects": family_effects},
        "birthplace": {"type": birthplace_type, "effects": birthplace_effects},
        "special_event": special_event,
        # 向后兼容的顶层 key
        "家族背景": family_type,
        "出生地": birthplace_type,
        "特殊事件": (special_event["type"], special_event["effects"]) if special_event else None,
    }
