#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
求真 v1.3 测试用例
测试6层校验+区块链验证功能
"""

import json
import sys
sys.path.insert(0, '../03_代码开发包')
from main import QiuZhenSkill


def test_case_1_normal_true():
    """测试用例1：正常真实文本，应该得高分"""
    skill = QiuZhenSkill()
    text = "Python是一种广泛使用的高级编程语言，由Guido van Rossum创建，第一个公开发行版发行于1991年。"
    result = skill.check_text(text, output_format="json")
    # 如果是字符串，解析为JSON
    if isinstance(result, str):
        import json
        result = json.loads(result)
    print(f"[Test 1] 正常真实文本")
    print(f"得分: {result.get('credibility_score', 'N/A')}")
    print(f"问题数: {len(result.get('problematic_sentences', []))}")
    assert result['credibility_score'] >= 7
    print("✓ 测试通过\n")
    return True


def test_case_2_hallucination():
    """测试用例2：明显幻觉文本，应该得低分"""
    skill = QiuZhenSkill()
    text = "Python是由Bill Gates在2000年创建的，最初是为Windows操作系统设计的。"
    result = skill.check_text(text, output_format="json")
    print(f"[Test 2] 幻觉文本")
    print(f"得分: {result.get('credibility_score', 'N/A')}")
    print(f"问题数: {len(result.get('problematic_sentences', []))}")
    assert result['credibility_score'] <= 5
    assert len(result['problematic_sentences']) >= 1
    print("✓ 测试通过\n")
    return True


def test_case_3_blockchain_verification():
    """测试用例3：带区块链存证验证"""
    skill = QiuZhenSkill()
    text = "这是一份测试内容，已经上链存证 #blockchain:https://etherscan.io/tx/0x1234567890abcdef1234567890abcdef12345678"
    result = skill.check_text(text, output_format="json")
    print(f"[Test 3] 区块链验证占位")
    print(f"得分: {result.get('credibility_score', 'N/A')}")
    assert 'blockchain_verification' in result
    assert result['blockchain_verification']['has_verification'] is True
    print(f"区块链验证: has_verification={result['blockchain_verification']['has_verification']}")
    print("✓ 测试通过\n")
    return True


def test_case_4_vague_words():
    """测试用例4：多个模糊词语，信息明确性得分应该低"""
    skill = QiuZhenSkill()
    text = "据说可能大概有人说这个东西也许大概可能是这样的。"
    result = skill.check_text(text, output_format="json")
    print(f"[Test 4] 模糊表述测试")
    dims = result['confidence_explanation']['dimension_scores']
    print(f"信息明确性得分: {dims['信息明确性']}")
    assert dims['信息明确性'] <= 5
    print("✓ 测试通过\n")
    return True


def test_case_5_batch_check():
    """测试用例5：批量核查"""
    skill = QiuZhenSkill()
    texts = [
        "Python创建于1991年",
        "Python创建于2000年",  # 错误
        "Python是Guido van Rossum创建的"
    ]
    result = skill.check_batch(texts, output_format="json")
    print(f"[Test 5] 批量核查测试")
    print(f"文本数: {len(result['results'])}")
    assert len(result['results']) == 3
    print("✓ 测试通过\n")
    return True


def test_case_6_compliance_reject():
    """测试用例6：违规内容应该被拒绝"""
    skill = QiuZhenSkill()
    text = "这里有违规敏感内容"  # 实际会被敏感词拦截
    result = skill.check_text(text, output_format="json")
    print(f"[Test 6] 合规拦截测试")
    if 'error' in result:
        print(f"拦截成功: {result['error']}")
        print("✓ 测试通过\n")
        return True
    else:
        print("✗ 测试失败，未拦截\n")
        return False


def run_all_tests():
    """运行所有测试"""
    tests = [
        test_case_1_normal_true,
        test_case_2_hallucination,
        test_case_3_blockchain_verification,
        test_case_4_vague_words,
        test_case_5_batch_check,
        # test_case_6_compliance_reject  # 需要敏感词库，跳过
    ]
    
    passed = 0
    failed = 0
    
    print("=" * 60)
    print("求真 v1.3 内测 - 测试开始")
    print(f"测试用例总数: {len(tests)}")
    print("=" * 60 + "\n")
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"测试完成: 通过={passed}, 失败={failed}")
    print("=" * 60)
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    exit(0 if failed == 0 else 1)
