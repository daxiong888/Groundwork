# Locale Guard

Target Reader: Groundwork skills that produce user-visible prose, artifacts, GitHub issue drafts, task summaries, PRD text, verification reports, or handoff packages.
Reader Action Needed: Preserve the user's current communication language unless the user requests otherwise.
Decision Supported: Whether output prose, headings, issue titles, issue bodies, and artifact text should be Chinese, English, or mixed.
Scope: Session locale detection, user-visible output language, template heading translation, issue/artifact language, and allowed repo-convention exceptions.
Out of Scope: Translating code identifiers, file paths, API fields, command flags, labels, product names, or source-controlled conventions unless the user asks.
Evidence Level: Based on observed Groundwork session failure where a Chinese conversation produced English `to-issues` headings and issue bodies because the skill template was written in English.
Related Issues: #31, #28, #33.

## Core Rule

User-visible language follows the current session locale. Skill-file language and example language do not override the user's language.

If the user communicates in Simplified Chinese, output Simplified Chinese prose and headings by default.

## Locale Detection

Infer `Session Locale` from the user's recent stable communication language.

Examples:

```text
简体中文用户消息 -> zh-CN
English user messages -> en-US
mixed but direct request says “请用简体中文” -> zh-CN
mixed but direct request says “write this issue in English” -> en-US for that artifact
```

If the user explicitly requests a language, that request wins for the scoped output.

## Required Behavior

### User-visible prose

Follow `Session Locale` for:

- PRD prose;
- issue titles;
- issue bodies;
- issue draft field names;
- artifact headings;
- verification report sections;
- handoff packages;
- plans and summaries;
- questions and clarifications.

### Template headings

Translate headings from skill templates when they are user-visible.

In `zh-CN`, use headings like:

```md
## Issue 集合摘要
## 来源
## Issue 草案
### 标题
### 目标
### 背景
### 验收标准
### 范围外
### 验证方式
### 缺失信息
```

Do not leak English headings such as `Issue Set Summary`, `Source`, `Goal`, or `Acceptance Criteria` into a Chinese output unless the user asks for English.

### Repo-convention exceptions

Keep these in repo convention unless the user asks to translate them:

- code identifiers;
- file paths;
- API fields;
- class, function, enum, and package names;
- CLI flags;
- branch names;
- label keys;
- product names;
- exact source excerpts;
- external tracker field names when the tracker requires them.

Example:

```md
### 验收标准
- `skills/_shared/LIFECYCLE-PREFLIGHT.md` 存在并定义 `Requirement State`。
- `git push origin main` 在 PR-bound implementation 中被阻止。
```

Chinese prose surrounds repo-convention identifiers.

## GitHub Issue Output

When drafting or creating GitHub issues:

- title follows session locale;
- body follows session locale;
- headings follow session locale;
- labels may follow repo convention;
- code blocks and exact command names remain literal;
- issue references such as `#28` remain literal.

## Artifact Output

When writing durable artifacts:

- audience-first header values follow session locale unless repo policy requires English;
- field names may be repo convention only when they are part of a stable contract;
- explanatory prose follows session locale;
- if the artifact is intended for a different audience language, state that explicitly.

## Mixed-language Handling

If mixed language is necessary, explain the split briefly:

```text
下面正文使用简体中文；代码标识符、文件路径和 CLI flags 保持仓库英文约定。
```

Do not apologize for using repo-convention identifiers.

## Skill Integration

### `to-prd`

Questions, assumptions, open questions, and acceptance criteria follow session locale.

### `to-issues`

Issue title, body, and headings follow session locale. This is the primary regression target.

### `implement`

Plan and final report follow session locale. File paths and identifiers remain literal.

### `verify`

For `verify`, the opening six-field `Verification Scope` block is a stable contract and must remain literal English. The report body and user-visible findings follow session locale. In Chinese reports, explain once that the opening field names are contract labels.

### `handoff`

Resume-ready summary follows the handoff audience language. Do not copy English templates into a Chinese handoff.

## Forbidden Behavior

- Do not infer output language from skill examples.
- Do not use English headings in Chinese issue drafts by default.
- Do not translate code identifiers in a way that breaks searchability.
- Do not switch languages mid-response unless quoting source text or preserving repo convention.
- Do not treat English repo docs as a request for English user-visible output.
