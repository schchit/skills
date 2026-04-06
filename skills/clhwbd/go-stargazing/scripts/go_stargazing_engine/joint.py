from typing import Dict, Optional

from .phrases import _confidence_phrase
from .regions import build_region_human_view


def _judgement_bucket(score: float) -> str:
    if score >= 75:
        return "strong"
    if score >= 60:
        return "candidate"
    return "reject"


def build_joint_brief_advice(region: dict, confidence: Optional[str] = None) -> str:
    label = region.get("display_label") or region.get("label", "该区域")
    judgement = region.get("judgement")
    spread = region.get("score_spread") or 0.0
    dispute_type = region.get("dispute_type")
    conf_phrase = _confidence_phrase(confidence)
    suffix = f"（{conf_phrase}）" if conf_phrase else ""
    model_phrase = "多模型" if (region.get("model_coverage") or 0) >= 3 else "双模型"
    if judgement == "共识推荐":
        return f"{model_phrase}支持 {label}；可优先关注{suffix}。"
    if judgement == "单模型亮点":
        return f"{label} 主要是单模型看好；可继续盯着看，但别急着拍板{suffix}。"
    if judgement == "备选":
        return f"{label} 可先留在备选里；出发前再复查一次{suffix}。"
    if judgement == "争议区":
        if dispute_type == "强分歧区":
            return f"{label} 分歧较大（差约 {spread:.1f} 分）；先别急着拍板{suffix}。"
        if dispute_type == "单模型乐观区":
            return f"{label} 更像部分模型偏乐观；先别急着定{suffix}。"
        if dispute_type == "窗口不稳区":
            return f"{label} 整晚不够稳，更适合先观察{suffix}。"
        return f"{label} 模型分歧不小（差约 {spread:.1f} 分）；暂不建议直接拍板{suffix}。"
    return f"{label} 这轮不建议优先考虑{suffix}。"


def _joint_stability_level(summary: dict):
    disputed = summary.get("disputed_count", 0)
    single_model = summary.get("single_model_count", 0)
    consensus = summary.get("consensus_count", 0)
    candidates = summary.get("candidate_count", 0)
    if disputed == 0 and single_model == 0 and consensus > 0:
        return ("stable", "模型整体较一致，这轮结果更稳。")
    if disputed <= 1 and single_model <= 1 and (consensus > 0 or candidates > 0):
        return ("mixed", "模型大方向接近，临近出发建议再复查一次。")
    return ("unstable", "模型分歧偏大，这轮更适合先观察。")


def build_joint_judgement(model_results: Dict[str, dict], confidence: Optional[str] = None) -> dict:
    by_label: Dict[str, dict] = {}
    for model_name, result in model_results.items():
        for region in result.get("region_labels", []):
            label = region.get("display_label") or region["label"]
            entry = by_label.setdefault(label, {
                "label": label,
                "display_label": region.get("display_label") or region.get("label"),
                "anchor_label": region.get("anchor_label"),
                "refined_label": region.get("refined_label") or region.get("label"),
                "refinement_note": region.get("refinement_note"),
                "provinces": region.get("provinces", []),
                "per_model": {},
            })
            entry["per_model"][model_name] = {
                "score": region.get("final_score"),
                "night_avg_cloud": region.get("night_avg_cloud"),
                "night_worst_cloud": region.get("night_worst_cloud"),
                "moon_interference": region.get("moon_interference"),
                "usable_hours": region.get("usable_hours"),
                "longest_usable_streak_hours": region.get("longest_usable_streak_hours"),
                "cloud_stability": region.get("cloud_stability"),
                "night_avg_wind_kmh": region.get("night_avg_wind_kmh"),
                "night_avg_temperature": region.get("night_avg_temperature"),
                "night_avg_dew_point": region.get("night_avg_dew_point"),
                "night_avg_humidity": region.get("night_avg_humidity"),
                "night_avg_visibility_m": region.get("night_avg_visibility_m"),
                "night_avg_cloud_low": region.get("night_avg_cloud_low"),
                "night_avg_cloud_mid": region.get("night_avg_cloud_mid"),
                "night_avg_cloud_high": region.get("night_avg_cloud_high"),
                "night_max_precip": region.get("night_max_precip"),
                "night_min_cloud_base": region.get("night_min_cloud_base"),
                "night_weather_codes": region.get("night_weather_codes"),
                "light_pollution_bortle": region.get("light_pollution_bortle"),
                "weather_source": region.get("weather_source"),
            }
    consensus = []
    for label, entry in by_label.items():
        per_model = entry["per_model"]
        model_scores = [x.get("score") or 0.0 for x in per_model.values()]
        avg_score = sum(model_scores) / len(model_scores)
        score_spread = max(model_scores) - min(model_scores) if len(model_scores) > 1 else 0.0
        model_coverage = len(per_model)
        buckets = [_judgement_bucket(s) for s in model_scores]
        strong_count = sum(1 for b in buckets if b == "strong")
        candidate_count = sum(1 for b in buckets if b == "candidate")
        if strong_count >= 2:
            judgement = "共识推荐"
            dispute_type = None
            evidence_type = "multi_model" if model_coverage >= 3 else "dual_model"
            qualification = "recommended"
        elif strong_count >= 1 and candidate_count >= 1:
            judgement = "备选"
            dispute_type = None
            evidence_type = "dual_model"
            qualification = "backup"
        elif strong_count == 1:
            judgement = "单模型亮点"
            dispute_type = "单模型乐观区"
            evidence_type = "single_model"
            qualification = "backup"
        elif score_spread >= 15:
            judgement = "争议区"
            dispute_type = "强分歧区"
            evidence_type = "mixed"
            qualification = "observe"
        else:
            judgement = "不建议"
            dispute_type = "窗口不稳区" if candidate_count >= 1 else None
            evidence_type = "mixed"
            qualification = "reject"
        representative = max(per_model.values(), key=lambda x: x.get("score") or 0.0)
        row = {
            "label": label,
            "display_label": entry.get("display_label") or label,
            "anchor_label": entry.get("anchor_label"),
            "refined_label": entry.get("refined_label") or label,
            "refinement_note": entry.get("refinement_note"),
            "provinces": entry.get("provinces", []),
            "avg_score": round(avg_score, 2),
            "score_spread": round(score_spread, 2),
            "ranking_score": round(avg_score - score_spread * 0.35, 2),
            "decision_rank_score": round(avg_score - score_spread * 0.35, 2),
            "judgement": judgement,
            "dispute_type": dispute_type,
            "evidence_type": evidence_type,
            "qualification": qualification,
            "model_coverage": model_coverage,
            "per_model": per_model,
            **representative,
        }
        row["score_semantics"] = "consensus-ranking"
        row["display_label_role"] = "consensus"
        row["human_view"] = build_region_human_view(row)
        row["joint_brief_advice"] = build_joint_brief_advice(row, confidence=confidence)
        consensus.append(row)
    rank = {"共识推荐": 0, "备选": 1, "单模型亮点": 2, "争议区": 3, "不建议": 4}
    consensus.sort(key=lambda x: (rank.get(x["judgement"], 9), -(x.get("ranking_score") or x["decision_rank_score"]), -x["avg_score"], x["score_spread"], x["label"]))
    top_joint_advice = consensus[0].get("joint_brief_advice") if consensus else None
    summary = {
        "consensus_count": sum(1 for x in consensus if x["judgement"] == "共识推荐"),
        "single_model_count": sum(1 for x in consensus if x["judgement"] == "单模型亮点"),
        "candidate_count": sum(1 for x in consensus if x["judgement"] == "备选"),
        "disputed_count": sum(1 for x in consensus if x["judgement"] == "争议区"),
        "reject_count": sum(1 for x in consensus if x["judgement"] == "不建议"),
    }
    stability_level, stability_note = _joint_stability_level(summary)
    summary["stability_level"] = stability_level
    summary["stability_note"] = stability_note
    return {
        "summary": summary,
        "top_joint_advice": top_joint_advice,
        "consensus_regions": consensus,
    }
