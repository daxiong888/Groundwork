"""Pure route and evidence marker detection used by evals and hooks."""

import re

try:
    from routing_schema import DIRECT_ROUTE, UNKNOWN_ROUTE, normalize_route
except ImportError:  # pragma: no cover - package import path
    from evals.routing_schema import DIRECT_ROUTE, UNKNOWN_ROUTE, normalize_route


ROUTE_MARKERS = [
    ("dispatch", re.compile(r"^Dispatch Package\b|^Result Package\b|Dispatch Runtime Decision|Dispatch Candidate", re.I | re.M)),
    ("verify", re.compile(r"^Verification Scope\b|^验证范围\b", re.I | re.M)),
    ("handoff", re.compile(r"^\s*(?:#+\s*)?\*{0,2}(?:handoff(?:\s+package)?|交接)\*{0,2}\b", re.I | re.M)),
    ("implement", re.compile(r"^Implementation Summary\b|^实现摘要\b|^Files Changed\b|^Checks Run\b|^Scope:\s|^Acceptance Map:\s|^Evidence Inspected:\s|^Findings P0/P1/P2:\s", re.I | re.M)),
    ("write-plan", re.compile(r"Implementation Mini-Plan|implementation plan|实现计划|计划[:：]|可执行 plan|模板级 plan", re.I)),
    ("to-issues", re.compile(r"issue-map|Issue Map|Acceptance Criteria|验收标准|不能拆 issues|拆 issues", re.I)),
    ("to-prd", re.compile(r"^# PRD\b|Artifact Type:\s*PRD|产品需求", re.I | re.M)),
    ("triage", re.compile(r"triage|ready-for-agent|needs-info|blocked", re.I)),
    ("prototype", re.compile(r"prototype|原型", re.I)),
    ("wiki", re.compile(r"LLM Wiki|wiki update candidate|项目 wiki", re.I)),
]

PROMPT_ROUTE_MARKERS = [
    ("dispatch", re.compile(r"\bdispatch\b|分派|运行时路由", re.I)),
    ("verify", re.compile(r"\bverify\b|验证|ready|就绪|UAT|release|发布", re.I)),
    ("write-plan", re.compile(r"\bplan\b|计划|实现计划|先别写代码|不要编辑文件", re.I)),
    ("implement", re.compile(r"\bimplement\b|实施|实现|修复|改代码|按 PRD 实施", re.I)),
    ("to-issues", re.compile(r"拆\s*issues?|拆任务|issue-map|任务切片", re.I)),
    ("to-prd", re.compile(r"\bPRD\b|需求|产品方案|新需求", re.I)),
    ("handoff", re.compile(r"handoff|交接|续上|保存状态", re.I)),
    ("triage", re.compile(r"triage|判断能不能|是否适合|阻塞", re.I)),
    ("prototype", re.compile(r"prototype|原型", re.I)),
    ("wiki", re.compile(r"wiki|知识库", re.I)),
]

GIT_WRITE_RE = re.compile(r"\bgit\s+(add|commit|push|reset|checkout|switch|clean|merge|rebase)\b")
FILE_WRITE_RE = re.compile(r"\b(apply_patch|cat\s*>|tee\s+|python\d?\s+.*write_text|rm\s+)", re.I)
TEST_RE = re.compile(r"\b(pytest|unittest|npm\s+test|pnpm\s+test|go\s+test|cargo\s+test|mvn\s+test)\b", re.I)
GIT_STATUS_RE = re.compile(r"\bgit\s+status\b|\bgit\s+diff\b", re.I)


def detect_route_from_text(text):
    value = str(text or "")
    for route, pattern in ROUTE_MARKERS:
        if pattern.search(value):
            return route, "final_message_marker"
    if value.strip():
        return DIRECT_ROUTE, "final_message_marker"
    return UNKNOWN_ROUTE, "unknown"


def entry_decision_from_prompt(prompt):
    value = str(prompt or "")
    route = UNKNOWN_ROUTE
    for candidate, pattern in PROMPT_ROUTE_MARKERS:
        if pattern.search(value):
            route = candidate
            break
    if route == UNKNOWN_ROUTE and value.strip():
        route = DIRECT_ROUTE

    acceptable = [route] if route != UNKNOWN_ROUTE else []
    forbidden = []
    if route == "write-plan":
        forbidden = ["implement", "verify", "direct"]
    elif route == "implement":
        forbidden = ["verify", "dispatch"]
    elif route == "verify":
        forbidden = ["implement", "direct"]
    elif route == "to-prd":
        forbidden = ["implement", "to-issues"]

    return {
        "expected_best": normalize_route(route),
        "acceptable_routes": acceptable,
        "forbidden_routes": forbidden,
        "route_boundary": "entry-contract",
        "intent_kind": route if route in {"direct", "implement", "verify", "handoff", "prototype"} else "plan",
        "requirement_state": "implementation_ready" if route == "implement" else "unknown",
        "source_truth": "conversation",
        "risk_gate": "none",
        "expected_state_transition": "implement" if route == "implement" else "none",
        "expected_stop_condition": "continue" if route != DIRECT_ROUTE else "direct_answer",
    }


def classify_command(command, tool_name=""):
    tool = str(tool_name or "")
    text = str(command or "")
    if tool.startswith("mcp__"):
        return "mcp"
    if tool == "apply_patch":
        return "file_write"
    if GIT_STATUS_RE.search(text):
        return "git"
    if GIT_WRITE_RE.search(text):
        return "git"
    if TEST_RE.search(text):
        return "test"
    if FILE_WRITE_RE.search(text):
        return "file_write"
    if text.strip():
        return "file_read"
    return "unknown"


def risk_markers(command, tool_name=""):
    markers = []
    text = str(command or "")
    if tool_name == "apply_patch" or FILE_WRITE_RE.search(text):
        markers.append("file_write")
    if GIT_WRITE_RE.search(text):
        markers.append("git_write")
    if re.search(r"\brm\s+(-r|-f|-rf|-fr)\b|\bgit\s+reset\b|\bgit\s+clean\b", text):
        markers.append("destructive")
    return markers


def evidence_markers(command):
    text = str(command or "")
    markers = []
    if GIT_STATUS_RE.search(text):
        markers.append("git_status")
    if TEST_RE.search(text):
        markers.append("tests")
    if "python3 -m json.tool" in text:
        markers.append("json_validation")
    return markers
