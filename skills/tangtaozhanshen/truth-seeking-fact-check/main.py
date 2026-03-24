#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Truth (求真) Skill v1.3 - 入口模块
功能：6层事实核查，识别AI幻觉，输出可信度评分，支持区块链存证验证
可简称 truth 使用
"""

from typing import Dict, List, Union, Optional
import json
import logging
from preprocess import TextPreprocessor
from checker import FactChecker
from datasource import DataSourceManager
from batch import BatchProcessor
from formatter import OutputFormatter
from compliance import ComplianceChecker

logger = logging.getLogger(__name__)

class TruthSkill:
    """Truth (求真) 技能主类 - v1.3 6层校验版本"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化"""
        self.config = config or {}
        self.compliance = ComplianceChecker()
        self.preprocessor = TextPreprocessor()
        self.datasource = DataSourceManager(self.config.get('datasources', {}))
        self.checker = FactChecker(self.datasource)
        self.batch_processor = BatchProcessor(self.checker, max_concurrency=2)  # 适配2核2G，最大并发=2
        self.formatter = OutputFormatter()
        
    def get_metadata(self) -> Dict:
        """获取技能元数据"""
        return {
            "name": "Truth (求真)",
            "version": "v1.3",
            "description": "事实核查技能，6层深度核查（含区块链存证验证），核查内容真实性，识别AI幻觉。可简称truth使用。",
            "author": "tangtaozhanshen",
            "license": "MIT-0",
            "features": [
                "6层事实核查",
                "区块链存证验证",
                "批量核查支持",
                "置信度解释",
                "适配2核2G环境"
            ]
        }
    
    def check_text(self, text: str, output_format: str = "both") -> Union[Dict, str]:
        """单篇文本核查 - 6层版本"""
        # 1. 合规检查
        is_ok, reason = self.compliance.check(text)
        if not is_ok:
            return self.formatter.format_error(reason, output_format)
        
        # 2. 文本预处理
        sentences = self.preprocessor.split_sentences(text)
        
        # 3. 6层事实核查
        result = self.checker.check(text, sentences)
        
        # 4. 格式化输出
        return self.formatter.format_result(result, output_format)
    
    def check_batch(self, texts: List[str], output_format: str = "both") -> Union[Dict, str]:
        """批量文本核查"""
        # 合规检查每篇文本
        for idx, text in enumerate(texts):
            is_ok, reason = self.compliance.check(text)
            if not is_ok:
                texts[idx] = f"【违规内容已拦截】{reason}"
        
        # 批量核查
        results = self.batch_processor.process_batch(texts)
        
        # 格式化输出
        return self.formatter.format_batch_result(results, output_format)
    
    def check_url(self, url: str, output_format: str = "both") -> Union[Dict, str]:
        """网页URL核查"""
        # TODO: 实现网页抓取
        # 占位：下一阶段完成
        error_msg = "网页核查功能开发中，敬请期待 v1.4"
        return self.formatter.format_error(error_msg, output_format)
    
    def skill_entry(self, params: Dict) -> Dict:
        """OpenClaw 技能标准入口 - v1.3"""
        text = params.get('text', '')
        texts = params.get('texts', [])
        url = params.get('url', '')
        output_format = params.get('output_format', 'both')
        
        if url:
            result = self.check_url(url, output_format='json')
        elif texts:
            result = self.check_batch(texts, output_format='json')
        elif text:
            result = self.check_text(text, output_format='json')
        else:
            return {"error": "缺少输入参数：text/texts/url 其中一项必填"}
        
        if isinstance(result, str):
            return json.loads(result)
        return result


# 独立运行测试
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    skill = TruthSkill()
    print("=== Truth (求真) v1.3 测试 ===")
    print("元数据:", json.dumps(skill.get_metadata(), indent=2, ensure_ascii=False))
