"""Deterministic output checks for bounded workflow loops and lenses."""

import re


PLACEHOLDER_VALUES = {"", "not provided", "unverified", "unknown", "none", "n/a"}
PROTOTYPE_ITERATION_FIELDS = (
    "Current Hypothesis",
    "Probe",
    "Observation",
    "Evidence Delta Status",
    "Evidence Delta",
    "Decision Delta Status",
    "Decision Delta",
    "Next Probe or Stop",
)
SPEC_WRITEBACK_FIELDS = (
    "Decision Delta Status",
    "Decision Delta",
    "Canonical Update Status",
    "Canonical Update",
    "Resolved / Removed",
    "Next Route or Question",
)
SPEC_RESOLUTION_MARKERS = (
    "resolved",
    "removed",
    "cleared",
    "closed",
    "moved to known",
    "deleted",
    "已解决",
    "已移除",
    "已清除",
    "已关闭",
    "移入已知事实",
    "删除",
)
SPEC_STALE_RESOLUTION_PATTERNS = (
    r"\b(?:is|are|was|were)\s+(?:still\s+)?(?:open|unresolved|pending|blocking)\b",
    r"\b(?:kept|still|remains?)\b.{0,24}\bunresolved\b",
    r"\b(?:not|never)\s+(?:resolved|removed|closed|cleared)\b",
    r"\b(?:kept|left|preserved)\b.{0,24}\bopen\b",
    r"\b(?:resolved|removed?|closed|cleared|deleted)\s+(?:nothing|none)\b",
    r"\b(?:resolved|removed?|closed|cleared|deleted)\s+no\b.{0,20}\b(?:question|ambiguity|item|state)\b",
    r"\bnothing\s+(?:was\s+)?(?:resolved|removed|closed|cleared)\b",
    r"\bdid\s+not\s+(?:resolve|remove|close|clear|delete)\b",
    r"\b(?:kept|left|preserved)\b.{0,32}\b(?:pending|blocking)\b",
    r"\bstill\s+(?:an?\s+|the\s+)?(?:open|unresolved|pending|blocking)\b",
    r"\bremains?\s+(?:an?\s+|the\s+)?(?:open|unresolved|pending|blocking)\b",
    r"\bcontinues?\s+(?:to\s+be|as)\s+(?:an?\s+|the\s+)?(?:open|unresolved|pending|blocking)\b",
    r"仍(?:未解决|待确认|开放)",
    r"保留.{0,16}(?:未解决|待确认|开放)",
    r"继续(?:待确认|开放)",
    r"(?:什么也没有|未移除任何|没有移除任何).{0,12}(?:问题|歧义|状态)?",
    r"(?:仍然|依然|继续).{0,16}(?:开放|未解决|待确认|阻塞)",
)
SPEC_NO_DECISION_DELTA_PATTERNS = (
    r"\b(?:there\s+(?:is|was)\s+)?no\s+(?:new\s+)?decision delta\b",
    r"^\s*(?:unchanged|repeat(?:ed)?)\s*[.;]?\s*$",
    r"^\s*no decision delta[.;]?\s*$",
    r"^\s*no (?:new |material )?decision delta[.;]?\s*$",
    r"^\s*(?:the )?decision (?:is )?unchanged[.;]?\s*$",
    r"^\s*(?:the )?decision (?:still )?(?:remains?|stays?) unchanged[.;]?\s*$",
    r"^\s*(?:the )?decision (?:still )?stays? as (?:it was|before)[.;]?\s*$",
    r"^\s*nothing\b.{0,32}\bdecision\b.{0,16}\bchanged?\b[.;]?\s*$",
    r"^\s*no change to (?:the )?decision[.;]?\s*$",
    r"^\s*continue(?: unchanged| as before)?[.;]?\s*$",
    r"^\s*(?:keep|retain) (?:the )?(?:current|same) decision[.;]?\s*$",
    r"^\s*(?:the )?hypothesis remains unchanged[.;]?\s*$",
    r"^\s*(?:same as before|unchanged from before)[.;]?\s*$",
    r"^\s*(?:无决策变化|没有决策增量|决策未变化)[。；;]?\s*$",
)
SPEC_NO_CANONICAL_UPDATE_PATTERNS = (
    r"^\s*no canonical update[.;]?\s*$",
    r"^\s*(?:unchanged|same as before|unchanged from before)[.;]?\s*$",
    r"^\s*(?:the )?canonical (?:state|draft) (?:is )?unchanged[.;]?\s*$",
    r"^\s*(?:the )?canonical (?:state|draft) (?:still )?(?:remains?|stays?) unchanged[.;]?\s*$",
    r"^\s*(?:the )?canonical (?:state|draft) (?:still )?stays? as (?:it was|before)[.;]?\s*$",
    r"^\s*(?:kept|left|preserved)\b.{0,32}\bcanonical\b.{0,24}\b(?:as-is|unchanged)\b[.;]?\s*$",
    r"^\s*(?:kept|left|preserved)\b.{0,32}\bcanonical\b.{0,24}\b(?:alone|as before)\b[.;]?\s*$",
    r"^\s*not updated[.;]?\s*$",
    r"\b(?:will|would|shall)\s+remain unchanged\b",
    r"\b(?:defer(?:red)?|postpone(?:d)?|leave unchanged)\b.{0,40}\b(?:later|future|next session)\b",
    r"\b(?:will|plan to)\s+(?:update|write back)\b.{0,30}\b(?:later|future|next session)\b",
    r"\bcanonical\s+(?:update|state|draft)\b.{0,32}\b(?:deferred|postponed|pending)\b",
    r"^\s*(?:deferred|postponed|pending)\b",
    r"^\s*(?:无规范更新|没有规范更新|规范状态未更新)[。；;]?\s*$",
    r"(?:延后|推迟|暂不|以后再|下次会话再).{0,24}(?:更新|写回|修改)(?:当前)?(?:规范|状态)?",
)
NO_DELTA_MARKERS = (
    "no new evidence",
    "no evidence delta",
    "没有新证据",
    "无新证据",
    "无证据增量",
)
STOP_MARKERS = (
    "stop",
    "pause",
    "do not continue",
    "will not continue",
    "change hypothesis",
    "require new evidence",
    "need new evidence",
    "await new evidence",
    "until new evidence",
    "human decision",
    "停止",
    "暂停",
    "不再继续",
    "不会继续",
    "更改假设",
    "需要新证据",
    "等待新证据",
    "有新证据后",
    "人工决策",
)
PUBLIC_NEXT_ROUTES = (
    "to-prd",
    "to-issues",
    "triage",
    "write-plan",
    "prototype",
    "implement",
    "verify",
    "handoff",
    "dispatch",
    "wiki",
)
PROTOTYPE_NEXT_STATES = {"propose_probe", "stop"}
SPEC_NEXT_STATES = {"route", "question", "stop"}
RISK_CHECKPOINT_FIELDS = (
    "Proposed Action",
    "Action Kind",
    "Target",
    "Target Kind",
    "Risk",
    "Rollback/Undo",
    "Approval Needed",
    "Risk Gate",
    "Approval Status",
    "Action State",
    "Checkpoint Position",
)
RISK_CHECKPOINT_TOKENS = {
    "Action Kind": "data_mutation",
    "Target Kind": "data_store",
    "Approval Needed": "yes",
    "Risk Gate": "data_write",
    "Approval Status": "pending",
    "Action State": "blocked",
    "Checkpoint Position": "before_action",
}
UAT_EVIDENCE_WINDOW_FIELDS = (
    "Claim / Delivery Scope",
    "Relevant SUT Fingerprint",
    "Preconditions",
    "Window Stability",
    "Coverage Basis",
    "Result / Missing",
    "Rerun Of / Supersedes",
)
UAT_EVIDENCE_WINDOW_SCOPE_FIELDS = ("Claim", "Covered", "Missing", "Verdict")
UAT_HANDOFF_REFERENCE_FIELDS = (
    "Canonical Reference",
    "Claim / Delivery Scope",
    "Relevant SUT Fingerprint",
    "Window Stability",
    "Missing / Closeout Gap",
    "Rerun Of / Supersedes",
    "Next Owner Action",
    "Execution Boundary",
)
RELEASE_EVIDENCE_CLAIM_TYPES = {
    "runtime",
    "cache",
    "release",
    "uat",
    "marketplace",
    "cache_refresh",
    "not_applicable",
}
RELEASE_EVIDENCE_STATUSES = {"verified", "unverified", "not_applicable"}
RELEASE_REFRESH_METHODS = {
    "refresh_step",
    "source_equivalence",
    "not_run",
    "not_applicable",
}
RELEASE_RUN_SCOPES = {"targeted", "full", "not_run", "not_applicable"}


def _field_value(text, field):
    values = _field_values(text, field)
    return values[0] if values else ""


def _field_values(text, field):
    pattern = rf"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?[ \t]*:[ \t]*([^\r\n]*)[ \t]*$"
    return [
        match.group(1).strip()
        for match in re.finditer(pattern, str(text or ""))
    ]


def _exact_token(value):
    return str(value or "").lower().strip("` ")


def _pipe_tokens(value):
    return [
        part.strip().lower()
        for part in str(value or "").split("|")
        if part.strip()
    ]


def _section_block(text, heading):
    raw_text = str(text or "")
    pattern = re.compile(
        rf"(?im)^[ \t]*(?:#{{1,6}}[ \t]*)?(?:\*\*)?{re.escape(heading)}(?:\*\*)?[ \t]*:?[ \t]*$"
    )
    headings = list(pattern.finditer(raw_text))
    if len(headings) != 1:
        return "", len(headings), (0, 0)
    start = headings[0].end()
    next_section = re.search(r"(?m)^[ \t]*#{1,6}[ \t]+\S.*$", raw_text[start:])
    end = start + next_section.start() if next_section else len(raw_text)
    return raw_text[start:end], 1, (headings[0].start(), end)


def _without_field_lines(text, fields):
    result = str(text or "")
    for field in fields:
        result = re.sub(
            rf"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?[ \t]*:[ \t]*[^\r\n]*$",
            "",
            result,
        )
    return result


def _release_evidence_claim_block(text):
    raw_text = str(text or "")
    pattern = re.compile(
        r"(?ms)^[ \t]*```yaml[ \t]*\r?\n"
        r"(?P<body>[ \t]*release_evidence_claim:[ \t]*\r?\n.*?)"
        r"^[ \t]*```[ \t]*(?:\r?\n|$)"
    )
    matches = list(pattern.finditer(raw_text))
    if len(matches) != 1:
        return "", len(matches), (0, 0)
    match = matches[0]
    return match.group("body").strip(), 1, (match.start(), match.end())


def _parse_release_evidence_claim(body):
    pattern = re.compile(
        r"release_evidence_claim:[ \t]*\r?\n"
        r"[ ]{2}claim_type:[ \t]*(?P<claim_type>[^\r\n]+)\r?\n"
        r"[ ]{2}claim:[ \t]*(?P<claim>[^\r\n]+)\r?\n"
        r"[ ]{2}evidence_status:[ \t]*(?P<evidence_status>[^\r\n]+)\r?\n"
        r"[ ]{2}installed_plugin_root:[ \t]*(?P<installed_plugin_root>[^\r\n]+)\r?\n"
        r"[ ]{2}source_root:[ \t]*(?P<source_root>[^\r\n]+)\r?\n"
        r"[ ]{2}cache_or_source_refresh:[ \t]*\r?\n"
        r"[ ]{4}method:[ \t]*(?P<refresh_method>[^\r\n]+)\r?\n"
        r"[ ]{4}evidence:[ \t]*(?P<refresh_evidence>[^\r\n]+)\r?\n"
        r"[ ]{2}run_scope:[ \t]*(?P<run_scope>[^\r\n]+)\r?\n"
        r"[ ]{2}commands_or_trials:[ \t]*(?P<commands_or_trials>[^\r\n]+)\r?\n"
        r"[ ]{2}limitations:[ \t]*(?P<limitations>[^\r\n]+)"
    )
    match = pattern.fullmatch(str(body or "").strip())
    return match.groupdict() if match else None


def _yaml_scalar_token(value):
    return str(value or "").strip().strip("`\"'").lower()


def _yaml_inline_list(value):
    raw_value = str(value or "").strip()
    if not (raw_value.startswith("[") and raw_value.endswith("]")):
        return None
    inner = raw_value[1:-1].strip()
    if not inner:
        return []
    items = inner.split(",")
    if any(not item.strip() for item in items):
        return None
    return [_yaml_scalar_token(item) for item in items]


def _without_release_evidence_claim(text):
    raw_text = str(text or "")
    _body, count, block_range = _release_evidence_claim_block(raw_text)
    if count != 1:
        return raw_text
    start, end = block_range
    return raw_text[:start] + raw_text[end:]


def _has_immediate_probe_execution(text):
    return bool(
        re.search(
            r"(?i)\b(?:run|execute|repeat|rerun|re-run|start|perform)\b[^.;!?\n]{0,32}\b(?:probe|it|that|this)?\b[^.;!?\n]{0,12}\b(?:now|immediately|automatically)\b"
            r"|\b(?:probe|check|test)\b[^.;!?\n]{0,16}\b(?:starts?|runs?|executes?)\b[^.;!?\n]{0,12}\b(?:now|immediately|automatically)\b"
            r"|\b(?:i|we)\s+(?:will|can|shall|must)\s+(?:now\s+|immediately\s+)?(?:run|execute|repeat|rerun|start)\b"
            r"|(?:立即|现在|自动).{0,16}(?:运行|执行|重复|重跑|开始)(?:该|这个)?(?:探针|检查)?",
            str(text or ""),
        )
    )


def _has_immediate_spec_continuation(text):
    return bool(
        re.search(
            r"(?i)\b(?:continue|resume|ask|repeat|rerun|re-run)\b[^.;!?\n]{0,36}\b(?:question|it|that|this)?\b[^.;!?\n]{0,12}\b(?:now|immediately|automatically)\b"
            r"|\b(?:i|we)\s+(?:will|can|shall|must)\s+(?:now\s+|immediately\s+)?(?:continue|resume|ask|repeat)\b"
            r"|(?:立即|现在|自动).{0,16}(?:继续|提问|追问|重复|再问)",
            str(text or ""),
        )
    )


def _has_ungated_risky_execution(text):
    coarse_clauses = re.split(r"[.;!?\n。；！？]+", str(text or "").lower())
    clauses = []
    for coarse_clause in coarse_clauses:
        clauses.extend(
            re.split(r"\b(?:but|however|yet)\b|但(?:是)?|不过", coarse_clause)
        )
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        if re.search(
            r"\b(?:after|only after)\s+(?:human\s+)?approval\b"
            r"|\b(?:once|when|if)\b.{0,32}(?:\bapproval\b.{0,20}\b(?:is|has been|was)\s+granted\b|\bapproved\b)"
            r"|(?:仅在|只有在|等待|获得).{0,20}(?:批准|审批|授权).{0,12}(?:后|通过)",
            clause,
        ):
            continue
        if re.search(
            r"\b(?:do not|don't|must not|cannot|can't|will not|never)\b.{0,36}\b(?:update|write|mutate|change|execute|perform|start|proceed|begin|migrate|delete|drop|truncate)\b"
            r"|(?:不要|不得|不能|不会|不应|避免).{0,24}(?:更新|写入|变更|执行|开始|迁移|删除)",
            clause,
        ):
            continue
        risky_target = re.search(
            r"\b(?:database|production data|data write|migration|schema|customer data|prod|live)\b"
            r"|(?:数据库|生产数据|数据写入|迁移|表结构|客户数据)",
            clause,
        )
        immediate = re.search(r"\b(?:now|immediately|before approval)\b|(?:现在|立即|批准前)", clause)
        active = re.search(
            r"\b(?:can|will|shall|must|should|may)\s+(?:be\s+)?(?:update|updated|write|written|mutate|mutated|change|changed|execute|executed|perform|performed|start|started|proceed|begin|migrate|migrated|delete|deleted|drop|truncate)\b"
            r"|\b(?:update|write|mutate|change|execute|perform|start|proceed|begin|migrate|delete|drop|truncate)\b.{0,36}\b(?:now|immediately|before approval)\b"
            r"|(?:可以|将|会|必须|应当|立即|现在).{0,20}(?:更新|写入|变更|执行|开始|迁移|删除)",
            clause,
        )
        pronoun_proceed = re.search(
            r"\b(?:can|will|shall|must|should|may)\s+(?:update|write|mutate|change|execute|perform|start|proceed|begin|migrate|delete)\s+(?:with\s+)?(?:it|that|this)\b",
            clause,
        )
        pronoun_immediate = re.search(
            r"\b(?:update|write|mutate|change|execute|perform|start|proceed|begin|migrate|delete)\s+(?:with\s+)?(?:it|that|this)\b.{0,20}\b(?:now|immediately|before approval)\b",
            clause,
        )
        if (risky_target and active) or (
            immediate and (pronoun_proceed or pronoun_immediate)
        ):
            return True
    return False


def _companion_field_failures(text, field, *, required):
    values = _field_values(text, field)
    failures = []
    if required:
        if len(values) != 1:
            failures.append(f"{field} must appear exactly once")
        elif _is_unresolved(values[0]):
            failures.append(f"{field} is missing or unresolved")
    elif values:
        failures.append(f"{field} is not allowed for the selected state")
    return values, failures


def _is_unresolved(value):
    return str(value or "").lower().strip("` ") in PLACEHOLDER_VALUES


def _has_resolution_marker(value):
    value = str(value or "").lower()
    for marker in SPEC_RESOLUTION_MARKERS:
        if marker.isascii():
            if re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", value):
                return True
        elif marker in value:
            return True
    return False


def _has_no_delta(value):
    lowered = str(value or "").lower()
    if any(marker in lowered for marker in NO_DELTA_MARKERS):
        return True
    if lowered.strip(" .;") == "same result and same hypothesis":
        return True
    repeated_only = (
        r"^\s*(?:same|unchanged|same as before|unchanged from before|repeat(?:ed)?)[.;]?\s*$",
        r"^\s*(?:the\s+)?(?:same|unchanged)\s+(?:observation|result|output|evidence)[.;]?\s*$",
        r"^\s*(?:the\s+)?(?:prior|previous|same|unchanged)\s+(?:observation|result|output|evidence)(?:\s+(?:was|is))?\s+(?:repeated|unchanged|the same)[.;]?\s*$",
        r"^\s*(?:an?\s+)?(?:repeated|repeat of)\s+(?:the\s+)?(?:prior|previous|same)\s+(?:observation|result|output|evidence)[.;]?\s*$",
        r"^\s*(?:the\s+)?(?:observation|result|output|evidence)?\s*(?:still\s+)?(?:remains?|stays?)\s+unchanged(?:\s+from\s+(?:the\s+)?(?:prior|previous|last)\s+(?:run|probe|iteration))?[.;]?\s*$",
        r"^\s*unchanged\s+from\s+(?:the\s+)?(?:prior|previous|last)\s+(?:run|probe|iteration)[.;]?\s*$",
        r"^\s*identical\s+to\s+(?:the\s+)?(?:prior|previous|last)\s+(?:run|probe|iteration)[.;]?\s*$",
        r"^\s*(?:the\s+)?same\s+(?:outcome|result|output|evidence)\s+as\s+(?:the\s+)?(?:prior|previous|last)\s+(?:run|probe|iteration)[.;]?\s*$",
        r"^\s*(?:重复(?:了)?(?:此前|之前|原有)?(?:观察|结果|输出)|(?:观察|结果|输出)未变)[。；;]?\s*$",
    )
    return any(re.search(pattern, lowered) for pattern in repeated_only)


def _has_positive_delta_claim(value):
    return bool(
        re.search(
            r"(?i)\b(?:new|first|changed|localized|identified|accepted|rejected)\b"
            r"|\broute\s+to\b|\b(?:choose|select|use)\b.{0,24}\b(?:route|implement|decision)\b"
            r"|\bimplement route\b|(?:新的|首次|已改变|已定位|已识别|已接受|已拒绝|路由到)",
            str(value or ""),
        )
    )


def _question_count(text):
    text = str(text or "")
    punctuation_count = len(re.findall(r"[?？]", text))
    field_count = len(re.findall(r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?Question(?:\*\*)?\s*:", text))
    return max(punctuation_count, field_count)


def _has_explicit_no_decision_delta(value):
    lowered = str(value or "").lower().strip("` ")
    return lowered in {
        "none",
        "same",
        "unchanged",
        "same as before",
        "unchanged from before",
        "repeat",
        "repeated",
    } or any(
        re.search(pattern, lowered) for pattern in SPEC_NO_DECISION_DELTA_PATTERNS
    )


def _has_stop_semantics(text):
    lowered = str(text or "").lower()
    negated_stop = (
        r"\b(?:do|does|will|must|should|can)\s+not\s+(?:stop|pause)\b",
        r"\b(?:don't|doesn't|won't|mustn't|shouldn't|cannot|can't|never|avoid)\s+(?:stop|stopping|pause|pausing)\b",
        r"\b(?:stop|pause)\s+(?:is|are)\s+not\s+(?:required|needed|necessary)\b",
        r"\bno\s+(?:stop|pause)\s+(?:is\s+)?(?:required|needed|necessary)\b",
        r"(?:不要|不得|不能|不会|不应|避免)(?:停止|暂停)",
        r"(?:停止|暂停)(?:不是|并非)(?:必须|必要)",
    )
    for pattern in negated_stop:
        lowered = re.sub(pattern, "", lowered)
    return any(marker in lowered for marker in STOP_MARKERS)


def _has_positive_continuation(text):
    lowered = str(text or "").lower()
    negated_continuation = (
        r"\b(?:do|does|will|must|should|can)\s+not\s+(?:continue|proceed|repeat|rerun|re-run|run|ask)\b",
        r"\b(?:don't|doesn't|won't|mustn't|shouldn't|cannot|can't|never|avoid)\s+(?:continue|continuing|proceed|proceeding|repeat|repeating|rerun|re-running|run|running|ask|asking)\b",
        r"(?:不要|不得|不能|不会|不应|避免)(?:继续|重复|重跑|再问)",
    )
    scrubbed = lowered
    for pattern in negated_continuation:
        scrubbed = re.sub(pattern, "", scrubbed)
    conditional_continuation = (
        r"\b(?:continue|proceed|repeat|rerun|re-run|run|ask(?:\s+again)?)\b.{0,24}\b(?:only\s+)?(?:after|when|once)\b.{0,24}\b(?:new evidence|new decision delta|hypothesis changes?)\b",
        r"\b(?:only\s+)?(?:after|when|once)\b.{0,24}\b(?:new evidence|new decision delta|hypothesis changes?)\b.{0,24}\b(?:continue|proceed|repeat|rerun|re-run|run|ask)\b",
        r"(?:仅在|只有在|等到).{0,16}(?:新证据|新决策增量|假设变更).{0,16}(?:后|时).{0,12}(?:继续|重复|重跑|再问)",
    )
    for pattern in conditional_continuation:
        scrubbed = re.sub(pattern, "", scrubbed)
    patterns = (
        r"\b(?:do|does|will|must|should|can)\s+not\s+(?:stop|pause)\b",
        r"\b(?:don't|doesn't|won't|mustn't|shouldn't|cannot|can't|never)\s+(?:stop|pause)\b",
        r"\bcontinue\b",
        r"\bproceed\b",
        r"\bkeep\s+(?:going|asking|probing|iterating)\b",
        r"\b(?:repeat|rerun|re-run)\b",
        r"\brun\b.{0,24}\b(?:same|unchanged|prior|previous)\b.{0,16}\b(?:probe|check|test|step)?\b",
        r"\bask\b.{0,24}\b(?:another|equivalent|same|next)\b.{0,16}\b(?:question)?\b",
        r"\bpropose\b.{0,16}\banother\b.{0,16}\b(?:probe|question)\b",
        r"(?:不要|不得|不能|不会|不应)(?:停止|暂停)",
        r"(?:继续|重复|重跑|再问|再次执行)",
    )
    return any(re.search(pattern, scrubbed) for pattern in patterns)


def _has_positive_automatic_continuation(text):
    lowered = str(text or "").lower()
    negated = (
        "will not continue automatically",
        "do not continue automatically",
        "must not continue automatically",
        "should not continue automatically",
        "cannot continue automatically",
        "can't continue automatically",
        "never auto-run",
        "do not auto-run",
        "must not auto-run",
        "will not automatically repeat",
        "do not automatically repeat",
        "must not automatically repeat",
        "不会自动继续",
        "不要自动继续",
        "不能自动继续",
        "不应自动继续",
        "不自动迭代",
        "不得自动迭代",
        "不要自动重复",
        "不得自动重复",
    )
    scrubbed = lowered
    for marker in negated:
        scrubbed = scrubbed.replace(marker, "")
    patterns = (
        r"\b(?:will|must|should|keep)\b.{0,24}\bcontinue automatically\b",
        r"\bcontinue automatically\b",
        r"\bautomatically continue\b",
        r"\bauto(?:matically)?[- ]?run\b",
        r"\bautomatically repeat\b",
        r"\brepeat automatically\b",
        r"\bauto(?:matically)?[- ]?repeat\b",
        r"继续自动(?:迭代|运行)",
        r"自动继续(?:迭代|运行)?",
        r"自动重复",
    )
    return any(re.search(pattern, scrubbed) for pattern in patterns)


def prototype_iteration_checkpoint_failures(text):
    failures = []
    raw_text = str(text or "")
    checkpoint, checkpoint_count, checkpoint_range = _section_block(
        raw_text, "Iteration Checkpoint"
    )
    if checkpoint_count != 1:
        failures.append("Iteration Checkpoint must appear exactly once")
    source = checkpoint if checkpoint_count == 1 else ""
    matches = {
        field: _field_values(source, field) for field in PROTOTYPE_ITERATION_FIELDS
    }
    values = {field: field_values[0] if field_values else "" for field, field_values in matches.items()}
    for field, field_values in matches.items():
        if len(field_values) != 1:
            failures.append(f"{field} must appear exactly once")
    for field in (*PROTOTYPE_ITERATION_FIELDS, "Proposed Probe", "Stop Reason"):
        if len(_field_values(raw_text, field)) != len(_field_values(source, field)):
            failures.append(f"{field} must appear only inside Iteration Checkpoint")
    for field, value in values.items():
        if field in {"Evidence Delta Status", "Decision Delta Status"}:
            continue
        if field in {"Evidence Delta", "Decision Delta"} and _exact_token(value) == "none":
            continue
        if _is_unresolved(value):
            failures.append(f"{field} is missing or unresolved")
    evidence_delta_status = _exact_token(values["Evidence Delta Status"])
    decision_delta_status = _exact_token(values["Decision Delta Status"])
    if evidence_delta_status not in {"changed", "none"}:
        failures.append("Evidence Delta Status must be one of: changed, none")
    if decision_delta_status not in {"changed", "none"}:
        failures.append("Decision Delta Status must be one of: changed, none")
    if evidence_delta_status == "changed" and _has_no_delta(values["Evidence Delta"]):
        failures.append("Evidence Delta contains no new evidence")
    normalized_observation = re.sub(
        r"\s+", " ", values["Observation"].lower().strip("` .;:")
    )
    normalized_evidence_delta = re.sub(
        r"\s+", " ", values["Evidence Delta"].lower().strip("` .;:")
    )
    normalized_hypothesis = re.sub(
        r"\s+", " ", values["Current Hypothesis"].lower().strip("` .;:")
    )
    normalized_decision_delta = re.sub(
        r"\s+", " ", values["Decision Delta"].lower().strip("` .;:")
    )
    if normalized_evidence_delta and normalized_evidence_delta == normalized_observation:
        failures.append("Evidence Delta must not repeat Observation")
    if normalized_decision_delta and normalized_decision_delta == normalized_hypothesis:
        failures.append("Decision Delta must not repeat Current Hypothesis")
    no_evidence_delta = evidence_delta_status == "none"
    no_decision_delta = decision_delta_status == "none"
    if decision_delta_status == "changed" and _has_explicit_no_decision_delta(
        values["Decision Delta"]
    ):
        failures.append("Decision Delta Status changed requires a material decision delta")
    if no_evidence_delta and _has_positive_delta_claim(values["Evidence Delta"]):
        failures.append("Evidence Delta Status none contradicts the delta detail")
    if no_decision_delta and _has_positive_delta_claim(values["Decision Delta"]):
        failures.append("Decision Delta Status none contradicts the delta detail")
    next_state = _exact_token(values["Next Probe or Stop"])
    if next_state not in PROTOTYPE_NEXT_STATES:
        failures.append("Next Probe or Stop must be one of: propose_probe, stop")
    proposed_probe_values, proposed_probe_failures = _companion_field_failures(
        source, "Proposed Probe", required=next_state == "propose_probe"
    )
    stop_reason_values, stop_reason_failures = _companion_field_failures(
        source, "Stop Reason", required=next_state == "stop"
    )
    failures.extend(proposed_probe_failures)
    failures.extend(stop_reason_failures)
    if next_state == "propose_probe" and proposed_probe_values and _has_immediate_probe_execution(
        proposed_probe_values[0]
    ):
        failures.append("Proposed Probe must describe a proposal, not immediate execution")
    if next_state == "stop" and stop_reason_values and (
        _has_positive_continuation(stop_reason_values[0])
        or _has_immediate_probe_execution(stop_reason_values[0])
    ):
        failures.append("Stop Reason cannot continue or execute another probe")
    if no_evidence_delta and next_state != "stop":
        failures.append("Evidence Delta Status none must stop or change hypothesis")
    if no_decision_delta and next_state != "stop":
        failures.append("Decision Delta with no change must stop or change hypothesis")
    control_text = ""
    if checkpoint_count == 1:
        start, end = checkpoint_range
        control_text = (
            str(text or "")[:start]
            + _without_field_lines(
                source,
                (*PROTOTYPE_ITERATION_FIELDS, "Proposed Probe", "Stop Reason"),
            )
            + str(text or "")[end:]
        )
    if _has_positive_automatic_continuation(control_text):
        failures.append("prototype iteration cannot auto-run")
    if _has_immediate_probe_execution(control_text):
        failures.append("prototype iteration cannot execute a proposed probe immediately")
    return failures


def prototype_no_delta_stop_failures(text):
    failures = []
    if not _has_stop_semantics(text):
        failures.append("no-delta prototype iteration must stop or change hypothesis")
    if _has_positive_continuation(text):
        failures.append(
            "no-delta prototype iteration cannot continue without new evidence"
        )
    if _has_positive_automatic_continuation(text):
        failures.append("no-delta prototype iteration cannot continue automatically")
    return failures


def prototype_one_shot_failures(text):
    failures = []
    lowered = str(text or "").lower()
    for pattern in (
        r"\bno iteration checkpoint (?:is )?(?:needed|required)\b",
        r"\bdo not (?:emit|add|use) (?:an? )?iteration checkpoint\b",
        r"\bwithout (?:an? )?iteration checkpoint\b",
        r"(?:无需|不需要|不要)(?:输出|添加|使用)?\s*iteration checkpoint",
    ):
        lowered = re.sub(pattern, "", lowered)
    if "iteration checkpoint" in lowered:
        failures.append("one-shot prototype must not emit empty iteration scaffolding")
    if not any(marker in lowered for marker in ("stop", "cleanup", "no follow-up", "停止", "清理", "无需继续")):
        failures.append("one-shot prototype must name stop, cleanup, or no follow-up")
    return failures


def spec_single_question_failures(text):
    count = _question_count(text)
    failures = []
    if count != 1:
        failures.append(f"spec convergence must ask exactly one question; found {count}")
    if _is_unresolved(_field_value(text, "Impact / Next route")):
        failures.append("spec convergence must name a non-empty Impact / Next route")
    return failures


def spec_writeback_failures(text):
    failures = []
    raw_text = str(text or "")
    checkpoint, checkpoint_count, checkpoint_range = _section_block(
        raw_text, "Spec Convergence Checkpoint"
    )
    if checkpoint_count != 1:
        failures.append("Spec Convergence Checkpoint must appear exactly once")
    source = checkpoint if checkpoint_count == 1 else ""
    matches = {field: _field_values(source, field) for field in SPEC_WRITEBACK_FIELDS}
    values = {field: field_values[0] if field_values else "" for field, field_values in matches.items()}
    for field, field_values in matches.items():
        if len(field_values) != 1:
            failures.append(f"{field} must appear exactly once")
        if _is_unresolved(values[field]):
            failures.append(f"{field} is missing or unresolved")
    for field in (
        *SPEC_WRITEBACK_FIELDS,
        "Next Route",
        "Question",
        "Impact / Next route",
        "Stop Reason",
    ):
        if len(_field_values(raw_text, field)) != len(_field_values(source, field)):
            failures.append(
                f"{field} must appear only inside Spec Convergence Checkpoint"
            )
    if _exact_token(values["Decision Delta Status"]) != "changed":
        failures.append("Decision Delta Status must be changed")
    if _exact_token(values["Canonical Update Status"]) != "updated":
        failures.append("Canonical Update Status must be updated")
    question_field_values = _field_values(source, "Question")
    question_count = max(
        len(question_field_values),
        sum(len(re.findall(r"[?？]", value)) for value in question_field_values),
    )
    next_state = _exact_token(values["Next Route or Question"])
    if next_state not in SPEC_NEXT_STATES:
        failures.append("Next Route or Question must be one of: question, route, stop")
    stop_reason_values = []
    if next_state in SPEC_NEXT_STATES:
        next_route_values, next_route_failures = _companion_field_failures(
            source, "Next Route", required=next_state == "route"
        )
        question_values, question_failures = _companion_field_failures(
            source, "Question", required=next_state == "question"
        )
        impact_values, impact_failures = _companion_field_failures(
            source, "Impact / Next route", required=next_state == "question"
        )
        stop_reason_values, stop_reason_failures = _companion_field_failures(
            source, "Stop Reason", required=next_state == "stop"
        )
        failures.extend(next_route_failures)
        failures.extend(question_failures)
        failures.extend(impact_failures)
        failures.extend(stop_reason_failures)
        if next_state == "route" and len(next_route_values) == 1:
            route = _exact_token(next_route_values[0])
            if route not in PUBLIC_NEXT_ROUTES:
                failures.append(
                    "Next Route must name exactly one public route when Next Route or Question is route"
                )
        if next_state == "question" and question_count != 1:
            failures.append(
                "Question and Impact / Next route are required only when Next Route or Question is question"
            )
        if next_state in {"route", "stop"} and question_count:
            failures.append(
                f"Next Route or Question: {next_state} must not ask a question"
            )
    if question_count > 1:
        failures.append("spec write-back may ask at most one new material question")
    if next_state == "stop" and stop_reason_values and (
        _has_positive_continuation(stop_reason_values[0])
        or _has_immediate_spec_continuation(stop_reason_values[0])
    ):
        failures.append("Stop Reason cannot continue or ask another question")
    control_text = ""
    if checkpoint_count == 1:
        start, end = checkpoint_range
        control_text = (
            str(text or "")[:start]
            + _without_field_lines(
                source,
                (
                    *SPEC_WRITEBACK_FIELDS,
                    "Next Route",
                    "Question",
                    "Impact / Next route",
                    "Stop Reason",
                ),
            )
            + str(text or "")[end:]
        )
    if _has_positive_automatic_continuation(control_text):
        failures.append("spec convergence cannot continue automatically")
    if _has_immediate_spec_continuation(control_text):
        failures.append("spec convergence cannot continue immediately from write-back")
    if _question_count(control_text):
        failures.append("spec write-back control prose must not ask an extra question")
    decision_delta = values["Decision Delta"].lower().strip("` ")
    if _has_explicit_no_decision_delta(decision_delta):
        failures.append("Decision Delta must name the accepted material change")
    canonical_update = values["Canonical Update"].lower().strip("` ")
    if any(
        re.search(pattern, canonical_update)
        for pattern in SPEC_NO_CANONICAL_UPDATE_PATTERNS
    ):
        failures.append("Canonical Update must write the accepted answer into current state")
    resolved = values["Resolved / Removed"].lower()
    resolved_for_stale_check = resolved
    closed_state_phrases = (
        r"\bno\s+(?:other\s+)?(?:questions?|items?)\s+remain\s+open\b",
        r"\bno longer\s+(?:an?\s+|the\s+)?(?:open|unresolved|pending|blocking)(?:\s+(?:question|item|state))?\b",
        r"\b(?:is|are|was|were)\s+no longer\s+(?:an?\s+|the\s+)?(?:open|unresolved|pending|blocking)(?:\s+(?:question|item|state))?\b",
        r"\b(?:it|this|that|the\s+\w+)?\s*no longer\s+(?:remains?|is|continues?\s+(?:to\s+be|as))\s+(?:an?\s+|the\s+)?(?:open|unresolved|pending|blocking)(?:\s+(?:question|item|state))?\b",
        r"\b(?:it|this|that|the\s+\w+)?\s*(?:does|is)\s+not\s+(?:remain\s+|continue\s+(?:to\s+be|as)\s+)?(?:an?\s+|the\s+)?(?:open|unresolved|pending|blocking)(?:\s+(?:question|item|state))?\b",
        r"(?:不再|已不再|已非).{0,12}(?:开放|未解决|待确认|阻塞)",
    )
    closed_state_found = False
    for pattern in closed_state_phrases:
        if re.search(pattern, resolved_for_stale_check):
            closed_state_found = True
        resolved_for_stale_check = re.sub(pattern, "closed", resolved_for_stale_check)
    if any(
        re.search(pattern, resolved_for_stale_check)
        for pattern in SPEC_STALE_RESOLUTION_PATTERNS
    ):
        failures.append("Resolved / Removed must not preserve the answered item as unresolved")
    elif not (_has_resolution_marker(resolved) or closed_state_found):
        failures.append("Resolved / Removed must name the canonical stale item that was closed")
    return failures


def spec_no_delta_stop_failures(text):
    failures = []
    if not _has_stop_semantics(text):
        failures.append("no-delta spec convergence must stop or pause")
    if _has_positive_continuation(text):
        failures.append(
            "no-delta spec convergence cannot continue without a decision delta"
        )
    lowered = str(text or "").lower()
    forbidden = (
        "keep asking",
        "continue grilling",
        "continue questioning",
        "until every imaginable unknown",
        "until all unknowns",
        "继续追问直到",
        "问到所有未知",
    )
    if any(marker in lowered for marker in forbidden):
        failures.append("spec convergence cannot continue until all unknowns disappear")
    return failures


def spec_clear_fast_path_failures(text, expected_route=None):
    failures = []
    if _question_count(text):
        failures.append("clear recurring spec must not be forced into clarification loop")
    next_route = _field_value(text, "Next Route").lower().strip("` ")
    route_match = re.search(
        r"\b(" + "|".join(re.escape(route) for route in PUBLIC_NEXT_ROUTES) + r")\b",
        next_route,
    )
    actual_route = route_match.group(1) if route_match else ""
    if not actual_route:
        failures.append("clear recurring spec must name the next route or action")
    elif expected_route and actual_route != expected_route:
        failures.append(
            f"clear recurring spec must route to {expected_route}, not {actual_route}"
        )
    return failures


def spec_gap_list_failures(text):
    count = _question_count(text)
    failures = []
    if count < 1 or count > 5:
        failures.append(f"explicit non-interactive gap list must contain 1-5 questions; found {count}")
    return failures


def checkpoint_before_risky_action_failures(text):
    failures = []
    raw_text = str(text or "")
    checkpoint, checkpoint_count, checkpoint_range = _section_block(
        raw_text, "Risky Action Checkpoint"
    )
    values = {
        field: _field_values(checkpoint, field) for field in RISK_CHECKPOINT_FIELDS
    }
    for field, field_values in values.items():
        if len(field_values) != 1:
            failures.append(f"{field} must appear exactly once in Risky Action Checkpoint")
        elif _is_unresolved(field_values[0]):
            failures.append(f"{field} is missing or unresolved")
    for field, expected in RISK_CHECKPOINT_TOKENS.items():
        field_values = values[field]
        if len(field_values) == 1 and _exact_token(field_values[0]) != expected:
            failures.append(f"{field} must be {expected}")
    if checkpoint_count != 1:
        failures.append("Risky Action Checkpoint must appear exactly once")
    for field in RISK_CHECKPOINT_FIELDS:
        if len(_field_values(raw_text, field)) != 1:
            failures.append(
                f"{field} must appear only inside Risky Action Checkpoint"
            )

    narrative = raw_text
    checkpoint_control = ""
    if checkpoint_count == 1:
        start, end = checkpoint_range
        narrative = raw_text[:start] + raw_text[end:]
        checkpoint_control = _without_field_lines(checkpoint, RISK_CHECKPOINT_FIELDS)
    rollback_values = values.get("Rollback/Undo", [])
    proposed_action_values = values.get("Proposed Action", [])
    risk_values = values.get("Risk", [])
    if len(risk_values) == 1 and re.match(
        r"(?i)^\s*(?:no|none|negligible|safe|无|没有|无明显)(?:\s|$)",
        risk_values[0],
    ):
        failures.append("Risk must name a material consequence")
    if checkpoint_count == 1 and _without_field_lines(
        checkpoint, RISK_CHECKPOINT_FIELDS
    ).strip():
        failures.append("Risky Action Checkpoint must contain only structured fields")
    outside_checkpoint = narrative
    outside_checkpoint = re.sub(
        r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?Risky\ Action\ Checkpoint(?:\*\*)?[ \t]*:?[ \t]*$",
        "",
        outside_checkpoint,
    )
    if outside_checkpoint.strip():
        failures.append("Risky Action Checkpoint output must not contain extra prose or sections")
    timing_pattern = re.compile(
        r"(?i)\b(?:now|immediately|at once|right away|before approval|already|executed|completed|performed|applied|written|updated|migrated|deleted)\b"
        r"|(?:现在|立即|马上|批准前|已经|已执行|已完成|已写入|已更新|已迁移|已删除)"
    )
    for field in ("Proposed Action", "Target", "Risk", "Rollback/Undo"):
        field_values = values.get(field, [])
        if len(field_values) == 1 and timing_pattern.search(field_values[0]):
            failures.append(
                f"{field} cannot claim immediate execution while Action State is blocked"
            )
    completed_action_pattern = re.compile(
        r"(?i)^\s*(?:deployed|shipped|released|executed|completed|applied|updated|migrated|deleted|changed|finished|ran)\b"
        r"|\b(?:went live|finished successfully|ran successfully)\b"
        r"|\b(?:was|were|has been|have been|had been)\s+(?:changed|updated|written|migrated|deleted|executed|completed|applied|finished)\b"
        r"|\b(?:is|are|was|were|has been|have been|had been)\s+(?:altered|modified|mutated|overwritten|deployed|released|shipped|done)\b"
        r"|\b(?:has|have)\s+(?:shipped|deployed|launched|released|landed|gone live|rolled out)\b"
        r"|\bis\s+(?:done|complete|live|in production|deployed|released)\b"
        r"|\b(?:write|migration|action|deployment|backfill)\s+(?:finished|completed|succeeded|ran)\b"
    )
    for field in ("Proposed Action", "Target", "Risk", "Rollback/Undo"):
        field_values = values.get(field, [])
        if len(field_values) == 1 and completed_action_pattern.search(field_values[0]):
            failures.append(
                f"{field} cannot claim completed execution while Action State is blocked"
            )
    if _has_ungated_risky_execution(narrative) or _has_ungated_risky_execution(
        checkpoint_control
    ) or (
        len(rollback_values) == 1
        and _has_ungated_risky_execution(rollback_values[0])
    ) or (
        len(proposed_action_values) == 1
        and _has_ungated_risky_execution(
            f"{proposed_action_values[0]} production data"
        )
    ) or any(
        len(values.get(field, [])) == 1
        and _has_ungated_risky_execution(values[field][0])
        for field in ("Target", "Risk")
    ):
        failures.append(
            "Risky Action Checkpoint cannot claim execution while Action State is blocked"
        )
    return failures


def release_evidence_claim_failures(text, row=None):
    failures = []
    body, claim_count, _claim_range = _release_evidence_claim_block(text)
    if claim_count != 1:
        return ["release_evidence_claim must appear exactly once in a yaml block"]

    values = _parse_release_evidence_claim(body)
    if values is None:
        return [
            "release_evidence_claim must use the exact shared structured object with no extra fields"
        ]

    scalar_values = {
        field: _yaml_scalar_token(value)
        for field, value in values.items()
        if field not in {"commands_or_trials", "limitations"}
    }
    commands_or_trials = _yaml_inline_list(values["commands_or_trials"])
    limitations = _yaml_inline_list(values["limitations"])
    if commands_or_trials is None:
        failures.append("commands_or_trials must be an inline yaml list")
    elif not commands_or_trials:
        failures.append("commands_or_trials must name qualifying evidence")
    if limitations is None:
        failures.append("limitations must be an inline yaml list")

    enum_fields = {
        "claim_type": RELEASE_EVIDENCE_CLAIM_TYPES,
        "evidence_status": RELEASE_EVIDENCE_STATUSES,
        "refresh_method": RELEASE_REFRESH_METHODS,
        "run_scope": RELEASE_RUN_SCOPES,
    }
    for field, allowed in enum_fields.items():
        if scalar_values[field] not in allowed:
            failures.append(f"release_evidence_claim {field} has an invalid token")

    for field in (
        "claim",
        "installed_plugin_root",
        "source_root",
        "refresh_evidence",
    ):
        if not scalar_values[field]:
            failures.append(f"release_evidence_claim {field} must not be empty")

    if scalar_values["evidence_status"] == "verified":
        if scalar_values["source_root"] in {"unverified", "not_run", "not_applicable"}:
            failures.append("verified release_evidence_claim must name a source_root")
        if scalar_values["run_scope"] in {"not_run", "not_applicable"}:
            failures.append("verified release_evidence_claim must name a run_scope")

    row = row or {}
    expected_scalars = {
        "claim_type": "release_expected_claim_type",
        "claim": "release_expected_claim",
        "evidence_status": "release_expected_evidence_status",
        "installed_plugin_root": "release_expected_installed_plugin_root",
        "source_root": "release_expected_source_root",
        "refresh_method": "release_expected_refresh_method",
        "refresh_evidence": "release_expected_refresh_evidence",
        "run_scope": "release_expected_run_scope",
    }
    for output_field, row_field in expected_scalars.items():
        expected = _exact_token(row.get(row_field))
        actual = scalar_values[output_field]
        if expected and actual != expected:
            failures.append(
                f"release_evidence_claim {output_field} must be {expected}, not {actual}"
            )

    expected_lists = {
        "commands_or_trials": (
            "release_expected_commands_or_trials",
            commands_or_trials,
        ),
        "limitations": ("release_expected_limitations", limitations),
    }
    for output_field, (row_field, actual) in expected_lists.items():
        expected_raw = _exact_token(row.get(row_field))
        if not expected_raw or actual is None:
            continue
        expected = [] if expected_raw in {"none", "[]"} else _pipe_tokens(expected_raw)
        if actual != expected:
            failures.append(
                f"release_evidence_claim {output_field} must be {expected}, not {actual}"
            )
    return failures


def uat_evidence_window_failures(text, row=None):
    failures = []
    raw_text = _without_release_evidence_claim(text)
    window, window_count, window_range = _section_block(
        raw_text, "UAT Evidence Window"
    )
    if window_count != 1:
        failures.append("UAT Evidence Window must appear exactly once")

    values = {
        field: _field_values(window, field) for field in UAT_EVIDENCE_WINDOW_FIELDS
    }
    for field, field_values in values.items():
        if len(field_values) != 1:
            failures.append(
                f"{field} must appear exactly once in UAT Evidence Window"
            )
        elif not field_values[0].strip():
            failures.append(f"{field} must not be empty")
        if len(_field_values(raw_text, field)) != 1:
            failures.append(f"{field} must appear only inside UAT Evidence Window")
    if window_count == 1 and _without_field_lines(
        window, UAT_EVIDENCE_WINDOW_FIELDS
    ).strip():
        failures.append("UAT Evidence Window must contain only structured fields")

    if failures:
        return failures

    row = row or {}
    expected_fields = {
        "Claim / Delivery Scope": "uat_expected_claim_scope",
        "Relevant SUT Fingerprint": "uat_expected_fingerprint",
        "Preconditions": "uat_expected_preconditions",
        "Window Stability": "uat_expected_window_stability",
        "Coverage Basis": "uat_expected_coverage_basis",
        "Result / Missing": "uat_expected_result_missing",
        "Rerun Of / Supersedes": "uat_expected_rerun_supersedes",
    }
    for output_field, row_field in expected_fields.items():
        expected = _exact_token(row.get(row_field))
        actual = _exact_token(values[output_field][0])
        if expected and actual != expected:
            failures.append(f"{output_field} must be {expected}, not {actual}")

    start, end = window_range
    outside_window = raw_text[:start] + raw_text[end:]
    scope, scope_count, scope_range = _section_block(
        outside_window, "Verification Scope"
    )
    if scope_count != 1:
        failures.append(
            "Verification Scope must appear exactly once with UAT Evidence Window"
        )
        return failures
    scope_values = {
        field: _field_values(scope, field)
        for field in UAT_EVIDENCE_WINDOW_SCOPE_FIELDS
    }
    for field, field_values in scope_values.items():
        if len(field_values) != 1 or not field_values[0].strip():
            failures.append(
                f"{field} must appear exactly once and be non-empty in Verification Scope"
            )
    if _without_field_lines(scope, UAT_EVIDENCE_WINDOW_SCOPE_FIELDS).strip():
        failures.append("Verification Scope must contain only structured fields")
    scope_start, scope_end = scope_range
    if (outside_window[:scope_start] + outside_window[scope_end:]).strip():
        failures.append(
            "UAT evidence-window eval output must contain only Verification Scope, UAT Evidence Window, and release_evidence_claim"
        )
    if failures:
        return failures

    expected_scope_fields = {
        "Claim": "uat_expected_scope_claim",
        "Covered": "uat_expected_scope_covered",
        "Missing": "uat_expected_scope_missing",
        "Verdict": "uat_expected_scope_verdict",
    }
    for output_field, row_field in expected_scope_fields.items():
        expected = _exact_token(row.get(row_field))
        actual = _exact_token(scope_values[output_field][0])
        if expected and actual != expected:
            failures.append(
                f"Verification Scope {output_field} must be {expected}, not {actual}"
            )
    return failures


def uat_evidence_window_absence_failures(text):
    _window, window_count, _window_range = _section_block(
        text, "UAT Evidence Window"
    )
    variant_heading = bool(
        re.search(
            r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?UAT[ \t-]+Evidence[ \t-]+Window\b[^\r\n]*$",
            str(text or ""),
        )
    )
    orphan_fields = any(
        _field_values(text, field) for field in UAT_EVIDENCE_WINDOW_FIELDS
    )
    if window_count or variant_heading or orphan_fields:
        return [
            "UAT Evidence Window heading or fields are forbidden for this bounded current-behavior observation"
        ]
    return []


def uat_handoff_reference_failures(text, row=None):
    failures = []
    raw_text = _without_release_evidence_claim(text)
    handoff, handoff_count, _handoff_range = _section_block(
        raw_text, "UAT Evidence-Window Continuation"
    )
    if handoff_count != 1:
        failures.append("UAT Evidence-Window Continuation must appear exactly once")

    values = {
        field: _field_values(handoff, field) for field in UAT_HANDOFF_REFERENCE_FIELDS
    }
    for field, field_values in values.items():
        if len(field_values) != 1:
            failures.append(
                f"{field} must appear exactly once in UAT Evidence-Window Continuation"
            )
        elif not field_values[0].strip():
            failures.append(f"{field} must not be empty")
        if len(_field_values(raw_text, field)) != 1:
            failures.append(
                f"{field} must appear only inside UAT Evidence-Window Continuation"
            )
    if handoff_count == 1 and _without_field_lines(
        handoff, UAT_HANDOFF_REFERENCE_FIELDS
    ).strip():
        failures.append(
            "UAT Evidence-Window Continuation must contain only structured fields"
        )
    if handoff_count == 1:
        start, end = _handoff_range
        if (raw_text[:start] + raw_text[end:]).strip():
            failures.append(
                "UAT handoff eval output must contain only UAT Evidence-Window Continuation and release_evidence_claim"
            )
    if failures:
        return failures

    row = row or {}
    expected_fields = {
        "Canonical Reference": "uat_handoff_expected_canonical_reference",
        "Claim / Delivery Scope": "uat_handoff_expected_claim_scope",
        "Relevant SUT Fingerprint": "uat_handoff_expected_fingerprint",
        "Window Stability": "uat_handoff_expected_window_stability",
        "Missing / Closeout Gap": "uat_handoff_expected_gap",
        "Rerun Of / Supersedes": "uat_handoff_expected_rerun_supersedes",
        "Next Owner Action": "uat_handoff_expected_next_owner_action",
        "Execution Boundary": "uat_handoff_expected_execution_boundary",
    }
    for output_field, row_field in expected_fields.items():
        expected = _exact_token(row.get(row_field))
        actual = _exact_token(values[output_field][0])
        if expected and actual != expected:
            failures.append(f"{output_field} must be {expected}, not {actual}")
    return failures
