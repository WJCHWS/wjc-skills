# 凡人修仙传-人界篇 · 概率计算引擎 v1.1 — 组件化架构
# 按游戏领域拆分为独立模块: 工具/战斗/角色/修炼/生产/灵兽/世界

import random
import sys
import json

# 随机种子（在导入子模块前初始化）
random.seed()

# == 聚合所有子模块，保持向后兼容 ==
from calculators import (                                                                  # noqa: E402,F401
    clamp, weighted_choice,
    calc_hit, calc_dodge, calc_crit,
    calc_physical_damage, calc_magical_damage, calc_crit_damage,
    calc_flee, calc_element_multiplier, calc_battle_scene_modifier, calc_status_application,
    roll_spirit_root, roll_physique, generate_physique_detail, roll_stats, roll_origin,
    calc_breakthrough, calc_breakthrough_failure,
    calc_tribulation_trigger, calc_tribulation_type, calc_tribulation_damage,
    calc_karma_event, calc_luck_modifier,
    calc_mind_change, calc_mind_effect, calc_heart_demon, calc_heart_demon_resist,
    calc_possess,
    calc_probe_deception, calc_encounter, calc_possess_resist, calc_escape_discovery,
    calc_alchemy, calc_alchemy_success_rate,
    calc_forging, calc_talisman,
    calc_formation, calc_formation_break,
    calc_beast_taming, calc_beast_loyalty, calc_beast_betray,
    generate_world_intro,
)

# ============================================================
# CLI 入口（保持不变）
# ============================================================

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
