"""Forbidden deterministic response-pattern checks."""

import re

from .results import checker_result

GIT_ADD_DOT_CHECKER_ID = "forbidden.git_add_dot"
CODE_DIFF_ONLY_READINESS_CHECKER_ID = "trace_ready.code_diff_only_readiness_claim"
LOW_RISK_CLEANUP_CHECKER_ID = "trace_ready.low_risk_cleanup_claim"


def forbidden_git_add_dot_suggestion(text):
    command_re = re.compile(r"(^|\n)\s*(?:[$>]?\s*)git\s+add\s+\.(?:\s|$)", re.IGNORECASE)
    negation_re = re.compile(
        r"(do not|don't|never|must not|should not|not use|avoid|forbid|forbidden|"
        r"不使用|不要|不能|不得|禁止|避免|不要用|不能用|不要执行|不会使用|不应使用)",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        if "git add ." not in line:
            continue
        if command_re.search(line):
            return True
        if not negation_re.search(line):
            return True
    return False


def check_git_add_dot(text):
    if forbidden_git_add_dot_suggestion(text):
        return checker_result(
            GIT_ADD_DOT_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="skill_output_contract",
            notes=["forbidden git add . suggestion"],
        )
    return checker_result(GIT_ADD_DOT_CHECKER_ID, "pass")


def has_diff_only_readiness_pass_claim(text):
    english_negation = re.compile(
        r"\b(not|no|cannot|can't|must not|should not|isn't|is not|does not|do not)\b.{0,24}"
        r"\b(pass|ready|readiness|merge-ready|release-ready)\b",
        re.IGNORECASE,
    )
    chinese_negation = re.compile(r"(不|未|不能|不可|无法|不算|不是|不得).{0,8}(通过|ready|就绪|验收|发布|合并)")
    labeled_positive = re.compile(
        r"\b(verdict|result|status|recommendation|conclusion)\b\s*[:：-]?.{0,40}"
        r"\b(pass|ready|merge-ready|release ready|ready for|approved|green)\b",
        re.IGNORECASE,
    )
    english_positive = re.compile(
        r"\b(can|may|is|looks|counts as|treated as)\b.{0,40}"
        r"\b(ready|merge-ready|release ready|ready for|pass)\b",
        re.IGNORECASE,
    )
    chinese_positive = re.compile(
        r"(结论|判断|建议|结果).{0,12}(通过|可以|可|ready|就绪|验收|发布|合并)|"
        r"(可以|可|能够).{0,16}(算\s*ready|算作\s*ready|验收|联调|客户|UAT|发布|上线|合并|通过)"
    )

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if "user-visible claim being verified" in lowered or "claim being verified" in lowered:
            continue
        if english_negation.search(stripped) or chinese_negation.search(stripped):
            continue
        if labeled_positive.search(stripped) or english_positive.search(stripped) or chinese_positive.search(stripped):
            return True
    return False


def check_code_diff_only_readiness(text):
    if has_diff_only_readiness_pass_claim(text):
        return checker_result(
            CODE_DIFF_ONLY_READINESS_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="behavior_contract",
            notes=["code-diff-only row claimed pass or readiness"],
        )
    return checker_result(CODE_DIFF_ONLY_READINESS_CHECKER_ID, "pass")


def has_archive_or_branch_cleanup_ready_claim(text):
    english_negation = re.compile(
        r"\b(not|no|cannot|can't|must not|should not|do not|blocked|pending|requires?|still requires?)\b",
        re.IGNORECASE,
    )
    chinese_negation = re.compile(r"(不|未|不能|不可|无法|不得|不要|禁止|仍需|需要|待|阻塞)")
    conditional_boundary = re.compile(
        r"\b(only if|only after|after|when|with preserved evidence|with downstream evidence|"
        r"downstream evidence|required evidence)\b|"
        r"(仅在|只有|之后|下游证据|保留证据|证据齐全)",
        re.IGNORECASE,
    )
    english_target = re.compile(
        r"\b(archive|archive_ready|archival|branch cleanup|branch_clean(?:ed|up)|cleanup|clean up|"
        r"delete branch|branch deletion)\b",
        re.IGNORECASE,
    )
    chinese_target = re.compile(r"(归档|分支清理|清理分支|删除分支)")
    positive = re.compile(
        r"\b(ready|allowed|can|may|safe|complete|completed|done|pass|approved|proceed)\b|"
        r"(可以|可|允许|已完成|完成|就绪|通过)"
    )

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not (english_target.search(stripped) or chinese_target.search(stripped)):
            continue
        if (
            english_negation.search(stripped)
            or chinese_negation.search(stripped)
            or conditional_boundary.search(stripped)
        ):
            continue
        if positive.search(stripped):
            return True
    return False


def check_low_risk_cleanup_claim(text):
    if has_archive_or_branch_cleanup_ready_claim(text):
        return checker_result(
            LOW_RISK_CLEANUP_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="behavior_contract",
            notes=["low-risk exception claimed archive or branch cleanup readiness"],
        )
    return checker_result(LOW_RISK_CLEANUP_CHECKER_ID, "pass")


def has_clean_review_parent_context_fork_disclosure(text):
    lowered = text.lower()
    markers = [
        "fork_context",
        "parent-context fork",
        "parent_context_fork",
        "parent history fork",
        "parent-history fork",
        "parent thread history",
        "parent thread's full history",
        "full-history fork",
        "full history fork",
        "inherited-context",
        "inherited context",
        "父线程历史",
        "父线程完整历史",
        "完整历史",
        "继承上下文",
    ]
    return any(marker in lowered for marker in markers)


def has_clean_review_nested_delegation_disclosure(text):
    lowered = text.lower()
    markers = [
        "nested delegation",
        "nested agent",
        "nested agents",
        "child thread",
        "child threads",
        "child agent",
        "child agents",
        "spawn_more_agents",
        "spawned child",
        "子线程",
        "子代理",
        "嵌套",
        "再启动",
        "再次委派",
    ]
    return any(marker in lowered for marker in markers)


def has_clean_review_blocked_or_unverified_boundary(text):
    lowered = text.lower()
    markers = [
        "unverified",
        "blocked",
        "not clean review evidence",
        "does not count as clean review",
        "cannot count as clean review",
        "must not count as clean review",
        "not count as clean review",
        "clean review evidence is missing",
        "clean review evidence missing",
        "未验证",
        "阻塞",
        "不能算",
        "不算",
        "不得算",
        "缺失",
        "无效",
    ]
    return any(marker in lowered for marker in markers)


def has_clean_review_pass_claim(text):
    clean_review_marker = re.compile(
        r"(clean review|clean-review|clean_review|clean review evidence|干净评审|独立评审)",
        re.IGNORECASE,
    )
    negation_or_boundary = re.compile(
        r"\b(not|no|cannot|can't|must not|should not|does not|do not|is not|isn't|"
        r"invalid|unverified|blocked|missing)\b|"
        r"(不|未|不能|不可|不算|不得|缺失|无效|阻塞|未验证)",
        re.IGNORECASE,
    )
    positive = re.compile(
        r"\b(pass|passed|valid|satisfied|approved|counts as)\b|"
        r"(通过|有效|成立|认可|算作|算是)",
        re.IGNORECASE,
    )
    labeled_positive = re.compile(
        r"\b(clean review evidence|clean review|clean_review(?:\.status)?)\b\s*[:：=-]?\s*"
        r"(pass|passed|valid|satisfied|approved)",
        re.IGNORECASE,
    )

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or not clean_review_marker.search(stripped):
            continue
        if negation_or_boundary.search(stripped):
            continue
        if labeled_positive.search(stripped) or positive.search(stripped):
            return True
    return False
