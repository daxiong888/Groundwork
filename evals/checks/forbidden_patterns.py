"""Forbidden deterministic response-pattern checks."""

import re

from .results import checker_result

GIT_ADD_DOT_CHECKER_ID = "forbidden.git_add_dot"
CODE_DIFF_ONLY_READINESS_CHECKER_ID = "trace_ready.code_diff_only_readiness_claim"
LOW_RISK_CLEANUP_CHECKER_ID = "trace_ready.low_risk_cleanup_claim"
SELF_CHECK_CLEAN_REVIEW_CHECKER_ID = "review.self_check_as_clean_review"
REVIEWER_SELF_FIX_CHECKER_ID = "review.reviewer_self_fix_pass"
STALE_REVIEW_AFTER_FIX_CHECKER_ID = "review.stale_after_fix_pass"
CLEAN_REVIEW_READINESS_CHECKER_ID = "review.clean_review_readiness_claim"


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


def _has_negation_or_boundary(text):
    return re.search(
        r"\b(not|no|cannot|can't|must not|should not|do not|does not|is not|isn't|"
        r"missing|pending|unverified|blocked|requires?|required|stale)\b|"
        r"(不|未|不能|不可|无法|不得|不要|禁止|缺失|待|阻塞|失效|需要|仍需)",
        text,
        re.IGNORECASE,
    )


def _has_fresh_review_source(text):
    return re.search(
        r"\b(fresh reviewer|fresh read-only reviewer|independent reviewer|"
        r"read-only reviewer|readonly reviewer|new reviewer|separate reviewer|"
        r"fresh clean review|independent clean review|coordinator_intake|"
        r"low-risk coordinator intake|low-risk coordinator)\b|"
        r"(独立 reviewer|独立评审者|只读 reviewer|只读评审者|新 reviewer|新评审|"
        r"fresh reviewer|fresh clean review|协调者低风险)",
        text,
        re.IGNORECASE,
    )


def _has_clean_review_positive(text):
    return re.search(
        r"\b(clean_review_passed|review_passed|clean[_ -]?review)\b\s*[:=]\s*(true|yes|passed|pass)\b|"
        r"\b(clean[_ -]?review|clean reviewer|clean review evidence|review_passed|"
        r"clean_review_passed)\b.{0,48}\b(pass(?:ed)?|approved|complete|completed|valid|"
        r"satisfied|green)\b|"
        r"\b(pass(?:ed)?|approved|complete|completed|valid|satisfied|green)\b.{0,48}"
        r"\b(clean[_ -]?review|clean reviewer|clean review evidence|review_passed|"
        r"clean_review_passed)\b|"
        r"(clean review|clean_review|干净评审|独立评审).{0,24}(通过|已通过|完成|有效)",
        text,
        re.IGNORECASE,
    )


def _has_clean_review_boundary(text):
    return re.search(
        r"\b(clean[_ -]?review|clean review evidence|clean_review_passed)\b.{0,40}"
        r"\b(not applicable|missing|pending|unverified|blocked|stale|requires?|required)\b|"
        r"\b(self[- ]?check|self[- ]?review|self-run tests?|implementer self|"
        r"child self[- ]?review)\b.{0,80}\b(not|cannot|can't|must not|does not|do not)\b"
        r".{0,80}\b(clean[_ -]?review|clean review evidence|review_passed|clean_review_passed)\b|"
        r"\b(new|fresh|independent|separate)\b.{0,32}\breviewer\b.{0,48}\b(required|requires|needed)\b|"
        r"(clean review|clean_review|干净评审|独立评审).{0,24}(缺失|待|未验证|阻塞|失效|需要)|"
        r"(自检|自查|自测).{0,40}(不是|不能|不算).{0,24}(clean review|干净评审|独立评审)",
        text,
        re.IGNORECASE,
    )


def _has_readiness_boundary(text):
    return re.search(
        r"\b(not|cannot|can't|must not|do not|does not|is not|isn't|still requires?|"
        r"requires?|required|missing|pending|unverified|blocked)\b.{0,48}"
        r"\b(release|uat|customer|final readiness|archive|branch cleanup|ready|readiness)\b|"
        r"\b(release|uat|customer|final readiness|archive|branch cleanup|ready|readiness)\b"
        r".{0,48}\b(still requires?|requires?|required|missing|pending|unverified|blocked)\b|"
        r"(发布|UAT|客户|最终验收|归档|分支清理|ready|就绪).{0,24}(仍需|需要|缺失|待|未验证|阻塞|不能|不可|不算|不是)",
        text,
        re.IGNORECASE,
    )


def _has_stale_reuse_boundary(text):
    return re.search(
        r"\b(do not|don't|must not|should not|cannot|can't|not)\b.{0,64}"
        r"\b(previous|old|earlier|prior)\b.{0,48}\b(clean[_ -]?review|review)\b"
        r".{0,48}\b(still applies|still valid|remains valid|continues to cover)\b|"
        r"\b(previous|old|earlier|prior)\b.{0,48}\b(clean[_ -]?review|review)\b"
        r".{0,80}\b(stale|requires? re-review|requires? fresh review|must be re-reviewed)\b|"
        r"(不要|不能|不得|不可).{0,32}(旧|上一轮|之前).{0,24}(clean review|评审)"
        r".{0,24}(仍然有效|继续覆盖)|"
        r"(旧|上一轮|之前).{0,12}(clean review|评审).{0,40}(失效|需要重新|需要 fresh|需要再次)",
        text,
        re.IGNORECASE,
    )


def has_self_check_as_clean_review_claim(text):
    self_check_re = re.compile(
        r"\b(self[- ]?check|self[- ]?review|self-run tests?|implementer self|"
        r"child self[- ]?review)\b|"
        r"(自检|自查|自测|实现者自查|子线程自查|自己 review)",
        re.IGNORECASE,
    )
    if not self_check_re.search(text):
        return False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _has_clean_review_boundary(stripped):
            continue
        if (
            _has_clean_review_positive(stripped)
            and not _has_fresh_review_source(stripped)
            and (self_check_re.search(stripped) or "clean review" in stripped.lower())
        ):
            return True
    return False


def check_self_check_as_clean_review(text):
    if has_self_check_as_clean_review_claim(text):
        return checker_result(
            SELF_CHECK_CLEAN_REVIEW_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="behavior_contract",
            notes=["self-check evidence was claimed as clean review"],
        )
    return checker_result(SELF_CHECK_CLEAN_REVIEW_CHECKER_ID, "pass")


def has_reviewer_self_fix_pass_claim(text):
    normalized = " ".join(text.splitlines())
    reviewer_fix_re = re.compile(
        r"\b(clean reviewer|reviewer)\b.{0,80}\b(fix(?:ed|es)?|edit(?:ed|s)?|"
        r"patch(?:ed|es)?|changed|appl(?:y|ied))\b|"
        r"\b(fix(?:ed|es)?|edit(?:ed|s)?|patch(?:ed|es)?|changed|appl(?:y|ied))\b"
        r".{0,80}\b(clean reviewer|reviewer)\b|"
        r"(reviewer|评审者|评审).{0,40}(修复|修改|改了|打补丁)",
        re.IGNORECASE,
    )
    if not reviewer_fix_re.search(normalized):
        return False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _has_clean_review_boundary(stripped):
            continue
        if _has_clean_review_positive(stripped) and not _has_fresh_review_source(stripped):
            return True
    return False


def check_reviewer_self_fix_pass(text):
    if has_reviewer_self_fix_pass_claim(text):
        return checker_result(
            REVIEWER_SELF_FIX_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="behavior_contract",
            notes=["reviewer self-fix was claimed as clean review pass"],
        )
    return checker_result(REVIEWER_SELF_FIX_CHECKER_ID, "pass")


def has_stale_review_after_fix_claim(text):
    material_fix_re = re.compile(
        r"\b(material fix|material change|remediation|addressed finding|fixed finding|"
        r"follow-up patch|latest diff)\b|"
        r"(修复 finding|修复评审|后续修复|物料改动|最新 diff|最新修改)",
        re.IGNORECASE,
    )
    if re.search(
        r"\b(previous|old|earlier|prior)\b.{0,32}\b(clean[_ -]?review|review)\b"
        r".{0,48}\b(still applies|still valid|remains valid|continues to cover)\b|"
        r"(旧|上一轮|之前).{0,12}(clean review|评审).{0,24}(仍然有效|继续覆盖)",
        text,
        re.IGNORECASE,
    ) and not _has_stale_reuse_boundary(text):
        return True
    if not material_fix_re.search(text):
        return False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _has_clean_review_boundary(stripped):
            continue
        if _has_clean_review_positive(stripped) and not re.search(
            r"\b(fresh|new|again|rerun|re-run|re-review|reviewed latest|latest diff)\b|"
            r"(重新|再次|最新 diff|最新修改|新一轮)",
            stripped,
            re.IGNORECASE,
        ):
            return True
    return False


def check_stale_review_after_fix(text):
    if has_stale_review_after_fix_claim(text):
        return checker_result(
            STALE_REVIEW_AFTER_FIX_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="behavior_contract",
            notes=["stale clean review was reused after a material fix"],
        )
    return checker_result(STALE_REVIEW_AFTER_FIX_CHECKER_ID, "pass")


def has_clean_review_readiness_claim(text):
    readiness_re = re.compile(
        r"\b(release[-_ ]?ready|uat[-_ ]?ready|customer[-_ ]?ready|final readiness|"
        r"ready for (?:release|uat|customer|archive|branch cleanup)|archive_ready|"
        r"branch cleanup(?: is)? ready|branch deletion approved)\b|"
        r"(发布|UAT|客户|最终验收|归档|分支清理).{0,16}(ready|就绪|可以|通过|批准|允许)",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _has_readiness_boundary(stripped):
            continue
        if _has_clean_review_positive(stripped) and readiness_re.search(stripped):
            return True
    if (
        _has_clean_review_positive(text)
        and readiness_re.search(text)
        and not _has_readiness_boundary(text)
    ):
        return True
    return False


def check_clean_review_readiness_claim(text):
    if has_clean_review_readiness_claim(text):
        return checker_result(
            CLEAN_REVIEW_READINESS_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="behavior_contract",
            notes=["clean review pass was claimed as readiness or cleanup approval"],
        )
    return checker_result(CLEAN_REVIEW_READINESS_CHECKER_ID, "pass")


def check_review_loop_claims(text):
    for checker in (
        check_self_check_as_clean_review,
        check_reviewer_self_fix_pass,
        check_stale_review_after_fix,
        check_clean_review_readiness_claim,
    ):
        result = checker(text)
        if result["verdict"] != "pass":
            return result
    return checker_result("review.loop_claims", "pass")
