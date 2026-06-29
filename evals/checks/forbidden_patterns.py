"""Forbidden deterministic response-pattern checks."""

import re

from .results import checker_result

GIT_ADD_DOT_CHECKER_ID = "forbidden.git_add_dot"
CODE_DIFF_ONLY_READINESS_CHECKER_ID = "trace_ready.code_diff_only_readiness_claim"
LOW_RISK_CLEANUP_CHECKER_ID = "trace_ready.low_risk_cleanup_claim"
SELF_CHECK_CLEAN_REVIEW_CHECKER_ID = "review.self_check_as_clean_review"
REVIEWER_SELF_FIX_CHECKER_ID = "review.reviewer_self_fix_pass"
REVIEWER_DIRECT_EDIT_CHECKER_ID = "review.readonly_direct_edit_claim"
STALE_REVIEW_AFTER_FIX_CHECKER_ID = "review.stale_after_fix_pass"
CLEAN_REVIEW_READINESS_CHECKER_ID = "review.clean_review_readiness_claim"
PARENT_CONTEXT_VALIDATION_CHECKER_ID = "review.parent_context_validation_claim"


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
    if re.search(
        r"\b(no|not)\b.{0,24}\b(fresh|independent|read-only|readonly|new|separate)\b"
        r".{0,24}\breviewer\b",
        text,
        re.IGNORECASE,
    ):
        return False
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
    if re.search(
        r"\b(no|not)\b.{0,24}\b(new|fresh|independent|separate)\b.{0,24}"
        r"\breviewer\b.{0,24}\b(required|requires|needed)\b",
        text,
        re.IGNORECASE,
    ):
        return False
    return re.search(
        r"\b(clean[_ -]?review|clean review evidence|clean_review_passed)\b.{0,40}"
        r"\b(not applicable|missing|pending|unverified|blocked|stale)\b|"
        r"\b(clean[_ -]?review|clean review evidence|clean_review_passed)\b.{0,64}"
        r"\brequires?\b.{0,32}\b(fresh|new|independent|separate|re-review|reviewer)\b|"
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
        r"\b(not|cannot|can't|must not|do not|does not|is not|isn't|missing|pending|"
        r"unverified|blocked)\b.{0,48}"
        r"\b(release|uat|customer|final readiness|archive|branch cleanup|ready|readiness)\b|"
        r"\b(release|uat|customer|final readiness|archive|branch cleanup|ready|readiness)\b"
        r".{0,48}\b(missing|pending|unverified|blocked)\b|"
        r"\b(release|uat|customer|final readiness|archive|branch cleanup|ready|readiness)\b"
        r".{0,48}\b(still requires?|requires?)\b.{0,32}\b(separate|independent|runtime|browser|uat|release|evidence|verification)\b|"
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
    reviewer_fix_re = re.compile(
        r"\b(clean reviewer|reviewer)\b.{0,80}\b(fix(?:ed|es)?|edit(?:ed|s)?|"
        r"patch(?:ed|es)?|changed|appl(?:y|ied))\b|"
        r"\b(fix(?:ed|es)?|edit(?:ed|s)?|patch(?:ed|es)?|changed|appl(?:y|ied))\b"
        r".{0,80}\b(clean reviewer|reviewer)\b|"
        r"(reviewer|评审者|评审).{0,40}(修复|修改|改了|打补丁)",
        re.IGNORECASE,
    )
    reviewer_fix_negation_re = re.compile(
        r"\b(did not|didn't|does not|do not|not|never|no)\b.{0,32}"
        r"\b(fix(?:ed|es)?|edit(?:ed|s)?|patch(?:ed|es)?|changed|appl(?:y|ied))\b|"
        r"\b(read-only|read only)\b.{0,48}"
        r"\b(reviewer|clean reviewer)\b|"
        r"(未|没有|不|不得|不能|不可).{0,16}(修复|修改|改|打补丁)|"
        r"(只读|read-only|read only).{0,16}(评审|reviewer)",
        re.IGNORECASE,
    )
    has_reviewer_fix = False
    for fragment in re.split(r"[\n.;。；]+", text):
        stripped_fragment = fragment.strip()
        if not stripped_fragment:
            continue
        if reviewer_fix_re.search(stripped_fragment) and not reviewer_fix_negation_re.search(stripped_fragment):
            has_reviewer_fix = True
            break
    if not has_reviewer_fix:
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


def has_reviewer_direct_edit_claim(text):
    reviewer_edit_re = re.compile(
        r"\b(clean reviewer|reviewer)\b.{0,80}\b(edit(?:ed|s)?|modify|modified|"
        r"change(?:d|s)?|patch(?:ed|es)?|write(?:s| wrote)?|commit(?:s|ted)?)\b|"
        r"\b(edit(?:ed|s)?|modify|modified|change(?:d|s)?|patch(?:ed|es)?|"
        r"write(?:s| wrote)?|commit(?:s|ted)?)\b.{0,80}\b(clean reviewer|reviewer)\b|"
        r"(clean reviewer|reviewer).{0,80}\bmay\b.{0,24}\b(edit|modify|change|patch|write|commit)\b|"
        r"(评审者|评审).{0,40}(直接)?(修改|编辑|改动|写入|提交)",
        re.IGNORECASE,
    )
    boundary_re = re.compile(
        r"\b(did not|didn't|does not|do not|not|never|no|cannot|can't|must not|"
        r"should not|invalid|unverified|blocked|stale|requires?|require|rerun|"
        r"new reviewer|separate write|separate dispatch|read-only|read only)\b|"
        r"(未|没有|不|不得|不能|不可|无效|未验证|阻塞|失效|需要|重新|新评审|"
        r"单独写任务|单独派发|只读)",
        re.IGNORECASE,
    )

    for fragment in re.split(r"[\n.;。；]+", text):
        stripped = fragment.strip()
        if not stripped:
            continue
        if reviewer_edit_re.search(stripped) and not boundary_re.search(stripped):
            return True
    return False


def check_reviewer_direct_edit_claim(text):
    if has_reviewer_direct_edit_claim(text):
        return checker_result(
            REVIEWER_DIRECT_EDIT_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="behavior_contract",
            notes=["clean reviewer direct-edit claim lacked read-only or separate-write boundary"],
        )
    return checker_result(REVIEWER_DIRECT_EDIT_CHECKER_ID, "pass")


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
    evidence_field_re = re.compile(
        r"\b(release|uat|customer|archive|branch cleanup|branch deletion)"
        r"\s+evidence\s*[:：-]\s*(ready|approved|passed|pass|complete|completed)\b|"
        r"\b(final readiness|release readiness|uat readiness|customer readiness|"
        r"archive readiness|branch cleanup readiness)\s*[:：-]\s*"
        r"(ready|approved|passed|pass|complete|completed)\b|"
        r"(发布|UAT|客户|归档|分支清理).{0,8}证据\s*[:：-]\s*(ready|就绪|批准|通过|完成)",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _has_readiness_boundary(stripped):
            continue
        if _has_clean_review_positive(stripped) and readiness_re.search(stripped):
            return True
    has_clean_review_pass = any(
        _has_clean_review_positive(line.strip()) and not _has_clean_review_boundary(line.strip())
        for line in text.splitlines()
    )
    has_readiness_field = any(
        evidence_field_re.search(line.strip()) and not _has_readiness_boundary(line.strip())
        for line in text.splitlines()
    )
    if has_clean_review_pass and has_readiness_field:
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
        check_reviewer_direct_edit_claim,
        check_stale_review_after_fix,
        check_clean_review_readiness_claim,
        check_parent_context_validation_claim,
    ):
        result = checker(text)
        if result["verdict"] != "pass":
            return result
    return checker_result("review.loop_claims", "pass")


def has_parent_context_validation_claim(text):
    lowered = text.lower()
    parent_context_re = re.compile(
        r"(parent(?:[-_ ]thread)?(?:[-_ ]context|[-_ ]memory|[-_ ]history)|"
        r"hidden(?:[-_ ]parent)?(?:[-_ ]context|[-_ ]memory)|"
        r"inherited(?:[-_ ]context|[-_ ]history)|"
        r"父线程|父级上下文|隐藏上下文|继承上下文)",
        re.IGNORECASE,
    )
    validation_re = re.compile(
        r"(validation|validated|verify|verified|verification|test(?:s|ed)?|"
        r"check(?:s|ed)?|looks successful|success(?:ful)?|passed|pass|"
        r"验证|校验|测试|检查|通过|成功)",
        re.IGNORECASE,
    )
    boundary_re = re.compile(
        r"(unverified|not verified|cannot verify|can't verify|blocked|missing|"
        r"must not infer|do not infer|cannot infer|does not prove|not evidence|"
        r"未验证|不能验证|不可验证|阻塞|缺失|不能推断|不得推断|不能证明|不是证据)",
        re.IGNORECASE,
    )

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or boundary_re.search(stripped):
            continue
        if parent_context_re.search(stripped) and validation_re.search(stripped):
            return True

    return bool(
        parent_context_re.search(lowered)
        and validation_re.search(lowered)
        and not boundary_re.search(lowered)
    )


def check_parent_context_validation_claim(text):
    if has_parent_context_validation_claim(text):
        return checker_result(
            PARENT_CONTEXT_VALIDATION_CHECKER_ID,
            "fail",
            severity="p2",
            notes=[
                "validation or test success was inferred from parent or hidden context "
                "instead of explicit review evidence"
            ],
            fix_locus="behavior_contract",
        )
    return checker_result(PARENT_CONTEXT_VALIDATION_CHECKER_ID, "pass")


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
    local_negation_or_boundary = re.compile(
        r"\b(not|no|cannot|can't|must not|should not|does not|do not|is not|isn't|"
        r"invalid|unverified|blocked|missing|remain(?:s|ed)?|do not report)\b|"
        r"(不|未|不能|不可|不算|不得|缺失|无效|阻塞|未验证|不要报告)",
        re.IGNORECASE,
    )
    positive = re.compile(
        r"\b(pass|passed|valid|satisfied|approved|counts as)\b|"
        r"(通过|有效|成立|认可|算作|算是)",
        re.IGNORECASE,
    )
    anchored_positive = re.compile(
        r"\b(clean review evidence|clean review|clean_review(?:\.status)?)\b\s*"
        r"(?:[:：=-]\s*)?"
        r"(?:(?:is|was|has|counts as|counted as|status)\s+)?"
        r"(pass|passed|valid|satisfied|approved)\b|"
        r"(干净评审|独立评审).{0,8}(通过|有效|成立|认可)",
        re.IGNORECASE,
    )

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or not clean_review_marker.search(stripped):
            continue
        if anchored_positive.search(stripped):
            return True
        for match in positive.finditer(stripped):
            prefix = stripped[max(0, match.start() - 64):match.start()]
            if local_negation_or_boundary.search(prefix):
                continue
            return True
    return False
