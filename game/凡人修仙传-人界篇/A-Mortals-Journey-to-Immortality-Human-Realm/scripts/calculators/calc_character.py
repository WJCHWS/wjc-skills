# 凡人修仙传-人界篇 · 概率计算引擎 · 角色创建 §2

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
    """出身随机生成: 家族背景+出生地+特殊事件三重判定"""
    families = [
        (
            "孤儿/弃婴",
            15,
            {"财富": 0, "知识": 0, "人脉": 0, "描述": "你是孤儿出身，无父无母，来历成谜。"},
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
