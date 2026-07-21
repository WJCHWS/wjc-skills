# 凡人修仙传-人界篇 · 概率计算引擎 v1.0 — 战斗/突破/炼丹/炼器/制符/阵法/天劫/机缘/体质等判定

import random
import sys
import json

# 随机种子
random.seed()

# == 工具函数 ==


def clamp(value, lo, hi):
    # clamp: 限制值在[lo,hi]范围内
    return max(lo, min(hi, value))


def weighted_choice(items, weight_key=1):
    # 加权随机选择: items=[(name,weight,...),...], weight_key=权重索引(默认1)
    total = sum(item[weight_key] for item in items)
    r = random.random() * total
    cum = 0
    for item in items:
        cum += item[weight_key]
        if r < cum:
            return item
    return items[-1]


# == 战斗 §4 ==


def calc_hit(atk_spd: int, def_spd: int) -> bool:
    # 命中判定 §4.2: hit=75%+(atk_spd-def_spd)*3%, [5%,99%]
    hit_rate = 0.75 + (atk_spd - def_spd) * 0.03
    hit_rate = clamp(hit_rate, 0.05, 0.99)
    return random.random() < hit_rate


def calc_dodge(atk_spd: int, def_spd: int) -> bool:
    # 闪避判定 §4.2: dodge=max(0,(def_spd-atk_spd)*2%)
    dodge_rate = max(0, (def_spd - atk_spd) * 0.02)
    return random.random() < dodge_rate


def calc_crit(luck: int) -> bool:
    # 暴击判定 §4.2: crit=5%+luck*0.05%
    crit_rate = 0.05 + luck * 0.0005
    return random.random() < crit_rate


def calc_physical_damage(atk: int, defense: int) -> int:
    # 物理伤害 §4.2: dmg=max(1,ATK-DEF+随机(-1~3))
    return max(1, atk - defense + random.randint(-1, 3))


def calc_magical_damage(base_dmg: int, atk: int, defense: int) -> int:
    # 法术伤害 §4.2: dmg=max(1,base+ATK*0.5-DEF*0.5+随机(-1~3))
    return max(
        1, base_dmg + int(atk * 0.5) - int(defense * 0.5) + random.randint(-1, 3)
    )


def calc_crit_damage(base_damage: int) -> int:
    # 暴击伤害 §4.2: crit_dmg=base*(1.5~3.0)
    multiplier = 1.5 + random.random() * 1.5
    return int(base_damage * multiplier)


def calc_flee(atk_spd: int, def_spd: int, realm_gap: int = 0) -> bool:
    # 逃跑判定 §21: rate=20%+spd_diff*5%-realm_gap*30%, [1%,90%]
    rate = 0.20 + (atk_spd - def_spd) * 0.05 - realm_gap * 0.30
    rate = clamp(rate, 0.01, 0.90)
    return random.random() < rate


def calc_element_multiplier(atk_element: str, def_element: str) -> float:
    # 五行相克 §4.3: 金克木/木克土/土克水/水克火/火克金, 克*1.5/被克*0.7/同*1.0
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


def calc_battle_scene_modifier(scene: str, element: str) -> float:
    # 战斗场景加成 §4.5
    modifiers = {
        "山地": {"土": 0.20},
        "水域": {"水": 0.20, "火": -0.20},
        "森林": {"木": 0.20},
        "火山": {"火": 0.30},
        "雪地": {"水": 0.20, "火": -0.30},
        "夜间": {"暗": 0.20},
    }
    return modifiers.get(scene, {}).get(element, 0.0)


def calc_status_application(status_name: str, status_level: int = 1) -> dict:
    # 特殊状态效果 §4.4: 返回每回合效果
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


# == 角色创建 §2 ==


def roll_spirit_root() -> dict:
    # 灵根随机抽取+属性确认 §2.1: 加权随机, 返回{name,element,affinity,counter:{克,被克}}
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
        ("真灵根·单属性", 12, {"修炼速度": 1.10, "突破难度": 0.85}),
        ("天灵根", 3, {"修炼速度": 1.60, "突破难度": 0.60}),
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
    elif name == "真灵根·单属性":
        elements = [random.choice(FIVE_ELEMENTS)]
        affinity = {elements[0]: 5}
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
        affinity[main] = 5  # 激活后主属性+5
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


def roll_physique(spirit_root_name: str, birthplace: str = "") -> dict:
    # 体质触发判定 §2.2.1: 触发率=10%+灵根加成+出生地加成±5%, [1%,50%]
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
    # 体质详情生成 §2.2.2-2.2.4: 四维度动态生成(name/source/effects/rarity/cost/awaken)
    # 维度1：来源类型 (2.2.2)
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
        ("特殊向", 0.08, {"special": "免疫特定状态或死后复活或吞噬恢复或某类生物亲和"}),
        ("代价向", 0.05, {"penalty": True}),
    ]

    num_dirs = 1 if random.random() < 0.6 else 2
    chosen_dirs = random.sample(directions, min(num_dirs, len(directions)))
    effects = [{"direction": d[0], "params": d[2]} for d in chosen_dirs]

    rarities = [
        ("常见", 0.50, 1.0, "你感觉自己的XX比常人稍强"),
        ("稀有", 0.30, 1.3, "你发现自己拥有罕见的XX之体"),
        ("史诗", 0.15, 1.6, "你的体质万里挑一，名为XX"),
        ("传说", 0.04, 2.0, "古籍中记载的XX之体，竟在你身上重现"),
        ("神话", 0.01, 2.5, "天道震颤，你的体质已超越此方天地认知"),
    ]
    rarity = weighted_choice(rarities)
    rarity_name = rarity[0]
    rarity_mult = rarity[2]

    cost = None
    total_strength = rarity_mult * (1.0 + len(chosen_dirs) * 0.3)
    if total_strength > 1.5 and random.random() < 0.70:
        costs = [
            "某属性功法速度-20~50%",
            "寿元上限-10~50年",
            "突破某境界难度+20~50%",
            "天劫概率+30%",
            "某类妖兽仇恨+50%",
            "需定期消耗特定资源",
            "情绪波动大，心境易下降",
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


def roll_stats() -> dict:
    # 基础属性随机 §2.4
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


def roll_origin() -> dict:
    # 出身随机生成 §2.5: 家族背景+出生地+特殊事件三重判定
    families = [
        (
            "孤儿/弃婴",
            15,
            {
                "财富": 0,
                "知识": 0,
                "人脉": 0,
                "描述": "你是孤儿出身，无父无母，来历成谜。",
            },
        ),
        (
            "贫苦农家",
            20,
            {
                "财富": 0,
                "知识": 0,
                "人脉": 1,
                "体魄加成": 5,
                "描述": "你出生在贫苦农家，从小劳作，练就一副结实身板。",
            },
        ),
        (
            "猎户之家",
            12,
            {
                "财富": 1,
                "知识": 1,
                "人脉": 1,
                "体魄加成": 10,
                "气血加成": 10,
                "物品": "短刀",
                "描述": "猎户家长大的你，跟父亲学过狩猎和草药辨识。",
            },
        ),
        (
            "渔/樵民家",
            10,
            {
                "财富": 0,
                "知识": 1,
                "人脉": 1,
                "地形适应": "水域/山地+10%",
                "描述": "渔樵为生的家庭让你熟悉山水之道。",
            },
        ),
        (
            "商贾之家",
            10,
            {
                "财富": 50,
                "知识": 2,
                "人脉": 1,
                "交易加成": 0.05,
                "描述": "商贾之家让你耳濡目染，懂得些买卖之道。",
            },
        ),
        (
            "书香门第",
            8,
            {
                "财富": 20,
                "知识": 3,
                "人脉": 1,
                "悟性加成": 5,
                "描述": "书香世家熏陶出你的聪慧，识字读书不在话下。",
            },
        ),
        (
            "没落贵族",
            6,
            {
                "财富": 30,
                "知识": 3,
                "人脉": 1,
                "物品": "祖传物品",
                "描述": "曾经的贵族已没落，但家中尚有几分底蕴。",
            },
        ),
        (
            "武林世家",
            5,
            {
                "财富": 20,
                "知识": 1,
                "人脉": 1,
                "atk加成": 5,
                "体魄加成": 10,
                "物品": "凡器武器",
                "描述": "武林世家出身的你有一身好武艺。",
            },
        ),
        (
            "江湖郎中/药师",
            4,
            {
                "财富": 10,
                "知识": 3,
                "人脉": 1,
                "炼丹初始": 1,
                "描述": "跟着师父行医问药，你认得不少草药。",
            },
        ),
        (
            "修仙小族(旁支)",
            5,
            {
                "财富": 50,
                "知识": 3,
                "人脉": 2,
                "初始修为": "炼气一层",
                "物品": "基础功法",
                "描述": "修仙小族的旁支子弟，比凡人多了几分见识。",
            },
        ),
        (
            "修仙大族(嫡系)",
            2,
            {
                "财富": 200,
                "知识": 4,
                "人脉": 4,
                "初始修为": "炼气二层",
                "物品": "黄阶功法",
                "描述": "修仙大族嫡系子弟，资源丰厚但家族内斗激烈。",
            },
        ),
        (
            "修仙大族(庶出)",
            2,
            {
                "财富": 30,
                "知识": 2,
                "人脉": 0,
                "初始修为": "炼气一层",
                "描述": "庶出身份让你在修仙大族中步步艰辛。",
            },
        ),
        (
            "被捡养/收养",
            1,
            {
                "财富": 0,
                "知识": 0,
                "人脉": 1,
                "描述": "你被好心人捡回收养，养父母身份莫测。",
            },
        ),
    ]
    chosen_family = weighted_choice(families, weight_key=1)
    result = {"家族背景": chosen_family[0]}
    result.update(chosen_family[2])

    birthplaces = [
        ("偏远山村", 0.25, {"环境特征": "宁静，灵气稀薄", "效果": {}}),
        ("凡人城镇", 0.20, {"环境特征": "人口密集，市井百态", "效果": {}}),
        ("修仙坊市附近", 0.12, {"环境特征": "修士往来频繁", "效果": {}}),
        (
            "宗门属地村落",
            0.15,
            {"环境特征": "受宗门庇护", "效果": {"每5年宗门收徒": True}},
        ),
        (
            "边境战区",
            0.05,
            {"环境特征": "常年战乱", "效果": {"死亡风险": "高", "遗落物品": True}},
        ),
        (
            "妖兽山脉边缘",
            0.05,
            {
                "环境特征": "危险与机遇并存",
                "效果": {"灵草概率": True, "妖兽威胁": True},
            },
        ),
        (
            "古战场遗址旁",
            0.03,
            {"环境特征": "怨气弥漫", "效果": {"残缺法器": True, "阴气侵蚀": True}},
        ),
        (
            "灵气枯竭之地",
            0.05,
            {"环境特征": "修炼困难", "效果": {"修炼速度": -0.20, "心境": 10}},
        ),
        (
            "灵气浓郁之地",
            0.04,
            {"环境特征": "得天独厚", "效果": {"修炼速度": 0.20, "觊觎风险": True}},
        ),
        (
            "绝境险地",
            0.03,
            {"环境特征": "极端环境", "效果": {"体魄": 15, "随机抗性": 0.20}},
        ),
        ("流浪/无定所", 0.03, {"环境特征": "居无定所", "效果": {"神识": 5, "速度": 3}}),
    ]
    chosen_birth = weighted_choice(birthplaces, weight_key=1)
    result["出生地"] = chosen_birth[0]
    result["出生地特征"] = chosen_birth[2]["环境特征"]

    if random.random() < 0.30:
        specials = [
            (
                "出生时天降异象",
                {
                    "气运加成": 20,
                    "描述": "你出生时天降异象，气运加身，但也被某势力暗中关注。",
                },
            ),
            (
                "襁褓中放于宗门门口",
                {
                    "物品": "信物/玉佩",
                    "描述": "你被人放在修仙宗门门口，身边一块信物指向未知身世。",
                },
            ),
            (
                "幼年大病不死",
                {
                    "毒抗": 0.10,
                    "寿元修正": -5,
                    "描述": "幼年一场大病差点要了你的命，但挺过来了，毒抗有所提升。",
                },
            ),
            (
                "被路过高人点拨",
                {
                    "悟性加成": 10,
                    "心境加成": 5,
                    "描述": "一位路过的修士随口点拨了你一句，令你茅塞顿开。",
                },
            ),
            (
                "捡到残破玉简",
                {
                    "物品": "残缺功法/法术",
                    "描述": "你偶然捡到一枚残破玉简，内含一门残缺的修炼之法。",
                },
            ),
            (
                "家族被灭门",
                {
                    "财富": 100,
                    "心境修正": -20,
                    "业力初始": 5,
                    "描述": "你的家族被仇家灭门，你带着遗产独自逃生，心中埋下仇恨。",
                },
            ),
            (
                "被当成炉鼎培养",
                {
                    "灵气加成": 0.30,
                    "寿元修正": -20,
                    "描述": "你从小被当成炉鼎培养，灵气基础扎实但折损了寿元。",
                },
            ),
            (
                "出生在古墓/遗迹中",
                {
                    "物品": "古物",
                    "诅咒": True,
                    "描述": "你在古墓中出生，身边放着一件神秘古物，但似乎也招来了某种诅咒。",
                },
            ),
            (
                "天生阴阳眼",
                {
                    "神识加成": 15,
                    "描述": "你天生阴阳眼，能看见常人看不到的灵体鬼魂，但也容易招惹脏东西。",
                },
            ),
            (
                "被妖兽养大",
                {
                    "体魄加成": 20,
                    "妖兽亲和": 0.50,
                    "描述": "你从小被妖兽养大，野性未脱，体魄强健但不懂人类礼法。",
                },
            ),
        ]
        result["特殊事件"] = random.choice(specials)

    return result


# == 突破 §2.3 ==


def calc_breakthrough(base_rate: float, difficulty: float, bonuses: dict) -> tuple:
    # 突破判定 §2.3: rate=base*(1/diff)*Πbonus, [1%,99%], returns(success,rate)
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
    # 突破失败后果 §2.3: 轻伤40%/重伤25%/修为尽失20%/走火入魔10%/死亡5%
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
    # 炼丹结果 §5.3-5.4: base=10%+lv*4%+wu_xing*0.15%+phys, +herb/furnace/fire/year/aux, [1%,95%]
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
    # 炼丹成功率明细 §5.3: 返回各步骤加成明细
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
    # 炼器结果 §6.3-6.4: base=15%+lv*3%+wu_xing*0.1%+phys, +material+fire
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
    # 制符判定 §8.3: rate=10%+lv*3%+wu_xing*0.1%
    rate = 0.10 + level * 0.03 + wu_xing * 0.001
    rate = clamp(rate, 0.01, 0.95)
    return random.random() < rate


# == 阵法 §7 ==


def calc_formation(formation_level: int, wu_xing: int) -> bool:
    # 布阵判定 §21: rate=20%+lv*5%+wu_xing*0.2%
    rate = 0.20 + formation_level * 0.05 + wu_xing * 0.002
    rate = clamp(rate, 0.01, 0.99)
    return random.random() < rate


def calc_formation_break(sense: int, formation_tier: int, force: bool = False) -> bool:
    # 破阵判定 §7.3: 神识探测或强行攻破
    if force:
        rate = max(0.05, 0.50 - formation_tier * 0.05)
    else:
        rate = 0.20 + sense * 0.01 - formation_tier * 0.03
    rate = clamp(rate, 0.01, 0.90)
    return random.random() < rate


# == 灵兽 §9 ==


def calc_beast_taming(player_sense: int, beast_sense: int) -> bool:
    # 灵兽契约判定 §9.1/§21: rate=30%+sense_diff*2%
    rate = 0.30 + (player_sense - beast_sense) * 0.02
    rate = clamp(rate, 0.01, 0.95)
    return random.random() < rate


def calc_beast_loyalty(base_loyalty: int = 60) -> int:
    # 灵兽初始忠诚度 §9.4: 随机60-100
    return random.randint(base_loyalty, 100)


def calc_beast_betray(loyalty: int) -> bool:
    # 灵兽叛逃判定 §9.4: 忠诚<30时可能叛逃
    if loyalty >= 30:
        return False
    rate = (30 - loyalty) * 0.05
    return random.random() < rate


# == 天劫 §12 ==


def calc_tribulation_trigger() -> bool:
    # 天劫触发 §12.1/§21: 大境界突破时30%概率触发
    return random.random() < 0.30


def calc_tribulation_type(karma: int = 0, fire_affinity: float = 0.0) -> str:
    # 天劫类型判定 §12.2
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
    # 天劫威力 §12: realm_tier境界等级(炼气1~化神5)
    base_dmg = realm_tier * 50
    multipliers = {"雷劫": 1.0, "火劫": 1.3, "心魔劫": 0.8, "双重劫": 1.8}
    return int(base_dmg * multipliers.get(tribulation_type, 1.0))


# == 因果/业力/气运 §13 ==


def calc_karma_event(karma: int) -> str:
    # 业力触发事件 §13.1: |karma|>50触发
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


def calc_luck_modifier(luck: int) -> float:
    # 气运修正 §13.2: luck≤0时-10%
    if luck <= 0:
        return -0.10
    return 0.0


# == 心魔/心境 §15 ==


def calc_mind_change(event_type: str) -> int:
    # 心境变化 §15.1: 返回变化值
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
    # 心境等级效果 §15.2
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
    # 心魔入侵判定 §15.3/§21: base=8%(<40→15%,<20→30%), +负业力加成
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
    # 心魔抵抗判定 §15.3: rate=sense*1%+mind*0.5%
    rate = sense * 0.01 + mind * 0.005
    rate = clamp(rate, 0.05, 0.90)
    return random.random() < rate


# == 夺舍 §18 ==


def calc_possess(
    attacker_sense: int, target_sense: int, target_has_protection: bool = False
) -> tuple:
    # 夺舍判定 §18.1: rate=sense_diff*2%, 护魂减半, [1%,80%]
    rate = (attacker_sense - target_sense) * 0.02
    if target_has_protection:
        rate *= 0.5
    rate = clamp(rate, 0.01, 0.80)
    return (random.random() < rate, rate)


# == 常用判定速查 §21 ==


def calc_probe_deception(sense: int, wu_xing: int) -> bool:
    # 识破骗局 §21: rate=30%+sense*0.5%+wu_xing*0.3%
    rate = 0.30 + sense * 0.005 + wu_xing * 0.003
    return random.random() < rate


def calc_encounter(luck: int) -> bool:
    # 遇到机缘 §21: rate=5%+luck*0.1%
    rate = 0.05 + luck * 0.001
    return random.random() < rate


def calc_possess_resist(sense: int, has_protection: bool = False) -> bool:
    # 被夺舍抵抗 §21: rate=sense*1%+保护加成
    rate = sense * 0.01
    if has_protection:
        rate += 0.30
    rate = clamp(rate, 0.05, 0.95)
    return random.random() < rate


def calc_escape_discovery(stealth_level: int, detector_sense: int) -> bool:
    # 隐匿/被发现判定(通用)
    rate = 0.30 + stealth_level * 0.05 - detector_sense * 0.005
    rate = clamp(rate, 0.05, 0.95)
    return random.random() < rate


# == 世界/家族介绍（仅机械参数，叙事由AI生成） ==


def generate_world_intro(
    family_name: str = "", birthplace: str = "", special_event=None
) -> dict:
    # 仅返回类型标记，所有叙事内容、人物关系、环境描写、姓氏等
    # 均由AI根据类型标记动态生成

    evt_name = ""
    if special_event:
        if isinstance(special_event, str):
            evt_name = special_event
        elif isinstance(special_event, (tuple, list)):
            evt_name = str(special_event[0]) if special_event else ""
        elif isinstance(special_event, dict):
            evt_name = special_event.get("name", "") or special_event.get("0", "")

    return {
        "family_type": family_name,
        "birthplace_type": birthplace,
        "special_event_name": evt_name,
    }


# == CLI 入口 ==

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python calc.py <函数名> [参数...]")
        print("可用函数:")
        funcs = [
            name for name in dir() if name.startswith(("calc_", "roll_", "generate_"))
        ]
        for f in sorted(funcs):
            print(f"  {f}")
        sys.exit(1)

    func_name = sys.argv[1]
    raw_args = sys.argv[2:]

    merged = []
    i = 0
    while i < len(raw_args):
        c = raw_args[i]
        if c.startswith(("{", "[")):
            joined = c
            j = i + 1
            while j < len(raw_args):
                joined += raw_args[j]
                j += 1
                try:
                    json.loads(joined)
                    c = joined
                    i = j - 1
                    break
                except json.JSONDecodeError:
                    continue
        merged.append(c)
        i += 1

    args = []
    for a in merged:
        if a.startswith(("{", "[")) or a in ("true", "false", "null"):
            try:
                args.append(json.loads(a))
            except json.JSONDecodeError:
                args.append(a)
        else:
            try:
                args.append(int(a))
            except ValueError:
                try:
                    args.append(float(a))
                except ValueError:
                    args.append(a)

    if func_name in globals() and callable(globals()[func_name]):
        result = globals()[func_name](*args)
        if isinstance(result, bool):
            print(json.dumps({"result": result, "success": result}))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"错误: 未找到函数 '{func_name}'")
        sys.exit(1)
