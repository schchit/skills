# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)


def calculate_bmi(weight: float, height: float) -> float:
    """计算BMI指数。

    如果 height <= 0 或 weight <= 0，抛出 ValueError。
    如果 BMI < 18.5 返回偏瘦，18.5-24.9 返回正常，>= 25 返回偏胖。
    """
    if height <= 0 or weight <= 0:
        raise ValueError("weight and height must be positive")
    return weight / (height * height)


def is_adult(age: int, country: str = "CN") -> bool:
    """判断是否成年。

    Args:
        age: 年龄
        country: 国家代码，支持CN(18), US(21), JP(20)
    """
    thresholds = {"CN": 18, "US": 21, "JP": 20}
    return age >= thresholds.get(country, 18)


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def fibonacci(n: int) -> list:
    """生成斐波那契数列前n项"""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    result = [0, 1]
    for i in range(2, n):
        result.append(result[-1] + result[-2])
    return result
