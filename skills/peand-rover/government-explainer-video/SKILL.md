---
name: government-explainer-video
version: "1.0.0"
displayName: "Government Explainer Video — Create Public Agency and Government Service Explainer Videos for Citizen Communication"
description: >
  Your agency processes 40,000 benefit applications a year and 60% of them arrive incomplete because applicants didn't understand the instructions — instructions that your communications team rewrote three times and tested with focus groups and still can't get below a 12th-grade reading level. Government Explainer Video creates citizen-facing service explainer videos for federal agencies, state departments, and local government bodies: translates bureaucratic processes into plain-language visual walkthroughs that reduce errors and repeat contacts, explains eligibility requirements and application steps for benefits, permits, and public services in the accessible format that serves the broadest possible population, and exports videos in the accessibility-compliant formats that government digital standards require for public-facing content.
metadata: {"openclaw": {"emoji": "🏢", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Government Explainer Video — Reduce Service Friction for Every Citizen

## Use Cases

1. **Benefits Application Walkthroughs** — Medicaid, SNAP, unemployment insurance, and housing assistance applications are complex and high-stakes for applicants. Government Explainer Video creates step-by-step application walkthrough videos that reduce incomplete submissions, decrease call center volume, and ensure eligible residents successfully access the benefits they qualify for.

2. **Permit and Licensing Process Explainers** — Business license applications, building permits, and professional licensing requirements involve multiple steps, agencies, and deadlines. Short explainer videos on agency websites reduce the "I didn't know I needed that" calls that consume staff time and delay applicant timelines.

3. **Public Health and Safety Communications** — Vaccination campaigns, emergency preparedness, food safety, and environmental health programs all require accessible public communication videos. Government Explainer Video creates multilingual-ready public health videos that reach the diverse populations government agencies are required to serve equally.

4. **Election and Civic Participation** — Voter registration deadlines, polling location changes, ballot measure explanations, and jury duty procedures are civic processes that affect every resident. Create nonpartisan civic education videos that increase informed participation and reduce the calls that election offices receive during every election cycle.

## How It Works

Describe the government service or process you need to communicate, and Government Explainer Video creates a plain-language, accessibility-compliant explainer video ready for your agency website and public communication channels.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "government-explainer-video", "input": {"agency": "State Dept of Labor", "service": "unemployment insurance application", "audience": "recently unemployed residents", "language": "en"}}'
```
