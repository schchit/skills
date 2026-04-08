#!/usr/bin/env python3
"""
Emotion Weather Station - Test Script
"""
import sys
import json
sys.path.insert(0, '.')

from handler import handle

def test_record():
    print("=== Test: record ===")
    result = handle("记录情绪：焦虑，强度7，触发因素是明天有重要会议")
    data = json.loads(result)
    assert data.get("success") == True
    assert "recordResult" in data
    print(f"  PASS: recorded {data['recordResult']['emotion']} intensity {data['recordResult']['intensity']}")

def test_analysis():
    print("=== Test: analysis ===")
    result = handle("分析我这一周的情绪")
    data = json.loads(result)
    assert data.get("success") == True
    print(f"  PASS: analysis returned")

def test_insight():
    print("=== Test: insight ===")
    result = handle("给我一些情绪调节建议")
    data = json.loads(result)
    assert data.get("success") == True
    print(f"  PASS: insight returned")

def test_pattern():
    print("=== Test: pattern ===")
    result = handle("发现我的情绪模式")
    data = json.loads(result)
    assert data.get("success") == True
    print(f"  PASS: pattern returned")

def test_weekly_summary():
    print("=== Test: weekly_summary ===")
    result = handle("生成情绪周报")
    data = json.loads(result)
    assert data.get("success") == True
    print(f"  PASS: weekly_summary returned")

def run_all():
    print("============================================================")
    print("Emotion Weather Station - Test Script")
    print("============================================================")
    tests = [test_record, test_analysis, test_insight, test_pattern, test_weekly_summary]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
    print(f"============================================================")
    print(f"Results: {passed}/{len(tests)} passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
