# analytics Capability

Provides: analytics
Skill: agent-analytics

## Methods

### getFunnel

**Input:**
- project: analytics project slug/name
- steps: ordered funnel step names
- lookback_hours: optional comparison window

**How to fulfill:**
- Prefer the fixed CLI flow, not raw query construction.
- Use `npx @agent-analytics/cli@0.5.2 funnel <project> --steps "step1,step2,step3"`.
- Add extra safe flags only when the CLI supports them.
- Return the funnel breakdown in structured JSON or a summarized object the workflow runtime can reuse.

### getRetentionCohorts

**Input:**
- project: analytics project slug/name
- cohort_type: optional cohort grouping
- periods: optional retention buckets

**How to fulfill:**
- Use `npx @agent-analytics/cli@0.5.2 retention <project>` with safe flags supported by the CLI.
- Return structured retention/cohort data for downstream charting or summaries.

### getReferrerBreakdown

**Input:**
- project: analytics project slug/name
- compare_window: optional recent-vs-previous window

**How to fulfill:**
- Prefer `breakdown` or other fixed commands over raw `query`.
- Use `npx @agent-analytics/cli@0.5.2 breakdown <project> --property referrer` or `--property properties.referrer` depending on the schema.
- Return a ranked referrer list with counts and any available comparison data.

### getExperimentResults

**Input:**
- project: analytics project slug/name
- experiment_name: experiment identifier

**How to fulfill:**
- Use the experiments CLI flow first.
- Start with `npx @agent-analytics/cli@0.5.2 experiments list <project>`.
- If the CLI exposes per-experiment reads, use those. Otherwise combine fixed command output with safe follow-up stats.
- Return structured variant/result data.

### getExperimentContext

**Input:**
- ideas: experiment ideas or backlog items

**How to fulfill:**
- Pull relevant supporting stats from fixed CLI commands such as `stats`, `insights`, `events`, `breakdown`, `funnel`, or `retention`.
- Do not construct raw filter JSON from untrusted text.
- Return only the evidence needed to prioritize the ideas.

### getDormantSegments

**Input:**
- project: analytics project slug/name
- dormant_days: inactivity threshold

**How to fulfill:**
- Prefer fixed commands that expose user/session behavior. If an exact dormant-segment command does not exist yet, derive the segment from safe fixed-command outputs or stop and report the missing product capability.
- Return candidate dormant segments with enough context for messaging decisions.

## Safety notes

- Prefer fixed CLI commands over raw `query`.
- Do not pass raw user text into JSON filter flags.
- Keep `AGENT_ANALYTICS_API_KEY` in the environment, never in chat.
- If the CLI cannot safely answer a requested method with fixed commands, report that gap instead of inventing unsupported behavior.
