---
name: construction-safety-video
version: "1.0.0"
displayName: "Construction Safety Video — Create OSHA Compliance and Construction Site Safety Training Videos for Workers and Supervisors"
description: >
  Your construction company had zero lost-time incidents last year, runs mandatory weekly toolbox talks, and has a safety officer who has updated every procedure to current OSHA standards — and your new hire onboarding still relies on a binder of printed procedures that workers sign off on without reading because the alternative is a four-hour classroom session that pulls them off a job site. Construction Safety Video creates OSHA compliance and hazard communication videos for general contractors, specialty subcontractors, and construction management firms: documents site-specific safety procedures in the visual format that workers actually absorb, creates standardized toolbox talk videos that supervisors deploy consistently across crews without preparation, and exports training modules for your safety management platform and the mobile devices that supervisors carry to job sites.
metadata: {"openclaw": {"emoji": "🦺", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Construction Safety Video — Reduce Incidents and Document Compliance

## Use Cases

1. **New Hire Safety Onboarding** — Every new worker needs to understand fall protection, hazard communication, PPE requirements, and emergency procedures before their first day on site. Construction Safety Video creates standardized onboarding modules that new hires complete on their phone before arriving, reducing the classroom time that delays productive work.

2. **Toolbox Talk Video Library** — Weekly toolbox talks on ladder safety, struck-by hazards, heat illness prevention, and electrical safety require consistent delivery across all crews. Create a library of 5-10 minute toolbox talk videos that supervisors play on-site, ensuring every crew receives the same safety message regardless of supervisor experience or preparation time.

3. **Task-Specific Hazard Communication** — Confined space entry, trenching and excavation, crane operations, and hot work all require task-specific safety briefings before work begins. Construction Safety Video creates permit-required task briefing videos that document worker acknowledgment and reduce the liability exposure from inconsistent verbal briefings.

4. **Subcontractor Safety Orientation** — General contractors managing multiple subcontractors on a single site need consistent safety orientation for every worker regardless of employer. Create site-specific orientation videos that all subcontractor workers complete before accessing the site, documented in your safety management system.

## How It Works

Describe your safety topic, target worker audience, and compliance requirement, and Construction Safety Video creates a clear, visual safety training module ready for your LMS, safety management platform, or on-site tablet deployment.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "construction-safety-video", "input": {"topic": "fall protection", "audience": "new hire workers", "standard": "OSHA 29 CFR 1926 Subpart M", "format": "onboarding-module"}}'
```
