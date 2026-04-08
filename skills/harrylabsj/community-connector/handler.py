"""
Community Connector handler - 社区互助连接器
将用户描述的社区/位置/场景信息，转化为具体可验证的连接方案。
"""
import json
import re
from typing import Optional


NEED_TYPES = {
    "邻里互助": {
        "keywords": ["谁有", "借用", "求助", "帮忙", "邻居", "急需", "急找", "急用"],
        "channels": ["业主群", "楼栋群", "楼道告示", "物业"],
        "urgency": "high"
    },
    "社区服务": {
        "keywords": ["物业", "居委会", "社区", "街道"],
        "channels": ["物业电话", "居委会", "街道办"],
        "urgency": "medium"
    },
    "商业服务": {
        "keywords": ["推荐", "哪家", "靠谱", "宠物医院", "诊所", "快递", "维修"],
        "channels": ["大众点评", "美团", "业主口碑推荐"],
        "urgency": "low"
    },
    "社交连接": {
        "keywords": ["拼", "一起", "组队", "找伴", "活动"],
        "channels": ["业主群活动版", "社区活动中心", "豆瓣小组"],
        "urgency": "low"
    }
}


def parse_location(text: str) -> dict:
    """从用户描述中解析位置信息"""
    result = {
        "communityName": None,
        "district": None,
        "city": None,
        "building": None,
        "unit": None,
        "rawMatched": []
    }

    # 匹配小区名（常见后缀）
    patterns = [
        (r'([\u4e00-\u9fa5]+花园[\u4e00-\u9fa5]*)', 'community'),
        (r'([\u4e00-\u9fa5]+小区)', 'community'),
        (r'([\u4e00-\u9fa5]+公寓)', 'community'),
        (r'([\u4e00-\u9fa5]+苑|[\u4e00-\u9fa5]+园|[\u4e00-\u9fa5]+庭)', 'community'),
        (r'([\u4e00-\u9fa5]+路)(?:[\d\-]+号)?', 'road'),
        (r'([\u4e00-\u9fa5]+区)', 'district'),
    ]
    for p, kind in patterns:
        m = re.search(p, text)
        if m:
            result["rawMatched"].append((m.group(1), kind))
            if kind == "community" and not result["communityName"]:
                result["communityName"] = m.group(1)
            elif kind == "district":
                result["district"] = m.group(1)

    # 匹配楼栋
    building_match = re.search(r'(\d+)[栋号]', text)
    if building_match:
        result["building"] = building_match.group(1)

    unit_match = re.search(r'(\d+)单元', text)
    if unit_match:
        result["unit"] = unit_match.group(1)

    return result


def classify_need(text: str) -> str:
    """判断需求类型"""
    scores = {}
    for ntype, info in NEED_TYPES.items():
        score = sum(1 for kw in info["keywords"] if kw in text)
        scores[ntype] = score
    if max(scores.values()) == 0:
        return "邻里互助"
    return max(scores, key=scores.get)


def extract_topic(text: str) -> str:
    """提取需求主题"""
    # 去掉常见模式
    cleaned = re.sub(r'(附近|有没有|谁有|想找|想请|请问)', '', text)
    # 去掉位置描述
    cleaned = re.sub(r'[\u4e00-\u9fa5]+(?:花园|小区|公寓|路|街|道|苑|园|庭|邨|庄|府|邸|郡|湾|城)', '', cleaned)
    # 去掉句末标点
    cleaned = re.sub(r'[？?。.]+$', '', cleaned)
    cleaned = cleaned.strip()
    if len(cleaned) >= 2:
        return cleaned[:30]
    return "相关需求"


def generate_opener(text: str, need_type: str, location: dict) -> str:
    """生成联系话术"""
    topic = extract_topic(text)
    is_urgent = any(kw in text for kw in ["急需", "紧急", "急找", "马上", "立刻", "急用"])

    if is_urgent or need_type == "邻里互助":
        template = "大家好，我是{unit}的邻居，{topic}，请问有没有邻居可以帮忙？谢谢！"
    else:
        template = "请教各位邻居：{topic}，有经验的邻居可以分享一下吗？提前感谢！"

    unit_str = ""
    if location.get("building"):
        unit_str = f"{location['building']}栋"
        if location.get("unit"):
            unit_str += f"{location['unit']}单元"

    opener = template.format(unit=unit_str, topic=topic)
    return opener


def generate_connection_plan(need_type: str, location: dict) -> dict:
    """生成连接方案"""
    type_info = NEED_TYPES.get(need_type, NEED_TYPES["邻里互助"])
    plan = {
        "primaryChannel": type_info["channels"][0],
        "actionSteps": [],
        "estimatedResponseTime": "1-24小时",
        "tips": []
    }

    if need_type == "邻里互助":
        if location.get("communityName"):
            plan["actionSteps"] = [
                f"联系{location['communityName']}物业获取业主群二维码",
                "进群后修改群昵称为楼栋单元号",
                "在群内发送求助话术"
            ]
            plan["tips"] = ["尽量在白天发送，非紧急避免深夜打扰"]
        else:
            plan["actionSteps"] = ["确认所在小区名称", "联系物业获取业主群方式"]
    elif need_type == "商业服务":
        plan["actionSteps"] = [
            "在大众点评/美团搜索关键词",
            "查看附近评分4.5以上商家",
            "在业主群询问真实口碑"
        ]
        plan["estimatedResponseTime"] = "实时"
    elif need_type == "社交连接":
        plan["actionSteps"] = [
            "在业主群活动版发布拼团意向",
            "联系社区活动中心了解近期活动",
            "加入豆瓣同城相关小组"
        ]
        plan["estimatedResponseTime"] = "1-7天"
    else:
        plan["actionSteps"] = ["确认具体需求", "联系对应服务机构"]

    return plan


def handle(text: str) -> dict:
    location = parse_location(text)
    need_type = classify_need(text)
    opener = generate_opener(text, need_type, location)
    connection_plan = generate_connection_plan(need_type, location)

    return {
        "locationParsed": location,
        "needType": need_type,
        "urgency": NEED_TYPES[need_type]["urgency"],
        "connectionPlan": connection_plan,
        "openerScript": opener,
        "safetyNotice": (
            "请勿在公开场合透露具体门牌号或手机号。"
            "涉及医疗急救请拨打120，涉及财产安全隐患请拨打110。"
        )
    }


if __name__ == "__main__":
    test_cases = [
        "孩子半夜发烧，附近谁有退烧药？",
        "想找小区附近的靠谱宠物医院",
        "有没有一起拼周末去植物园的邻居？",
        "小区业主群怎么加入？",
    ]
    print("=== Community Connector 自测 ===\n")
    for tc in test_cases:
        result = handle(tc)
        print(f"Input: {tc}")
        print(f"  -> needType={result['needType']} urgency={result['urgency']}")
        print(f"  -> opener: {result['openerScript']}")
        print(f"  -> plan: {result['connectionPlan']['primaryChannel']} | {result['connectionPlan']['actionSteps'][0] if result['connectionPlan']['actionSteps'] else 'N/A'}")
        print()
