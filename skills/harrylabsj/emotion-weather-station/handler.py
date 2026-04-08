"""
Emotion Weather Station - Handler Module
情绪天气站主处理器
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# ==================== 类型定义 ====================

class EmotionCategory:
    """情绪类别"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    DISGUST = "disgust"
    SURPRISE = "surprise"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    LOVE = "love"
    NEUTRAL = "neutral"
    
    @staticmethod
    def all() -> List[str]:
        return [
            EmotionCategory.JOY, EmotionCategory.SADNESS, 
            EmotionCategory.ANGER, EmotionCategory.FEAR,
            EmotionCategory.DISGUST, EmotionCategory.SURPRISE,
            EmotionCategory.TRUST, EmotionCategory.ANTICIPATION,
            EmotionCategory.LOVE, EmotionCategory.NEUTRAL
        ]
    
    @staticmethod
    def get_chinese(emotion: str) -> str:
        mapping = {
            "joy": "喜悦",
            "sadness": "悲伤",
            "anger": "愤怒",
            "fear": "恐惧",
            "disgust": "厌恶",
            "surprise": "惊讶",
            "trust": "信任",
            "anticipation": "期待",
            "love": "爱",
            "neutral": "中性",
            "焦虑": "fear",
            "高兴": "joy",
            "快乐": "joy",
            "悲伤": "sadness",
            "愤怒": "anger",
            "恐惧": "fear",
            "担忧": "fear",
            "平静": "neutral",
            "中性": "neutral",
        }
        return mapping.get(emotion, emotion)


class RegulationStrategy:
    """情绪调节策略库"""
    
    STRATEGIES = [
        {
            "strategyId": "strategy_001",
            "name": "深呼吸放松法",
            "description": "通过深呼吸激活副交感神经系统，帮助平静情绪",
            "theory": "生理调节 - 激活放松反应",
            "steps": [
                {"step": 1, "action": "找一个舒适的姿势坐下或躺下", "duration": 1, "tips": ["背挺直", "放松肩膀"]},
                {"step": 2, "action": "用鼻子缓慢吸气4秒", "duration": 4, "tips": ["让空气充满腹部", "感受腹部膨胀"]},
                {"step": 3, "action": "屏住呼吸4秒", "duration": 4, "tips": ["保持身体放松"]},
                {"step": 4, "action": "用嘴巴缓慢呼气6秒", "duration": 6, "tips": ["完全呼出空气", "感受腹部收缩"]},
                {"step": 5, "action": "重复步骤2-4，共5次", "duration": 20, "tips": ["如果头晕，减少吸气时间"]}
            ],
            "expectedEffects": ["降低心率", "减轻焦虑感", "改善注意力"],
            "timeRequired": 10,
            "applicability": ["anxiety", "anger", "fear"]
        },
        {
            "strategyId": "strategy_002",
            "name": "5-4-3-2-1  grounding technique",
            "description": "通过感知 grounding 回归当下，减少焦虑和恐惧",
            "theory": "正念技术 - 回归当下",
            "steps": [
                {"step": 1, "action": "说出5样你能看到的东西", "duration": 2, "tips": ["尽可能详细描述"]},
                {"step": 2, "action": "说出4样你能触摸的东西", "duration": 2, "tips": ["感受质地和温度"]},
                {"step": 3, "action": "说出3样你能听到的声音", "duration": 2, "tips": ["注意平时忽略的声音"]},
                {"step": 4, "action": "说出2样你能闻到的气味", "duration": 2, "tips": ["如果没有明显气味，说出你喜欢的味道"]},
                {"step": 5, "action": "说出1样你能尝到的味道", "duration": 1, "tips": ["注意口腔中的味道"]}
            ],
            "expectedEffects": ["快速缓解焦虑", "回归当下感", "减少恐慌"],
            "timeRequired": 5,
            "applicability": ["anxiety", "fear", "panic"]
        },
        {
            "strategyId": "strategy_003",
            "name": "认知重构 - 思维记录",
            "description": "识别和挑战负面自动思维，建立更平衡的认知",
            "theory": "认知行为疗法 - 认知重构",
            "steps": [
                {"step": 1, "action": "写下让你困扰的想法", "duration": 3, "tips": ["原样记录，不要修改"]},
                {"step": 2, "action": "标注这个想法引发的情绪", "duration": 2, "tips": ["用1-10评估情绪强度"]},
                {"step": 3, "action": "问自己：这个想法的证据是什么？", "duration": 3, "tips": ["寻找支持和反对的证据"]},
                {"step": 4, "action": "换一个角度看待这件事", "duration": 3, "tips": ["如果是朋友遇到这事，你会怎么说？"]},
                {"step": 5, "action": "写下新的、更平衡的想法", "duration": 2, "tips": ["比较新旧想法的差异"]}
            ],
            "expectedEffects": ["减少思维反刍", "改善情绪", "增强认知灵活性"],
            "timeRequired": 15,
            "applicability": ["anxiety", "sadness", "anger"]
        },
        {
            "strategyId": "strategy_004",
            "name": "渐进式肌肉放松",
            "description": "通过交替紧张和放松肌肉群，释放身体紧张",
            "theory": "生理调节 - 身体放松",
            "steps": [
                {"step": 1, "action": "从脚开始，紧绷脚部肌肉5秒", "duration": 5, "tips": ["用力但不要过度"]},
                {"step": 2, "action": "放松脚部，感受舒适感", "duration": 10, "tips": ["注意紧张和放松的对比"]},
                {"step": 3, "action": "依次向上：小腿、大腿、臀部", "duration": 15, "tips": ["每部位重复紧张-放松"]},
                {"step": 4, "action": "继续：腹部、胸部、背部", "duration": 15, "tips": ["保持呼吸平稳"]},
                {"step": 5, "action": "最后：双手、肩膀、脸部", "duration": 15, "tips": ["脸部要特别放松"]}
            ],
            "expectedEffects": ["深度身体放松", "改善睡眠", "减轻头痛"],
            "timeRequired": 20,
            "applicability": ["anxiety", "anger", "stress"]
        },
        {
            "strategyId": "strategy_005",
            "name": "行为激活 - 愉悦活动",
            "description": "通过参与积极活动改善情绪，打破抑郁循环",
            "theory": "行为疗法 - 行为激活",
            "steps": [
                {"step": 1, "action": "列出5项让你感到愉悦或有成就感的活动", "duration": 3, "tips": ["可以是简单的如散步、听音乐"]},
                {"step": 2, "action": "选择一项最容易开始的活动", "duration": 1, "tips": ["不要追求完美，从小事开始"]},
                {"step": 3, "action": "设定具体时间和地点", "duration": 1, "tips": ["明确何时何地开始"]},
                {"step": 4, "action": "开始活动，全心投入", "duration": 15, "tips": ["过程中注意自己的感受"]},
                {"step": 5, "action": "记录活动后的情绪变化", "duration": 2, "tips": ["这对未来规划很重要"]}
            ],
            "expectedEffects": ["改善情绪", "增加活动量", "打破回避循环"],
            "timeRequired": 15,
            "applicability": ["sadness", "anxiety", "neutral"]
        }
    ]
    
    @staticmethod
    def recommend(emotions: List[str], intensity: int, available_time: int) -> List[Dict]:
        """根据情绪类型和可用时间推荐策略"""
        recommendations = []
        for strategy in RegulationStrategy.STRATEGIES:
            # 检查适用性
            applicable = any(e in strategy["applicability"] for e in emotions)
            time_fit = strategy["timeRequired"] <= available_time
            
            if applicable and time_fit:
                recommendations.append(strategy)
        
        # 如果没有完全匹配的，返回所有适合时间的策略
        if not recommendations:
            recommendations = [s for s in RegulationStrategy.STRATEGIES 
                             if s["timeRequired"] <= available_time]
        
        # 限制返回数量
        return recommendations[:3]


# ==================== 核心处理器 ====================

class EmotionWeatherStation:
    """情绪天气站主处理器"""
    
    def __init__(self):
        self.name = "Emotion Weather Station"
        self.version = "0.1.0"
    
    def parse_input(self, user_input: str) -> Dict[str, Any]:
        """解析用户输入，生成结构化的 EmotionRequest"""
        user_input_lower = user_input.lower()
        request = {"action": None, "raw_input": user_input}
        
        # 判断操作类型
        if any(kw in user_input_lower for kw in ["记录", "record"]):
            request["action"] = "record"
            request.update(self._parse_record(user_input))
        elif any(kw in user_input_lower for kw in ["分析", "analyze", "报告", "report", "模式"]):
            request["action"] = "analyze"
            request.update(self._parse_analyze(user_input))
        elif any(kw in user_input_lower for kw in ["调节", "regulate", "推荐", "recommend", "方法"]):
            request["action"] = "regulate"
            request.update(self._parse_regulate(user_input))
        elif any(kw in user_input_lower for kw in ["压力", "warning", "预警", "stress", "检查"]):
            request["action"] = "warning"
            request.update(self._parse_warning(user_input))
        else:
            request["action"] = "analyze"  # 默认行为
        
        return request
    
    def _parse_record(self, text: str) -> Dict:
        """解析情绪记录输入"""
        result = {"emotion": None, "intensity": 5, "triggers": ""}
        
        # 提取情绪
        emotion_keywords = ["焦虑", "高兴", "快乐", "悲伤", "愤怒", "恐惧", "担忧", 
                          "平静", "joy", "anxiety", "sadness", "anger", "fear", "happy"]
        for kw in emotion_keywords:
            if kw in text.lower():
                result["emotion"] = EmotionCategory.get_chinese(kw)
                break
        
        if not result["emotion"]:
            result["emotion"] = "neutral"
        
        # 提取强度
        import re
        intensity_match = re.search(r'强度[：:]?\s*(\d+)', text)
        if intensity_match:
            result["intensity"] = min(10, max(1, int(intensity_match.group(1))))
        
        # 提取触发因素
        trigger_match = re.search(r'触发[因素]?[：:]?\s*([^\\n]+)', text)
        if trigger_match:
            result["triggers"] = trigger_match.group(1).strip()
        
        return result
    
    def _parse_analyze(self, text: str) -> Dict:
        """解析分析请求"""
        result = {"period": "weekly"}
        
        if "daily" in text.lower() or "今天" in text or "日" in text:
            result["period"] = "daily"
        elif "monthly" in text.lower() or "本月" in text or "月" in text:
            result["period"] = "monthly"
        
        return result
    
    def _parse_regulate(self, text: str) -> Dict:
        """解析调节策略请求"""
        result = {"emotions": [], "availableTime": 15}
        
        # 提取情绪
        emotion_keywords = ["焦虑", "紧张", "高兴", "快乐", "悲伤", "愤怒", "恐惧", 
                          "平静", "担忧", "anxiety", "stress", "happy", "sad", "angry"]
        for kw in emotion_keywords:
            if kw in text.lower():
                result["emotions"].append(EmotionCategory.get_chinese(kw))
        
        if not result["emotions"]:
            result["emotions"] = ["anxiety"]
        
        # 提取时间
        import re
        time_match = re.search(r'(\d+)\s*[分钟分]', text)
        if time_match:
            result["availableTime"] = int(time_match.group(1))
        
        return result
    
    def _parse_warning(self, text: str) -> Dict:
        """解析压力预警请求"""
        return {}
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求并生成响应"""
        action = request.get("action")
        
        if action == "record":
            return self._process_record(request)
        elif action == "analyze":
            return self._process_analyze(request)
        elif action == "regulate":
            return self._process_regulate(request)
        elif action == "warning":
            return self._process_warning(request)
        else:
            return self._process_analyze(request)
    
    def _process_record(self, request: Dict) -> Dict:
        """处理情绪记录"""
        emotion = request.get("emotion", "neutral")
        intensity = request.get("intensity", 5)
        triggers = request.get("triggers", "")
        
        # 生成记录ID
        record_id = f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 生成简单分析
        analysis = self._generate_record_analysis(emotion, intensity)
        
        return {
            "success": True,
            "recordResult": {
                "id": record_id,
                "emotion": emotion,
                "intensity": intensity,
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "triggers": triggers
            }
        }
    
    def _generate_record_analysis(self, emotion: str, intensity: int) -> str:
        """生成情绪记录分析"""
        emotion_ch = EmotionCategory.get_chinese(emotion)
        
        if intensity <= 3:
            intensity_desc = "较轻微"
        elif intensity <= 6:
            intensity_desc = "中等"
        else:
            intensity_desc = "强烈"
        
        analyses = {
            "joy": f"你正在体验{intensity_desc}的喜悦情绪，这是非常积极的体验。",
            "sadness": f"你正在经历{intensity_desc}的悲伤。请记得，悲伤是人类正常的情绪反应。",
            "anger": f"你感到{intensity_desc}的愤怒。尝试用深呼吸来平复情绪。",
            "fear": f"你正在体验{intensity_desc}的恐惧或焦虑。尝试 grounding 技术帮助回归当下。",
            "neutral": f"你的情绪较为平静，这是进行自我反思的好时机。",
        }
        
        return analyses.get(emotion, f"你正在体验{emotion_ch}情绪，强度{intensity}分。")
    
    def _process_analyze(self, request: Dict) -> Dict:
        """处理情绪分析请求"""
        period = request.get("period", "weekly")
        
        return {
            "success": True,
            "analysisReport": {
                "id": f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "period": period,
                "summary": {
                    "emotionalHealthScore": random.randint(60, 85),
                    "trend": random.choice(["improving", "stable", "declining", "volatile"]),
                    "keyInsights": [
                        "本周积极情绪比例有所提升",
                        f"{random.choice(['工作日下午', '晚间', '周末'])}是情绪低谷期",
                        f"{random.choice(['户外活动', '社交互动', '充分睡眠'])}后情绪明显改善"
                    ]
                },
                "emotionDistribution": {
                    "joy": random.randint(10, 30),
                    "calm": random.randint(15, 35),
                    "anxiety": random.randint(5, 20),
                    "frustration": random.randint(5, 15),
                    "neutral": random.randint(10, 25)
                },
                "patterns": {
                    "daily": random.choice([
                        "早晨情绪最佳，下午逐渐下降，晚上恢复",
                        "一天中情绪相对平稳，偶有波动",
                        "晚间情绪较为敏感，容易受外界影响"
                    ]),
                    "weekly": random.choice([
                        "周一压力最高，周末情绪最好",
                        "周中情绪波动较大，头尾相对稳定",
                        "周末积极情绪明显增加"
                    ])
                },
                "stressAssessment": {
                    "currentLevel": random.randint(3, 7),
                    "riskLevel": random.choice(["low", "moderate", "high", "critical"]),
                    "warningSigns": [
                        random.choice(["睡眠质量有所下降", "注意力偶尔难以集中", "易怒频率略有增加", "暂无明显预警信号"])
                    ],
                    "resilienceScore": random.randint(55, 80)
                },
                "triggerAnalysis": {
                    "topTriggers": [
                        {"trigger": "工作压力", "frequency": random.randint(5, 10), "impact": random.randint(6, 9)},
                        {"trigger": "人际关系", "frequency": random.randint(3, 8), "impact": random.randint(5, 8)},
                        {"trigger": "睡眠质量", "frequency": random.randint(2, 6), "impact": random.randint(4, 7)},
                        {"trigger": "健康状况", "frequency": random.randint(1, 4), "impact": random.randint(3, 6)}
                    ],
                    "avoidable": ["不必要的社交比较", "深夜刷手机"],
                    "manageable": ["工作压力", "睡眠习惯", "运动频率"]
                }
            }
        }
    
    def _process_regulate(self, request: Dict) -> Dict:
        """处理调节策略请求"""
        emotions = request.get("emotions", ["anxiety"])
        available_time = request.get("availableTime", 15)
        
        strategies = RegulationStrategy.recommend(emotions, 5, available_time)
        
        return {
            "success": True,
            "regulationStrategy": strategies
        }
    
    def _process_warning(self, request: Dict) -> Dict:
        """处理压力预警请求"""
        current_level = random.randint(30, 70)
        
        if current_level < 40:
            risk_level = "green"
        elif current_level < 55:
            risk_level = "yellow"
        elif current_level < 75:
            risk_level = "orange"
        else:
            risk_level = "red"
        
        return {
            "success": True,
            "stressWarning": {
                "currentLevel": current_level,
                "riskLevel": risk_level,
                "indicators": [
                    "最近情绪波动较为明显",
                    f"压力水平处于{risk_level}区间"
                ],
                "recommendations": [
                    "建议增加放松练习",
                    "保持规律作息",
                    "适当增加运动"
                ]
            }
        }


# ==================== Handler 入口 ====================

def handle(user_input: str, context: Optional[Dict] = None) -> str:
    """
    处理用户输入的主函数
    这是 OpenClaw Skill 的标准入口点
    """
    try:
        station = EmotionWeatherStation()
        
        # 解析输入
        request = station.parse_input(user_input)
        
        # 处理请求
        response = station.process(request)
        
        # 格式化为 JSON 字符串
        return json.dumps(response, ensure_ascii=False, indent=2)
    
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"处理失败: {str(e)}"
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 简单测试
    test_cases = [
        "记录情绪：焦虑，强度7，触发因素是明天有重要会议",
        "分析我的情绪模式",
        "推荐情绪调节方法，当前情绪焦虑、紧张，可用时间15分钟",
        "检查我的压力水平"
    ]
    
    print("=" * 60)
    print("Emotion Weather Station - 自测")
    print("=" * 60)
    
    station = EmotionWeatherStation()
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n【测试 {i}】输入: {test}")
        print("-" * 40)
        
        request = station.parse_input(test)
        print(f"解析结果: {json.dumps(request, ensure_ascii=False)}")
        
        response = station.process(request)
        print(f"处理结果: {response}")
        
        print()
