import pytest
from pathlib import Path
from src.core.eval.run_eval import ReportBuilder

def test_generate_report_writes_file():
    mock_results = [
        {
            "id": 1,
            "category": "refund",
            "query": "환불해줘",
            "tool": "issue_refund",
            "tool_ok": True,
            "expected_tool": "issue_refund",
            "decision": "ALLOW",
            "gate_ok": True,
            "expected_gate": "ALLOW",
            "ret_ok": True,
            "faith_ok": None
        }
    ]
    
    mock_metrics = {
        "total": 1,
        "tool_acc": 1.0,
        "gate_acc": 1.0,
        "ret_prec": 1.0
    }
    
    report_path = ReportBuilder.generate_report("test_suite", mock_results, mock_metrics)
    
    assert report_path.exists(), "Report file was not created"
    assert report_path.is_file(), "Report path is not a file"
    
    content = report_path.read_text(encoding="utf-8")
    assert "Pockit" in content, "Dashboard template name is missing"
    assert "test_suite" in content, "Eval set name is not replaced"
    assert "issue_refund" in content, "Mock results json is not injected"
