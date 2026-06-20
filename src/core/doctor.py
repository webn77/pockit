"""Pockit Doctor — 프로젝트 환경 및 의존성 자가 진단 스크립트."""
from __future__ import annotations

import sys
from pathlib import Path

def check_dependencies() -> bool:
    print("[1] 파이썬 패키지 의존성 검사 중...")
    required = ["langgraph", "langchain_core", "chromadb", "sentence_transformers", "mcp"]
    ok = True
    for req in required:
        try:
            __import__(req)
            print(f"  ✓ {req} 로드 성공")
        except ImportError:
            print(f"  ✗ {req} 로드 실패 (설치가 필요합니다)")
            ok = False
    return ok

def check_paths() -> bool:
    print("[2] 중요 데이터 및 정책 파일 검사 중...")
    root = Path(__file__).resolve().parents[2]
    
    paths = {
        "CSV 거래 데이터": root / "data" / "transactions.csv",
        "환불 정책 문서": root / "data" / "policies" / "refund_policy.md",
        "수수료 정책 문서": root / "data" / "policies" / "fee_policy.md",
        "기본 평가 골든셋": root / "src" / "core" / "eval" / "golden.jsonl",
    }
    
    ok = True
    for name, p in paths.items():
        if p.exists():
            print(f"  ✓ {name} 존재: {p.relative_to(root)}")
        else:
            print(f"  ✗ {name} 없음: {p.relative_to(root)}")
            ok = False
    return ok

def main():
    print("=== pockit Doctor: 시스템 진단 시작 ===")
    dep_ok = check_dependencies()
    path_ok = check_paths()
    
    print("\n=== 진단 결과 ===")
    if dep_ok and path_ok:
        print("  ✓ 모든 환경이 정상입니다! 데모 및 평가를 진행하셔도 좋습니다.")
        sys.exit(0)
    else:
        print("  ✗ 일부 설정에 문제가 발견되었습니다. 위 로그를 확인해 주세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()
