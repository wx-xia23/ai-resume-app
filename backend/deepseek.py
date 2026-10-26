"""DeepSeek 客户端：构造 prompt、发起请求、解析固定 JSON 结果。"""

import json
import os
import re

import requests

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 90


class DeepSeekTimeout(Exception):
    """请求 DeepSeek 超时。"""


class DeepSeekError(Exception):
    """DeepSeek 调用失败或返回内容无法解析。"""


def _build_messages(resume_text: str, industries: list[str]) -> list[dict]:
    system_prompt = (
        "你是一位资深HR总监兼简历优化专家，拥有互联网、人工智能、金融、设计、"
        "市场、人力资源、教育等多个行业的招聘经验。你的任务是根据候选人简历内容，"
        "客观、专业地给出综合评分与针对性的优化建议。"
    )
    industry_list = "、".join(industries)
    user_prompt = f"""请评估以下候选人简历，意向行业为：{industry_list}。

要求：
1. 只输出一个 JSON 对象，不要输出任何其他文字或 Markdown。
2. JSON 结构必须严格为：
{{
  "total_score": 0,
  "general_advice": "通用修改建议",
  "industry_scores": [
    {{"industry": "行业名称", "score": 0, "advice": "针对性优化建议"}}
  ]
}}
3. total_score 为 0-100 的整数，代表简历综合质量。
4. industry_scores 中每个元素对应一个意向行业，字段 industry 必须与给出的行业名称完全一致。
5. 评分依据：教育背景、工作经历与项目成果、技能匹配度、量化数据、排版与可读性、亮点呈现。
6. advice 要具体、可执行，指出简历中缺失或薄弱的部分。

简历内容如下：
---简历开始---
{resume_text}
---简历结束---"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _extract_json(content: str) -> dict:
    """剥离 ```json 围栏，json.loads 失败时正则截取 { ... } 兜底。"""
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    raise DeepSeekError("AI 返回内容无法解析为 JSON")


def _clamp_score(value) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))


def _normalize_result(data: dict, industries: list[str]) -> dict:
    total = _clamp_score(data.get("total_score", 0))
    general = str(data.get("general_advice", "")).strip() or "暂无通用建议"

    raw_scores = data.get("industry_scores") or data.get("industries") or []
    score_map = {}
    for item in raw_scores:
        if not isinstance(item, dict):
            continue
        name = str(item.get("industry", "")).strip()
        if not name:
            continue
        advice = str(item.get("advice", "")).strip() or "暂未给出该行业建议"
        score_map[name] = {
            "industry": name,
            "score": _clamp_score(item.get("score", 0)),
            "advice": advice,
        }

    industry_scores = []
    for name in industries:
        industry_scores.append(
            score_map.get(name, {"industry": name, "score": 0, "advice": "暂未给出该行业建议"})
        )

    return {
        "total_score": total,
        "general_advice": general,
        "industry_scores": industry_scores,
    }


def evaluate_resume(resume_text: str, industries: list[str]) -> dict:
    """调用 DeepSeek 评估简历，返回规范化后的固定 JSON。"""
    if not DEEPSEEK_API_KEY:
        raise DeepSeekError("未配置 DEEPSEEK_API_KEY 环境变量，请在启动前设置")

    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": _build_messages(resume_text, industries),
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    except requests.Timeout:
        raise DeepSeekTimeout("AI 评估超时")
    except requests.RequestException as exc:
        raise DeepSeekError(f"请求 DeepSeek 失败：{exc}")

    if resp.status_code != 200:
        raise DeepSeekError(f"DeepSeek 接口返回异常：HTTP {resp.status_code} {resp.text[:200]}")

    try:
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as exc:
        raise DeepSeekError(f"DeepSeek 返回结构异常：{exc}")

    data = _extract_json(content)
    return _normalize_result(data, industries)