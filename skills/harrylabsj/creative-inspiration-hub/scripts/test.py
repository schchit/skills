#!/usr/bin/env python3
"""Creative Inspiration Hub - Full Test Script"""
import sys
import json
sys.path.insert(0, '.')

from handler import handle_request

def test_all_branches():
    print("=== Creative Inspiration Hub Full Test ===\n")
    
    tests = [
        ("idea-generation", {"type": "idea-generation", "theme": "智能家居", "domains": ["technology", "design"]}),
        ("cross-domain", {"type": "cross-domain", "domainA": "technology", "domainB": "biology"}),
        ("inspiration-trigger", {"type": "inspiration-trigger", "keywords": ["创新", "突破"]}),
        ("evaluation", {"type": "evaluation", "ideaToEvaluate": "基于AI的推荐系统"}),
        ("mindmap", {"type": "mindmap", "coreConcept": "创新", "relatedThoughts": ["想法1", "想法2"]})
    ]
    
    results = []
    for name, req in tests:
        try:
            result = handle_request(req)
            success = result.get("success", False)
            has_data = (
                result.get("ideas") or 
                result.get("combinations") or 
                result.get("triggers") or 
                result.get("evaluation") or
                result.get("mindmap")
            )
            status = "PASS" if success and has_data else "FAIL"
            print(f"{name}: {status}")
            if not has_data:
                print(f"  Warning: {list(result.keys())}")
            results.append((name, status))
        except Exception as e:
            print(f"{name}: ERROR - {e}")
            results.append((name, "ERROR"))
    
    print(f"\n=== Summary: {sum(1 for _, s in results if s == 'PASS')}/{len(results)} passed ===")
    return all(s == "PASS" for _, s in results)

if __name__ == "__main__":
    success = test_all_branches()
    sys.exit(0 if success else 1)
