"""Runtime-safe route and evidence marker detection shared by hooks and evals."""

import json
from pathlib import Path
import re


CLASSIFIER_SOURCE_PATH = str(Path(__file__).resolve())
ROUTE_REGISTRY_PATH = Path(__file__).resolve().with_name("groundwork_route_registry.json")
ROUTE_REGISTRY = json.loads(ROUTE_REGISTRY_PATH.read_text(encoding="utf-8"))

PUBLIC_SKILL_ROUTES = set(ROUTE_REGISTRY["public_routes"])
PROMPT_PRECEDENCE = tuple(ROUTE_REGISTRY["prompt_precedence"])
DEFAULT_FORBIDDEN_ROUTES = ROUTE_REGISTRY["default_forbidden_routes"]
DIRECT_ROUTE = "direct"
UNKNOWN_ROUTE = "unknown"
HOST_PREEMPTION_ROUTE = "runtime-safety-gate"
WORKFLOW_ROUTES = PUBLIC_SKILL_ROUTES | {DIRECT_ROUTE, UNKNOWN_ROUTE, HOST_PREEMPTION_ROUTE}

CONCEPT_EXPLANATION_RE = re.compile(r"有什么区别|区别是什么|简单解释|概念区别|difference between", re.I)
EVIDENCE_UPGRADE_RE = re.compile(r"能不能|可以|可否|是否|算|当|作为|证据|evidence|readiness|验收|通过|升级", re.I)
EVIDENCE_BOUNDARY_QUESTION_PATTERN = (
    r"("
    r"(?:runtime|test(?:s)?|screenshot(?:s)?|source|cache|evidence|运行时|测试|截图|源码|源代码|缓存|证据)"
    r".{0,40}"
    r"(?:能不能|可不可以|可以|可否|是否|算不算|算|当|作为|升级|count(?:s)? as|satisf(?:y|ies)|support|prove)"
    r".{0,40}"
    r"(?:readiness|ready|release|UAT|acceptance|验收|通过|就绪|发布|clean[- ]?review|证据)"
    r")|("
    r"(?:readiness|ready|release|UAT|acceptance|验收|通过|就绪|发布|clean[- ]?review)"
    r".{0,40}"
    r"(?:能不能|可不可以|可以|可否|是否|算不算|算|当|作为|升级|count(?:s)? as|satisf(?:y|ies)|support|prove)"
    r".{0,40}"
    r"(?:runtime|test(?:s)?|screenshot(?:s)?|source|cache|evidence|运行时|测试|截图|源码|源代码|缓存|证据)"
    r")"
)
EVIDENCE_BOUNDARY_QUESTION_RE = re.compile(EVIDENCE_BOUNDARY_QUESTION_PATTERN, re.I)

DIRECT_PLAIN_TEXT_RE = re.compile(
    r"错别字|错字|typo|润色|polish|rewrite this sentence|"
    r"^\s*(?:什么是|.*是什么\??|.*是什么意思|what is|what does .+ mean|first principles 是什么意思)",
    re.I,
)
PLANMODE_PRD_RE = re.compile(
    r"(?:Plan Mode|计划模式).{0,80}(?:PRD|需求|docs/prd|创建|写|落文件|不要确认|不需要再确认)|"
    r"(?:PRD|需求|新需求|产品方案|方案|workflow|流程).{0,80}(?:草稿|draft|新|设计|新增|创建|收敛|改成)",
    re.I,
)
RAW_DELEGATION_RE = re.compile(
    r"(?:我有个|有个|新的?|new).{0,30}(?:想法|idea|新功能|feature|需求|方案).{0,80}"
    r"(?:直接|先)?\s*(?:拆(?:成)?\s*issues?|拆任务|issue drafts?|任务切片).{0,80}"
    r"(?:agent|并行|不要先问|不要问|不问问题)",
    re.I,
)
EXISTING_ISSUE_READINESS_RE = re.compile(
    r"(?:triage|判断|能不能|是否|哪些能|哪些需要).{0,80}(?:issue|issues|任务).{0,80}"
    r"(?:给\s*(?:子\s*)?agent\s*做|ready[-_ ]?for[-_ ]?agent|ready[-_ ]?for[-_ ]?human|AFK|HITL|人决定|blocked|blocker|阻塞)|"
    r"(?:issue|issues|任务).{0,80}(?:triage|判断|能不能|是否|哪些能|哪些需要).{0,80}"
    r"(?:给\s*(?:子\s*)?agent\s*做|ready[-_ ]?for[-_ ]?agent|ready[-_ ]?for[-_ ]?human|AFK|HITL|人决定|blocked|blocker|阻塞)",
    re.I,
)
CLOSEOUT_DECISION_RE = re.compile(
    r"(?:verify|测试|checks?|验证|done|wontfix).{0,80}(?:通过|pass(?:ed)?|完成|证据|evidence|owner).{0,80}"
    r"(?:判断|能不能|是否|可不可以).{0,50}(?:close|关闭|关掉|closeout|结案|关\s*issue)|"
    r"(?:判断|能不能|是否|可不可以).{0,50}(?:close|关闭|关掉|closeout|结案|关\s*issue).{0,80}"
    r"(?:verify|测试|checks?|验证|done|wontfix|通过|pass(?:ed)?|证据|evidence)",
    re.I,
)
AUDIT_REQUEST_RE = re.compile(r"audit|审计|审查|审核|review|代码评估|架构评估", re.I)
EXPLICIT_AUDIT_DISPATCH_RE = re.compile(
    r"(?:dispatch|route|package|fan[- ]?out|delegate|分派|路由|打包|分发|分配给|交给).{0,80}"
    r"(?:audit|审计|审查|审核|review|subagent|reviewer)|"
    r"(?:audit|审计|审查|审核|review).{0,80}"
    r"(?:dispatch|route|package|fan[- ]?out|delegate|分派|路由|打包|分发|分配给|交给)",
    re.I,
)
ACCEPTED_SOURCE_RE = re.compile(
    r"已接受|accepted|accepted[- ]ready|ready[-_ ]?for[-_ ]?agent|"
    r"ready issue(?:s)?|ready task(?:s)?|ready work|ready package|任务已经确认",
    re.I,
)
DOWNSTREAM_MATERIAL_RE = re.compile(
    r"completed .{0,40}(?:package|result|review)|"
    r"(?:returned|return|返回).{0,40}(?:package|result|review)|"
    r"(?:result|review|implementation|clean[- ]?review|clean reviewer|child implementation|coordinator intake).{0,40}package|"
    r"(?:managed worktree|Codex App managed worktree|pendingWorktreeId|child thread|clean[- ]?review coordinator intake)",
    re.I,
)
DISPATCH_ACTION_RE = re.compile(
    r"\bdispatch\b|分派|运行时路由|runtime package|runtime route|Runtime Packages|"
    r"Dispatch Package|Result Package|Dispatch Runtime Decision|Dispatch Summary|"
    r"fan[- ]?out|clean[- ]?review fan[- ]?out|managed worktree|child thread|subagent|"
    r"model profile|reasoning selector|runtime|worktree|package",
    re.I,
)
WRITE_PLAN_RE = re.compile(r"\bwrite[- ]?plan\b|\bimplementation plan\b|实现计划|执行步骤|检查点|stop condition|只写.*计划", re.I)
PLAN_THEN_IMPLEMENT_RE = re.compile(
    r"(?:plan|计划).{0,50}(?:开始|直接|然后|随后|并|同时|现在).{0,20}(?:改|实现|修|patch|edit)|"
    r"(?:开始|直接|然后|随后|并|同时|现在).{0,20}(?:改|实现|修|patch|edit).{0,50}(?:plan|计划)",
    re.I,
)
IMPLEMENT_RE = re.compile(
    r"\bimplement\b|实施|实现|修复|改代码|按 PRD 实施|"
    r"直接\s*patch|patch|补丁|"
    r"修(?:这个|一下)?\s*(?:bug|问题)?|"
    r"(bug|问题).{0,12}(修|改|patch|补丁)",
    re.I,
)
IMPLEMENT_BYPASS_RE = re.compile(r"确认跳过|明确跳过|skip(?:ped)?\s+(?:PRD|planning|plan)", re.I)
SELF_REVIEW_CLEAN_REVIEW_QUESTION_RE = re.compile(
    r"(self[- ]?review|self[- ]?check|自查|自审|same[- ]?session|同一\s*session).{0,40}"
    r"(?:能不能|可不可以|可以|可否|是否|算不算|算|当|作为|吗|\\?)"
    r".{0,40}(clean[- ]?review|独立(?:审查|review|验证)|readiness|证据|evidence|验收)|"
    r"(clean[- ]?review|独立(?:审查|review|验证)).{0,40}"
    r"(?:能不能|可不可以|可以|可否|是否|算不算|算|当|作为|吗|\\?)"
    r".{0,40}(self[- ]?review|self[- ]?check|自查|自审|same[- ]?session|同一\s*session)",
    re.I,
)

ROUTE_MARKERS = [
    ("verify", re.compile(r"^Verification Scope\b|^验证范围\b", re.I | re.M)),
    ("handoff", re.compile(r"^\s*(?:#+\s*)?\*{0,2}(?:handoff(?:\s+package)?|交接)\*{0,2}\b", re.I | re.M)),
    (
        "implement",
        re.compile(
            r"^Implementation Summary\b|^Blocked Implementation\b|^Implementation Blocked\b|"
            r"^实现受阻\b|^阻塞实现\b|^实现摘要\b|"
            r"^Scope:\s|^Acceptance Map:\s|^Evidence Inspected:\s|^Findings P0/P1/P2:\s",
            re.I | re.M,
        ),
    ),
    (
        "write-plan",
        re.compile(
            r"^Implementation Mini-Plan\b|^Implementation Plan\b|"
            r"^\s*(?:#+\s*)?\*{0,2}(?:实现计划|可执行 plan|模板级 plan)\*{0,2}\b|"
            r"^\s*计划[:：]",
            re.I | re.M,
        ),
    ),
    (
        "triage",
        re.compile(
            r"^\s*(?:#+\s*)?\*{0,2}Triage(?: Verdict)?\*{0,2}\b|^State Transition\b|"
            r"^(?:State|Status|Decision|状态|决策|Next State)\s*[:：].*"
            r"(?:ready-for-agent|needs-info|AFK|HITL|blocked)",
            re.I | re.M,
        ),
    ),
    (
        "to-prd",
        re.compile(
            r"^# PRD\b|^# Compact PRD\b|\bCompact PRD\b|压缩版 PRD/spec|Artifact Type:\s*PRD|产品需求|"
            r"^\s*(?:Recommended route|Route|Owner|Expected route)\s*[:：].*\bto-prd\b|"
            r"(?:raw/draft intent|raw intent|draft intent).{0,80}(?:应先走|先走|route(?:s)? to).{0,40}\bto-prd\b|"
            r"\braw idea\b.{0,80}(?:not issue-ready|to-prd|accepted source)|"
            r"\bnot issue-ready\b|不是 accepted PRD/spec/plan|"
            r"(?:没有给出|只有|仅有).{0,30}新功能想法|"
            r"新功能想法.{0,80}(?:accepted source|不能拆|还不能拆|先走)",
            re.I | re.M,
        ),
    ),
    (
        "to-issues",
        re.compile(
            r"^\s*(?:#+\s*)?\*{0,2}(?:Issue Map|Issue Drafts?)\*{0,2}\b|"
            r"^\s*(?:#+\s*)?\*{0,2}Acceptance Criteria\*{0,2}\b|"
            r"\bissue drafts?\b|tracker-neutral issue drafts",
            re.I | re.M,
        ),
    ),
    ("prototype", re.compile(r"prototype|原型", re.I)),
    ("wiki", re.compile(r"LLM Wiki|wiki update candidate|项目 wiki", re.I)),
]

PROMPT_ROUTE_MARKERS = [
    ("handoff", re.compile(r"handoff|交接|续上|保存状态", re.I)),
    (
        "verify",
        re.compile(
            r"\bverify\b|验证|ready|就绪|UAT|release|发布|"
            + EVIDENCE_BOUNDARY_QUESTION_PATTERN
            + r"|"
            r"(self[- ]?review|self[- ]?check|自查|自审|same[- ]?session|同一\s*session).{0,30}"
            r"(clean[- ]?review|独立(?:审查|review|验证)|readiness|证据|evidence|验收)|"
            r"(clean[- ]?review|独立(?:审查|review|验证)).{0,30}"
            r"(self[- ]?review|self[- ]?check|自查|自审|same[- ]?session|同一\s*session)",
            re.I,
        ),
    ),
    ("write-plan", re.compile(r"\bplan\b|计划|实现计划|先别写代码|不要编辑文件", re.I)),
    (
        "implement",
        re.compile(
            r"\bimplement\b|实施|实现|修复|改代码|按 PRD 实施|"
            r"直接\s*patch|patch|补丁|"
            r"修(?:这个|一下)?\s*(?:bug|问题)?|"
            r"(bug|问题).{0,12}(修|改|patch|补丁)",
            re.I,
        ),
    ),
    ("to-issues", re.compile(r"拆\s*issues?|拆任务|issue-map|任务切片", re.I)),
    ("to-prd", re.compile(r"\bPRD\b|需求|产品方案|新需求", re.I)),
    ("triage", re.compile(r"triage|判断能不能|是否适合|阻塞", re.I)),
    ("prototype", re.compile(r"prototype|原型", re.I)),
    ("wiki", re.compile(r"wiki|知识库", re.I)),
]

GIT_WRITE_RE = re.compile(r"\bgit\s+(add|commit|push|reset|checkout|switch|clean|merge|rebase)\b")
FILE_WRITE_RE = re.compile(r"\b(apply_patch|cat\s*>|tee\s+|python\d?\s+.*write_text|rm\s+)", re.I)
TEST_RE = re.compile(r"\b(pytest|unittest|npm\s+test|pnpm\s+test|go\s+test|cargo\s+test|mvn\s+test)\b", re.I)
GIT_STATUS_RE = re.compile(r"\bgit\s+status\b|\bgit\s+diff\b", re.I)


def normalize_route(value):
    route = str(value or "").strip()
    return route if route in WORKFLOW_ROUTES else UNKNOWN_ROUTE


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if "|" in text:
        return [part.strip() for part in text.split("|") if part.strip()]
    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]
    return [text]


def first_nonempty_line(text):
    return next((line.strip() for line in str(text or "").splitlines() if line.strip()), "")


def has_anchored_dispatch_marker(text):
    first = first_nonempty_line(text)
    if first == "dispatch_version: 2":
        return True
    anchored_marker = re.compile(
        r"^\s*(?:#+\s*)?\*{0,2}"
        r"(?:Dispatch Summary|Dispatch Package|Result Package|Dispatch Runtime Decision|Dispatch Candidate)"
        r"\*{0,2}\b",
        re.I,
    )
    return bool(anchored_marker.search(first))


def has_legacy_dispatch_shape(text):
    value = str(text or "")
    first = first_nonempty_line(value)
    first_marker = re.sub(r"^[#*\s]+|[*\s]+$", "", first).lower()
    if first_marker.startswith("package-only runtime routing"):
        lowered = value.lower()
        return (
            "dispatch_version: 2" in lowered
            or "runtime packages" in lowered
            or "expected result package" in lowered
            or "dispatch summary" in lowered
            or "dispatch packages" in lowered
        )
    lowered = value.lower()
    if "dispatch_version: 2" in lowered:
        compact_schema_markers = ["adapter_completeness", "source:", "tasks:", "policy:"]
        if all(marker in lowered for marker in compact_schema_markers):
            return True
        schema_markers = [
            "adapter_completeness",
            "runtime_policy",
            "dispatch_native_alignment",
            "runtime_package",
            "result_package_expected",
        ]
        return sum(1 for marker in schema_markers if marker in lowered) >= 2
    if "pendingworktreeid" in lowered:
        topology_markers = ["managed worktree", "child thread", "worktree path", "manual fallback"]
        blocked_markers = ["blocked", "human_decision", "fallback", "不能继续", "无法继续", "不能在", "缺少"]
        return any(marker in lowered for marker in topology_markers) and any(
            marker in lowered for marker in blocked_markers
        )
    if "managed worktree" in lowered and "child thread" in lowered:
        gap_markers = [
            "non-readiness boundary",
            "source truth",
            "not git",
            "not a git repository",
            "missing",
            "还缺",
            "缺至少",
            "无法继续",
        ]
        blocked_markers = ["blocked", "human_decision", "cannot continue", "无法继续", "不能继续"]
        no_change_markers = ["changed files:\n无", "changed files:\r\n无", "无。"]
        return (
            any(marker in lowered for marker in gap_markers)
            and any(marker in lowered for marker in blocked_markers)
            and any(marker in lowered for marker in no_change_markers)
        )
    lifecycle_decision_markers = [
        "clean_review_pending",
        "needs_remediation",
        "low_risk_coordinator_intake",
        "merge_pending",
        "discard_pending",
        "branch_cleanup_pending",
    ]
    lifecycle_context_markers = [
        "managed worktree",
        "child package",
        "child implementation package",
        "returned package",
        "coordinator intake",
        "clean reviewer package",
        "clean-review package",
        "clean review package",
    ]
    lifecycle_action_markers = [
        "route this",
        "route it",
        "routed to",
        "correct lifecycle decision",
        "should be rejected",
        "must not be promoted",
        "fan-out",
        "fan out",
    ]
    if (
        any(marker in lowered for marker in lifecycle_decision_markers)
        and any(marker in lowered for marker in lifecycle_context_markers)
        and any(marker in lowered for marker in lifecycle_action_markers)
    ):
        return True
    if (
        "recommended coordinator response" in lowered
        and "package" in lowered
        and "fresh clean review" in lowered
        and ("partial validation" in lowered or "validation-fix" in lowered)
    ):
        return True
    if (
        "dispatch" in lowered
        and ("dispatch package" in lowered or "dispatch-package.md" in lowered or "dispatch package v2" in lowered)
        and (
            "blocked at intake" in lowered
            or "requires named source truth" in lowered
            or "accepted ready task artifact" in lowered
            or "ready task artifact" in lowered
            or "stop condition applies" in lowered
        )
        and (
            "did not create files" in lowered
            or "no files were changed" in lowered
            or "no ready task artifacts" in lowered
            or "without executing" in lowered
        )
    ):
        return True
    return False


def has_dispatch_route_marker(text):
    return has_anchored_dispatch_marker(text) or has_legacy_dispatch_shape(text)


def detect_route_from_text(text):
    value = str(text or "")
    if has_anchored_dispatch_marker(value):
        return "dispatch", "final_message_marker"
    for route, pattern in ROUTE_MARKERS:
        if pattern.search(value):
            return route, "final_message_marker"
    if has_legacy_dispatch_shape(value):
        return "dispatch", "final_message_marker"
    if value.strip():
        return DIRECT_ROUTE, "final_message_marker"
    return UNKNOWN_ROUTE, "unknown"


def is_direct_plain_text(value):
    return bool(DIRECT_PLAIN_TEXT_RE.search(value) or CONCEPT_EXPLANATION_RE.search(value)) and not (
        EVIDENCE_BOUNDARY_QUESTION_RE.search(value)
    )


def is_raw_or_planmode_prd_intake(value):
    if ACCEPTED_SOURCE_RE.search(value) or is_implement_bypass(value):
        return False
    return bool(PLANMODE_PRD_RE.search(value) or RAW_DELEGATION_RE.search(value))


def is_evidence_boundary_verify(value):
    return bool(
        EVIDENCE_BOUNDARY_QUESTION_RE.search(value)
        or SELF_REVIEW_CLEAN_REVIEW_QUESTION_RE.search(value)
    )


def is_dispatch_ready_package_cue(value):
    return bool(
        DISPATCH_ACTION_RE.search(value)
        and (ACCEPTED_SOURCE_RE.search(value) or DOWNSTREAM_MATERIAL_RE.search(value))
    )


def is_implement_bypass(value):
    return bool(IMPLEMENT_BYPASS_RE.search(value) and IMPLEMENT_RE.search(value))


def is_existing_issue_readiness(value):
    if is_dispatch_ready_package_cue(value):
        return False
    return bool(EXISTING_ISSUE_READINESS_RE.search(value))


def is_closeout_decision(value):
    if re.search(r"^\s*(?:验证|verify).{0,50}(?:是否|能不能|can).{0,30}(?:通过|pass)", str(value or ""), re.I):
        return False
    return bool(CLOSEOUT_DECISION_RE.search(value))


def is_explicit_audit_dispatch(value):
    return bool(AUDIT_REQUEST_RE.search(value) and EXPLICIT_AUDIT_DISPATCH_RE.search(value))


def is_ordinary_audit_request(value):
    return bool(
        AUDIT_REQUEST_RE.search(value)
        and not is_explicit_audit_dispatch(value)
        and not is_evidence_boundary_verify(value)
        and not IMPLEMENT_RE.search(value)
    )


def is_plan_then_implement(value):
    return bool(WRITE_PLAN_RE.search(value) and IMPLEMENT_RE.search(value) and PLAN_THEN_IMPLEMENT_RE.search(value))


def fallback_prompt_route(value):
    for candidate, pattern in PROMPT_ROUTE_MARKERS:
        if pattern.search(value):
            return candidate
    return None


def prompt_route(value):
    if not str(value or "").strip():
        return UNKNOWN_ROUTE
    rules = {
        "direct_plain_text": lambda: DIRECT_ROUTE if is_direct_plain_text(value) else None,
        "implement_bypass": lambda: "implement" if is_implement_bypass(value) else None,
        "raw_prd_intake": lambda: "to-prd" if is_raw_or_planmode_prd_intake(value) else None,
        "handoff": lambda: "handoff" if re.search(r"handoff|交接|续上|保存状态", value, re.I) else None,
        "closeout_triage": lambda: "triage" if is_closeout_decision(value) else None,
        "plan_then_implement": lambda: "implement" if is_plan_then_implement(value) else None,
        "ordinary_audit_direct": lambda: DIRECT_ROUTE if is_ordinary_audit_request(value) else None,
        "evidence_verify": lambda: "verify" if is_evidence_boundary_verify(value) else None,
        "write_plan": lambda: "write-plan" if WRITE_PLAN_RE.search(value) else None,
        "issue_readiness_triage": lambda: "triage" if is_existing_issue_readiness(value) else None,
        "explicit_audit_dispatch": lambda: "dispatch" if is_explicit_audit_dispatch(value) else None,
        "ready_package_dispatch": lambda: "dispatch" if is_dispatch_ready_package_cue(value) else None,
        "implement": lambda: "implement" if IMPLEMENT_RE.search(value) else None,
        "fallback_markers": lambda: fallback_prompt_route(value),
        "direct_fallback": lambda: DIRECT_ROUTE,
    }
    unknown_rules = [rule for rule in PROMPT_PRECEDENCE if rule not in rules]
    if unknown_rules:
        raise ValueError(f"unknown prompt precedence rules: {unknown_rules}")
    for rule_name in PROMPT_PRECEDENCE:
        route = rules[rule_name]()
        if route is not None:
            return route
    return DIRECT_ROUTE


def entry_decision_from_prompt(prompt):
    value = str(prompt or "")
    route = prompt_route(value)

    acceptable = [route] if route != UNKNOWN_ROUTE else []
    forbidden = list(DEFAULT_FORBIDDEN_ROUTES.get(route, []))

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


__all__ = [
    "CLASSIFIER_SOURCE_PATH",
    "ROUTE_REGISTRY_PATH",
    "ROUTE_REGISTRY",
    "PROMPT_PRECEDENCE",
    "DEFAULT_FORBIDDEN_ROUTES",
    "PUBLIC_SKILL_ROUTES",
    "DIRECT_ROUTE",
    "UNKNOWN_ROUTE",
    "HOST_PREEMPTION_ROUTE",
    "WORKFLOW_ROUTES",
    "normalize_route",
    "as_list",
    "detect_route_from_text",
    "has_anchored_dispatch_marker",
    "has_legacy_dispatch_shape",
    "has_dispatch_route_marker",
    "entry_decision_from_prompt",
    "classify_command",
    "risk_markers",
    "evidence_markers",
]
