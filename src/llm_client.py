"""LLM seam (코어 어댑터) — 단일 파일로 LLM 호출을 격리.

기본 = Claude **구독**(Claude Code 로그인) 기반. API 키 불필요.
reuser는 이 파일의 complete()/complete_json() 두 함수만 갈아끼우면
ANTHROPIC_API_KEY나 타 provider로 전환할 수 있다. (core/adapter thesis)

게이트 thesis: LLM은 "어떤 툴+인자"만 고르고(structured selection),
판정·실행은 LangGraph가 한다. 그래서 여기 함수는 텍스트/JSON 반환만 한다.
"""

from __future__ import annotations

import json
import os
import re
import subprocess

_MODEL = os.environ.get("ANTHROPIC_MODEL")  # 없으면 Claude Code 기본 모델


def complete(prompt: str, system: str | None = None, timeout: int = 90) -> str:
    """구독 기반 단발 호출 → 텍스트 반환."""
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if _MODEL:
        cmd += ["--model", _MODEL]
    if system:
        cmd += ["--append-system-prompt", system]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (rc={proc.returncode}): {proc.stderr[:300]}")

    payload = json.loads(proc.stdout)
    if payload.get("is_error"):
        raise RuntimeError(f"claude error: {payload.get('result')}")
    return payload["result"]


def _strip_fence(text: str) -> str:
    """```json ... ``` 펜스 제거."""
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


def complete_json(prompt: str, system: str | None = None, timeout: int = 90) -> dict:
    """구독 기반 단발 호출 → JSON 파싱 반환. structured selection용."""
    raw = complete(prompt, system=system, timeout=timeout)
    return json.loads(_strip_fence(raw))


if __name__ == "__main__":
    out = complete_json(
        "도구 중 하나를 골라라. 도구: get_transaction(transaction_id), calc_fee(amount, method).\n"
        "질문: 'TX1009 거래 조회해줘'\n"
        'JSON만 출력: {"tool":"...","args":{...}}'
    )
    print("selection:", out)
