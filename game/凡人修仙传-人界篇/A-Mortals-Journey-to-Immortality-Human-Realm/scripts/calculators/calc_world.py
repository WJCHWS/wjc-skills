# 凡人修仙传-人界篇 · 概率计算引擎 · 世界/家族介绍
# 仅返回类型标记，叙事由AI生成


def generate_world_intro(
    family_name: str = "", birthplace: str = "", special_event=None
) -> dict:
    """仅返回类型标记，所有叙事内容、人物关系、环境描写、姓氏等均由AI根据类型标记动态生成"""

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
