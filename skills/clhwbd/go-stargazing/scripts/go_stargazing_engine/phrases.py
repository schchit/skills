from typing import Optional


def _confidence_phrase(confidence: Optional[str], model: Optional[str] = None) -> Optional[str]:
    model_rank = {"ecmwf_ifs": 3, "gfs_global": 2, "icon_global": 2, None: 0}.get(model, 0)
    if confidence == "high" and model_rank >= 2:
        return "短期预报可信度较高，且使用了较高分辨率模型，结果相对可靠"
    if confidence == "high":
        return "短期预报可信度较高"
    if confidence == "medium" and model_rank >= 2:
        return "属于中期预报，但使用了较高分辨率模型，参考价值仍较强，建议出发前再复查一次"
    if confidence == "medium":
        return "属于中期预报，预报精度有所下降，建议出发前再复查一次"
    if confidence == "low" and model_rank >= 2:
        return "属于中远期预报，更适合作趋势参考；较高分辨率模型有助于减少误判"
    if confidence == "low":
        return "属于中远期预报，当前更适合作趋势参考"
    return None
