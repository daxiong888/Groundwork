"""Verify-related deterministic check constants."""

import re
import shlex

VERIFY_SCOPE_FIELDS = ["Claim", "Covered", "Missing"]
VERIFY_SCOPE_FIELD_ALIASES = {
    "Claim": ["Claim", "User-visible Claim Being Verified", "In Scope"],
    "Covered": ["Covered"],
    "Missing": ["Missing", "Not Covered"],
}


def missing_verify_scope_fields(text):
    scope, count = _verification_scope_block(text)
    if count != 1:
        return list(VERIFY_SCOPE_FIELDS)
    return [
        field
        for field, aliases in VERIFY_SCOPE_FIELD_ALIASES.items()
        if not any(
            any(value.strip() for value in _field_values(scope, alias))
            for alias in aliases
        )
    ]
QA_FAILURE_FIELDS = [
    "Expected",
    "Actual",
    "Reproduction",
    "Severity",
    "Minimal Diagnosis",
    "Evidence Delta",
    "Source / AC Change",
    "Implementation Authority",
    "Risk Change",
    "Fix Plan",
    "Gap-Closure Admission",
    "Gap Closure Plan",
    "Re-QA Required",
    "Regression Note",
    "Scoped Next Action",
]
QA_GAP_CLOSURE_STRUCTURED_FIELDS = tuple(QA_FAILURE_FIELDS)
ARTIFACT_HEADER_FIELDS = [
    "Target Reader",
    "Reader Action Needed",
    "Artifact Type",
    "Source of Truth",
    "Safe to Share / Redaction Notes",
]


QA_GAP_CLOSURE_ADMISSIONS = {
    "ready_for_implement",
    "diagnose_before_edit",
    "needs_info",
    "product_or_contract_rework",
    "human_decision",
    "blocked",
}
QA_GAP_CLOSURE_READY = {"ready_for_implement", "diagnose_before_edit"}
QA_IMPLEMENTATION_AUTHORITY_VALUES = {
    "existing_and_sufficient",
    "approval_required",
    "missing",
    "unverified",
}
QA_RISK_CHANGE_VALUES = {
    "unchanged_within_boundary",
    "new_or_increased",
    "unverified",
}
QA_SOURCE_AC_CHANGE_VALUES = {"unchanged", "changed", "unverified"}
QA_PLACEHOLDER_VALUES = {"", "not provided", "unverified", "unknown", "none", "n/a"}
QA_NO_EVIDENCE_DELTA_PATTERNS = (
    r"\bno new evidence\b",
    r"\bno evidence delta\b",
    r"^\s*same result and same hypothesis[.;]?\s*$",
    r"没有新证据",
    r"无新证据",
    r"无证据增量",
    r"证据(?:没有|无)变化",
)
QA_NON_ACTIONABLE_GAP_PLANS = {
    "source truth and acs are unchanged",
    "source truth and acceptance criteria are unchanged",
    "源事实和验收标准未变化",
}
QA_ACTIONABLE_GAP_PLAN_PATTERN = re.compile(
    r"\b(?:apply|change|fix|inspect|reproduce|rerun|re-run|review|scope|update|collect|capture|verify|remove|add|limit|trace)\b"
    r"|修改|修复|检查|复现|重跑|审查|限定|更新|收集|记录|验证|应用|删除|新增|限制|追踪",
    re.IGNORECASE,
)
QA_SCOPED_NEXT_ACTIONS = {
    "ready_for_implement": {"route: implement"},
    "diagnose_before_edit": {"route: implement"},
    "needs_info": {"route: verify"},
    "product_or_contract_rework": {"route: to-prd"},
    "human_decision": {"route: human_decision"},
    "blocked": {"route: stop", "route: triage"},
}
QA_CHANGED_HYPOTHESIS_MARKERS = (
    "changed hypothesis",
    "change hypothesis",
    "hypothesis changed",
    "new hypothesis",
    "改变假设",
    "更改假设",
    "调整假设",
    "新假设",
    "假设改为",
)
QA_SCOPE_ACTION_VARIANT = r"(?:patch(?:ed|ing)?|fix(?:ed|ing)?|edit(?:ed|ing)?|rewrit(?:e|ten|ing)|chang(?:e|ed|ing)|modif(?:y|ied|ying)|touch(?:ed|ing)?|updat(?:e|ed|ing)|refactor(?:ed|ing)?|remov(?:e|ed|ing)|replac(?:e|ed|ing))"
QA_SCOPE_ACTION_PAST = r"(?:patched|fixed|edited|rewritten|changed|modified|touched|updated|refactored|removed|replaced)"
QA_BROAD_SCOPE_PATTERNS = (
    rf"\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\b(?:every|all)\b.{{0,24}}\b(?:modules?|files?|components?|services?|packages?|layers?)\b",
    rf"\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\b(?:the\s+)?(?:whole|entire)\b.{{0,20}}\b(?:repository|repo|codebase|system|project)\b",
    rf"\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\beverything\b",
    rf"\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\bunrelated\b.{{0,20}}\b(?:modules?|files?|components?|services?|packages?|layers?)\b",
    rf"\b(?:every|all)\b.{{0,24}}\b(?:modules?|files?|components?|services?|packages?|layers?)\b.{{0,40}}\b(?:(?:must|should|will|would|can|could)\s+be|(?:is|are|was|were)(?:\s+being)?)\s+{QA_SCOPE_ACTION_PAST}\b",
    rf"\b(?:the\s+)?(?:whole|entire)\b.{{0,20}}\b(?:repository|repo|codebase|system|project)\b.{{0,40}}\b(?:(?:must|should|will|would|can|could)\s+be|(?:is|are|was|were)(?:\s+being)?)\s+{QA_SCOPE_ACTION_PAST}\b",
    r"\b(?:broad|sweeping|repo(?:sitory)?-wide|codebase-wide|system-wide)\b.{0,20}\b(?:rewrite|change|refactor|cleanup)\b",
    r"(?:修复|编辑|重写|修改|更新|重构|替换|删除).{0,20}(?:所有|全部|每个).{0,12}(?:模块|文件|组件|服务|包|分层)",
    r"(?:修复|编辑|重写|修改|更新|重构|替换|删除).{0,20}(?:整个仓库|全仓|整个代码库|整个系统|整个项目)",
    r"(?:大范围|全局|全量).{0,10}(?:重写|修改|重构|清理)",
)


QA_FAILURE_HEADER_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?QA Failure(?:\*\*)?[ \t]*:?[ \t]*$"
)
QA_NEXT_MARKDOWN_SECTION_PATTERN = re.compile(r"(?m)^[ \t]*#{1,6}[ \t]+\S.*$")
VERIFICATION_SCOPE_HEADER_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?Verification Scope(?:\*\*)?[ \t]*:?[ \t]*$"
)


def _qa_failure_block(text):
    text = str(text or "")
    headers = list(QA_FAILURE_HEADER_PATTERN.finditer(text))
    if len(headers) != 1:
        return "", len(headers)
    block = text[headers[0].end() :]
    next_section = QA_NEXT_MARKDOWN_SECTION_PATTERN.search(block)
    if next_section:
        block = block[: next_section.start()]
    return block, 1


def _verification_scope_block(text):
    text = str(text or "")
    headers = list(VERIFICATION_SCOPE_HEADER_PATTERN.finditer(text))
    if len(headers) != 1:
        return "", len(headers)
    block = text[headers[0].end() :]
    qa_header = QA_FAILURE_HEADER_PATTERN.search(block)
    next_section = QA_NEXT_MARKDOWN_SECTION_PATTERN.search(block)
    ends = [
        match.start()
        for match in (qa_header, next_section)
        if match is not None
    ]
    if ends:
        block = block[: min(ends)]
    return block, 1


def _field_values(text, field):
    pattern = rf"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?[ \t]*:[ \t]*([^\r\n]*)[ \t]*$"
    return [
        match.group(1).strip()
        for match in re.finditer(pattern, str(text or ""))
    ]


def _strip_negated_implement_phrases(value):
    value = str(value or "").lower()
    patterns = (
        r"\b(?:do not|does not|will not|must not|should not|cannot|can't|never)\s+(?:(?:enter|route to|invoke|run|start|execute)\s+)?implement\b",
        r"\b(?:don't|doesn't|won't|mustn't|shouldn't)\s+(?:(?:enter|route to|invoke|run|start|execute)\s+)?implement\b",
        r"\bavoid\s+(?:(?:entering|routing to|invoking|running|starting|executing)\s+)?implement\b",
        r"\b(?:am|is|are|was|were)\s+not\s+(?:entering|routing to|invoking|running|starting|executing)\s+implement\b",
        r"(?:不要|不得|不能|不会|不应|避免)(?:进入|路由到|调用|运行|开始|执行)?\s*implement\b",
    )
    for pattern in patterns:
        value = re.sub(pattern, "", value)
    return value


def _has_positive_implement_route(value):
    return bool(re.search(r"\bimplement\b", _strip_negated_implement_phrases(value)))


def _has_changed_hypothesis(value):
    scrubbed = str(value or "").lower()
    for pattern in (
        r"\b(?:no|not|without)\b.{0,24}\b(?:changed|change|new)\s+hypothesis\b",
        r"\bhypothesis\b.{0,16}\b(?:did not|has not|is not)\s+change(?:d)?\b",
        r"(?:没有|无|未|并未).{0,12}(?:改变|更改|调整|新)(?:的)?假设",
    ):
        scrubbed = re.sub(pattern, "", scrubbed)
    return any(marker in scrubbed for marker in QA_CHANGED_HYPOTHESIS_MARKERS)


def _qa_check_identity(value):
    normalized = str(value or "").strip("` ")
    match = re.fullmatch(
        r"(command|manual)\s*:\s*(\S(?:.*\S)?)",
        normalized,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    kind, payload = match.groups()
    kind = kind.lower()
    if kind == "command":
        try:
            lexer = shlex.shlex(
                payload,
                posix=True,
                punctuation_chars=";&|()<>`",
            )
            lexer.whitespace_split = True
            lexer.commenters = ""
            tokens = list(lexer)
        except ValueError:
            return ("invalid", payload)
        if any(re.fullmatch(r"[;&|()<>`]+", token) for token in tokens):
            return ("invalid", payload)
        while tokens and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[0]):
            tokens.pop(0)
        if not tokens:
            return ("invalid", payload)
        executable = tokens[0].rsplit("/", 1)[-1].lower()
        args = tokens[1:]
        if executable in {
            ":", "command", "echo", "env", "eval", "exec", "false", "nice",
            "nohup", "printf", "sudo", "time", "timeout", "true", "xargs",
        }:
            return ("invalid", payload)
        if executable in {"sh", "bash", "zsh", "dash"} and any(
            arg == "-c" or arg.startswith("-c") for arg in args
        ):
            return ("invalid", payload)
        if re.fullmatch(r"python\d*(?:\.\d+)?|node|ruby|perl", executable) and any(
            arg == "--eval" or arg.startswith("--eval=") or arg.startswith(("-c", "-e"))
            for arg in args
        ):
            return ("invalid", payload)
        if executable == "deno" and args and args[0] in {"eval", "repl"}:
            return ("invalid", payload)
    if kind == "manual" and (
        not re.fullmatch(r"[a-z0-9][a-z0-9._/-]*", payload)
        or payload in {"ok", "pass", "success"}
    ):
        return ("invalid", payload)
    return (kind, payload)


def _has_new_authority_or_risk(text):
    lowered = str(text or "").lower()
    if re.search(r"\bapproval needed\s*:\s*yes\b", lowered) or re.search(
        r"\b(?:approval|permission)\b.{0,24}\bnot (?:granted|received|obtained)\b",
        lowered,
    ):
        return True
    negated_patterns = (
        r"\b(?:do|does|did|will|must|should|can)\s+not\b.{0,40}\b(?:change|update|write|mutate|delete|migrate|deploy|push|publish|drop|truncate)\b",
        r"\b(?:don't|doesn't|didn't|won't|mustn't|shouldn't|cannot|can't|never|avoid)\b.{0,40}\b(?:change|update|write|mutate|delete|migrate|deploy|push|publish|drop|truncate)\b",
        r"\bno\b.{0,40}\b(?:write|change|update|mutation|delete)\b.{0,20}\b(?:is|are|was|were)?\s*(?:needed|required|planned)\b",
        r"(?:不要|不得|不能|不会|不应|避免).{0,30}(?:修改|更新|写入|变更|删除|迁移|部署|推送|发布)",
    )
    positive_patterns = (
        r"\b(?:change|update|write|mutate|delete|migrate|deploy|push|publish|drop|truncate)\b.{0,50}\b(?:production (?:data|database|system|environment|deployment|schema|table|rows?)|prod database|live database|database rows?|rows? in (?:prod|production)|in (?:prod|production|live)|remote|customer data|schema)\b",
        r"\b(?:production data|production database|live database|prod database|database rows?|rows? in (?:prod|production)|customer data|in (?:prod|production|live)|(?:prod|production|live) (?:data|database|schema|table|rows?|environment))\b.{0,50}\b(?:write|mutation|change|update|delete|migrate|drop|truncate)\b",
        r"(?:修改|更新|写入|变更|删除|迁移|部署|推送|发布).{0,24}(?:生产数据|生产库|数据库行|远端|客户数据|表结构)",
    )
    for clause in re.split(r"[.;!?\n。；！？]+", lowered):
        scrubbed = clause
        for pattern in negated_patterns:
            scrubbed = re.sub(pattern, "", scrubbed)
        if any(re.search(pattern, scrubbed) for pattern in positive_patterns):
            return True
    return False


def _has_automatic_implement_execution(value):
    value = _strip_negated_implement_phrases(value)
    patterns = (
        r"\bautomatically\b.{0,24}\b(?:execute|invoke|run|start)?\s*implement\b",
        r"\bauto(?:matically)?[- ]?run\b.{0,16}\bimplement\b",
        r"\b(?:execut(?:e|ing)|invok(?:e|ing)|run(?:ning)?|start(?:ing)?)\s+(?:the\s+)?implement\b",
        r"\bimplement\b.{0,16}\b(?:now|immediately|automatically)\b",
        r"\bproceed\s+(?:(?:now|immediately)\s+)?to\s+implement\b",
        r"(?:自动|立即).{0,20}(?:执行|调用|运行)?\s*implement\b",
    )
    return any(re.search(pattern, value) for pattern in patterns)


def _strip_negated_broad_scope_phrases(value):
    value = str(value or "").lower()
    patterns = (
        rf"\b(?:do|does|did|am|is|are|was|were|have|has|had|will|would|must|should|can|could)\s+not\b.{{0,24}}\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\b(?:every|all)\b.{{0,24}}\b(?:modules?|files?|components?|services?|packages?|layers?)\b",
        rf"\b(?:don't|doesn't|didn't|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|won't|wouldn't|mustn't|shouldn't|cannot|can't|couldn't|never|avoid)\b.{{0,24}}\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\b(?:every|all)\b.{{0,24}}\b(?:modules?|files?|components?|services?|packages?|layers?)\b",
        rf"\b(?:do|does|did|am|is|are|was|were|have|has|had|will|would|must|should|can|could)\s+not\b.{{0,24}}\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\beverything\b",
        rf"\b(?:don't|doesn't|didn't|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|won't|wouldn't|mustn't|shouldn't|cannot|can't|couldn't|never|avoid)\b.{{0,24}}\b{QA_SCOPE_ACTION_VARIANT}\b.{{0,40}}\beverything\b",
        rf"\bnot\s+(?:every|all)\b.{{0,24}}\b(?:modules?|files?|components?|services?|packages?|layers?)\b.{{0,40}}\b{QA_SCOPE_ACTION_PAST}\b",
        rf"\b(?:every|all)\b.{{0,24}}\b(?:modules?|files?|components?|services?|packages?|layers?)\b.{{0,40}}\b(?:must|should|will|would|can|could)\s+not\s+be\s+{QA_SCOPE_ACTION_PAST}\b",
        r"(?:不要|不得|不能|不会|不应|避免).{0,16}(?:修复|编辑|重写|修改|更新|重构|替换|删除).{0,20}(?:所有|全部|每个).{0,12}(?:模块|文件|组件|服务|包|分层)",
    )
    for pattern in patterns:
        value = re.sub(pattern, "", value)
    return value


def _has_explicit_broad_scope(value):
    for clause in re.split(r"[.;!?\n。；！？]+", str(value or "").lower()):
        scrubbed = _strip_negated_broad_scope_phrases(clause)
        if any(re.search(pattern, scrubbed) for pattern in QA_BROAD_SCOPE_PATTERNS):
            return True
    return False


def _has_positive_remediation_execution(value):
    value = str(value or "").lower()
    negated = (
        r"\b(?:i|we)\s+(?:did|do|will|have|am|are)\s+not\b[^\n]{0,100}\b(?:apply|patch|fix|change|modify|rewrite|update|edit|implement)\b",
        r"\b(?:i|we)\s+(?:haven't|didn't|don't|won't|am not|aren't|never)\b[^\n]{0,100}\b(?:apply|patch|fix|change|modify|rewrite|update|edit|implement)\b",
        r"\b(?:has|have|had)\s+not\s+been\s+(?:patched|fixed|changed|modified|rewritten|updated|edited|implemented)\b",
        r"\b(?:was|were|is|are)\s+not\s+(?:patched|fixed|changed|modified|rewritten|updated|edited|implemented)\b",
        r"\b(?:fix|patch|change|update|edit|remediation)\b[^\n]{0,40}\b(?:has|have|had)\s+not\s+been\s+applied\b",
        r"\b(?:fix|patch|change|update|edit|remediation)\b[^\n]{0,40}\b(?:was|were|is|are)\s+not\s+applied\b",
        r"(?:我|我们)(?:没有|未|不会|不得|不应).{0,40}(?:修复|修改|重写|更新|编辑|实现)",
    )
    patterns = (
        r"\b(?:i|we)\s+(?:(?:have|had)(?:\s+(?:already|just))?\s+|(?:already|just)\s+)?(?:applied|patched|fixed|changed|modified|rewrote|rewritten|updated|edited|implemented)\b",
        r"\b(?:i|we)\s+(?:am|are)\s+(?:applying|patching|fixing|changing|modifying|rewriting|updating|editing|implementing)\b",
        r"\b(?:has|have|had)\s+(?:(?:already|just)\s+)?been\s+(?:(?:already|just)\s+)?(?:patched|fixed|changed|modified|rewritten|updated|edited|implemented)\b",
        r"\b(?:fix|patch|change|update|edit|remediation)\b[^\n]{0,40}\b(?:has|have|had)\s+(?:(?:already|just)\s+)?been\s+(?:(?:already|just)\s+)?applied\b",
        r"\b(?:fix|patch|change|update|edit|remediation)\b[^\n]{0,40}\b(?:was|were|is|are)\s+(?:already\s+)?applied\b",
        r"\b(?:i|we)\s+(?:update|change|edit|fix|patch|rewrite|implement)\b[^.;!?\n]{0,60}\b(?:now|immediately|already)\b",
        r"\b(?:i|we)\s+(?:will|shall|can|must)\s+(?:now|immediately|right away)\s+(?:apply|patch|fix|change|modify|rewrite|update|edit|implement)\b",
        r"\b(?:i|we)\s+(?:will|shall|can|must)\s+(?:now\s+|immediately\s+)?(?:apply|patch|fix|change|modify|rewrite|update|edit|implement)\b[^.;!?\n]{0,60}\b(?:now|immediately|right away|at once)\b",
        r"\b(?:apply|patch|fix|change|modify|rewrite|update|edit|implement|do)\b[^.;!?\n]{0,40}\b(?:now|immediately|right away|at once)\b",
        r"^\s*(?:deployed|shipped|released|executed|completed|applied|patched|fixed|updated|implemented)\b",
        r"\b(?:went|is) live\b",
        r"\b(?:has|have)\s+(?:shipped|deployed|launched|released|landed|gone live|rolled out)\b",
        r"\bis\s+(?:live|in production|deployed|released|done|complete)\b",
        r"\b(?:rolled out|promoted to production|published)\b",
        r"\b(?:filter|fix|patch|change|release|deployment)\b[^.;!?\n]{0,24}\b(?:was|has been|went)\s+(?:deployed|shipped|released|applied|live)\b",
        r"\b(?:ship|release|deploy)\b[^.;!?\n]{0,40}\b(?:now|immediately|right away|at once)\b",
        r"(?:我|我们)(?:已|已经|正在).{0,16}(?:修复|修改|重写|更新|编辑|实现)",
    )
    for clause in re.split(r"[.;!?\n。；！？]+", value):
        scrubbed = clause
        for pattern in negated:
            scrubbed = re.sub(pattern, "", scrubbed)
        if any(re.search(pattern, scrubbed) for pattern in patterns):
            return True
    return False


def _has_only_qa_structured_lines(text):
    remaining = str(text or "")
    remaining = VERIFICATION_SCOPE_HEADER_PATTERN.sub("", remaining)
    remaining = QA_FAILURE_HEADER_PATTERN.sub("", remaining)
    fields = {
        "Verdict",
        *QA_GAP_CLOSURE_STRUCTURED_FIELDS,
        *(
            alias
            for aliases in VERIFY_SCOPE_FIELD_ALIASES.values()
            for alias in aliases
        ),
    }
    for field in fields:
        remaining = re.sub(
            rf"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?[ \t]*:[ \t]*[^\r\n]*$",
            "",
            remaining,
        )
    return not remaining.strip()


def qa_gap_closure_gate_failures(text):
    """Return deterministic QA feedback-gate contract failures."""

    failures = []
    scope_headers = list(VERIFICATION_SCOPE_HEADER_PATTERN.finditer(str(text or "")))
    qa_headers = list(QA_FAILURE_HEADER_PATTERN.finditer(str(text or "")))
    verification_scope, verification_scope_count = _verification_scope_block(text)
    if verification_scope_count != 1:
        failures.append("Verification Scope block must appear exactly once")
        verdict_values = []
    else:
        verdict_values = _field_values(verification_scope, "Verdict")
    if len(verdict_values) != 1:
        failures.append("Verdict must appear exactly once in Verification Scope")
    verdict = (
        verdict_values[0].lower().strip("` ") if len(verdict_values) == 1 else ""
    )
    if verdict not in {"fail", "blocked"}:
        failures.append("Verification Verdict must remain fail or blocked for QA Failure")

    qa_failure, qa_failure_count = _qa_failure_block(text)
    if qa_failure_count != 1:
        failures.append("QA Failure block must appear exactly once")
        return failures
    if (
        len(scope_headers) == 1
        and len(qa_headers) == 1
        and scope_headers[0].start() > qa_headers[0].start()
    ):
        failures.append("Verification Scope must appear before QA Failure")
    if _field_values(qa_failure, "Verdict"):
        failures.append(
            "Verdict must not appear in QA Failure; keep it in Verification Scope"
        )
    field_values = {
        field: _field_values(qa_failure, field)
        for field in QA_GAP_CLOSURE_STRUCTURED_FIELDS
    }
    for field, values in field_values.items():
        if len(values) != 1:
            failures.append(f"{field} must appear exactly once in QA Failure")
        if len(_field_values(text, field)) != len(values):
            failures.append(f"{field} must appear only inside QA Failure")
    if verification_scope_count == 1:
        for scope_field, aliases in VERIFY_SCOPE_FIELD_ALIASES.items():
            scope_count = sum(
                len(_field_values(verification_scope, alias)) for alias in aliases
            )
            global_count = sum(len(_field_values(text, alias)) for alias in aliases)
            if scope_count != 1:
                failures.append(
                    f"{scope_field} must appear exactly once in Verification Scope"
                )
            if global_count != scope_count:
                failures.append(
                    f"{scope_field} must appear only inside Verification Scope"
                )
        if len(_field_values(text, "Verdict")) != len(verdict_values):
            failures.append("Verdict must appear only inside Verification Scope")

    def qa_value(field):
        values = field_values[field]
        return values[0].lower().strip("` ") if values else ""

    def qa_raw_value(field):
        values = field_values[field]
        return values[0].strip("` ") if values else ""

    admission = qa_value("Gap-Closure Admission")
    if admission not in QA_GAP_CLOSURE_ADMISSIONS:
        failures.append("Gap-Closure Admission is missing or invalid")
        return failures

    evidence_delta = qa_value("Evidence Delta")
    next_action = qa_value("Scoped Next Action")
    implementation_authority = qa_value("Implementation Authority")
    risk_change = qa_value("Risk Change")
    source_ac_change = qa_value("Source / AC Change")
    if implementation_authority not in QA_IMPLEMENTATION_AUTHORITY_VALUES:
        failures.append("Implementation Authority is missing or invalid")
    if risk_change not in QA_RISK_CHANGE_VALUES:
        failures.append("Risk Change is missing or invalid")
    if source_ac_change not in QA_SOURCE_AC_CHANGE_VALUES:
        failures.append("Source / AC Change is missing or invalid")
    severity = qa_value("Severity")
    if not re.fullmatch(r"p[0-3]", severity):
        failures.append("Severity must be P0-P3 for QA Failure")
    field_broad_scope = False
    if admission in QA_GAP_CLOSURE_READY:
        changed_hypothesis = _has_changed_hypothesis(evidence_delta)
        no_evidence_delta = any(
            re.search(pattern, evidence_delta)
            for pattern in QA_NO_EVIDENCE_DELTA_PATTERNS
        )
        if evidence_delta in QA_PLACEHOLDER_VALUES or (
            no_evidence_delta and not changed_hypothesis
        ):
            failures.append("Evidence Delta is missing, unresolved, or contains no new evidence")
        if source_ac_change != "unchanged":
            failures.append(f"Source / AC Change must be unchanged for {admission}")
        if implementation_authority != "existing_and_sufficient":
            failures.append(
                f"Implementation Authority must be existing_and_sufficient for {admission}"
            )
        if risk_change != "unchanged_within_boundary":
            failures.append(
                f"Risk Change must be unchanged_within_boundary for {admission}"
            )
        for field in (
            "Expected",
            "Actual",
            "Reproduction",
            "Minimal Diagnosis",
            "Fix Plan",
            "Gap Closure Plan",
            "Re-QA Required",
        ):
            value = qa_value(field)
            if value in QA_PLACEHOLDER_VALUES:
                failures.append(f"{field} cannot be unresolved for {admission}")
            if field in {"Fix Plan", "Gap Closure Plan"} and _has_explicit_broad_scope(
                value
            ):
                field_broad_scope = True
                failures.append(f"{field} must remain bounded for {admission}")
            if field in {"Fix Plan", "Gap Closure Plan"} and _has_positive_remediation_execution(
                value
            ):
                failures.append(
                    f"{field} must remain a bounded proposal and cannot claim execution for {admission}"
                )
            if field == "Gap Closure Plan" and (
                value in QA_NON_ACTIONABLE_GAP_PLANS
                or not QA_ACTIONABLE_GAP_PLAN_PATTERN.search(value)
            ):
                failures.append(
                    f"Gap Closure Plan must name a scoped change or evidence update for {admission}"
                )
        reproduction_identity = _qa_check_identity(qa_raw_value("Reproduction"))
        re_qa_identity = _qa_check_identity(qa_raw_value("Re-QA Required"))
        if reproduction_identity is None:
            failures.append(
                f"Reproduction must name a stable command: or manual: original-check identity for {admission}"
            )
        elif reproduction_identity[0] == "invalid":
            failures.append(
                f"Original check identity cannot be an echo/status placeholder for {admission}"
            )
        if re_qa_identity is None or (
            reproduction_identity
            and reproduction_identity[0] != "invalid"
            and re_qa_identity != reproduction_identity
        ):
            failures.append(
                f"Re-QA Required must name the same original-check identity as Reproduction for {admission}"
            )
        elif re_qa_identity[0] == "invalid" and (
            not reproduction_identity or reproduction_identity[0] != "invalid"
        ):
            failures.append(
                f"Original check identity cannot be an echo/status placeholder for {admission}"
            )
        if next_action not in QA_SCOPED_NEXT_ACTIONS[admission]:
            failures.append(
                f"Scoped Next Action must be route: implement for {admission}"
            )
    else:
        allowed_actions = QA_SCOPED_NEXT_ACTIONS[admission]
        if next_action not in allowed_actions:
            failures.append(
                f"Scoped Next Action must be one of {', '.join(sorted(allowed_actions))} for {admission}"
            )
    if (
        implementation_authority == "approval_required"
        or risk_change == "new_or_increased"
    ) and admission not in {"human_decision", "blocked"}:
        failures.append(
            "Gap-Closure Admission must be human_decision or blocked when approval is required or risk is new/increased"
        )
    if implementation_authority == "missing" and admission != "blocked":
        failures.append(
            "Gap-Closure Admission must be blocked when implementation authority is missing"
        )

    if _has_new_authority_or_risk(text) and admission not in {
        "human_decision",
        "blocked",
    }:
        failures.append(
            "New authority or risk must route to human_decision or blocked"
        )

    if _has_explicit_broad_scope(text) and not field_broad_scope:
        failures.append("QA gap closure must remain bounded across the full output")
    if not _has_only_qa_structured_lines(text):
        failures.append(
            "QA gap closure output must contain only Verification Scope and QA Failure structured fields"
        )
    execution_narrative = str(text or "")
    for field in (*QA_GAP_CLOSURE_STRUCTURED_FIELDS, *VERIFY_SCOPE_FIELDS, "Verdict"):
        execution_narrative = re.sub(
            rf"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?[ \t]*:[ \t]*[^\r\n]*$",
            "",
            execution_narrative,
        )
    if _has_automatic_implement_execution(
        execution_narrative
    ) or _has_positive_remediation_execution(execution_narrative):
        failures.append("QA gap closure must recommend rather than execute implement")

    return failures
