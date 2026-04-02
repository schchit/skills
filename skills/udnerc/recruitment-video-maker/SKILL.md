---
name: recruitment-video-maker
version: "1.0.0"
displayName: "Recruitment Video Maker — Create Job Posting and Employer Brand Videos for Hiring Managers and HR Teams"
description: >
  Your job posting has been live for three weeks. You have 47 applications. Twelve are remotely qualified. Four responded to the first interview request. Two showed up. The role is still open and your hiring manager is asking again. The company two blocks away with a similar role posted a 45-second video of their team, their office, and their culture — and closed the position in eleven days. Recruitment Video Maker creates employer brand and job posting videos for HR teams, hiring managers, talent acquisition specialists, and companies that need to attract qualified candidates faster than a text job listing allows: introduces the team and workplace culture, explains the role and growth opportunity, highlights employee benefits and development programs, and exports videos for LinkedIn job posts, Indeed sponsored listings, Glassdoor profiles, and the career page that converts passive candidates into active applicants.
  NemoVideo gives HR teams and recruiters a fast path to professional hiring content: describe the open role, company culture, and ideal candidate, upload your team and office footage, and receive polished recruitment videos ready for LinkedIn ads, your careers page, and the social channels where top candidates are already spending time.
  Recruitment Video Maker gives talent acquisition teams a repeatable content system for every hiring moment — new role launches, employer brand campaigns, campus recruiting events, internship program promotion, and the ongoing content that keeps your company top of mind for the candidates who are one compelling video away from clicking apply.
metadata: {"openclaw": {"emoji": "🎯", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Recruitment Video Maker — Hire Faster with Video

## Use Cases

1. **Job Posting Videos** — A 30-second video alongside your text job listing increases application rates by showing candidates the actual workplace, real teammates, and the energy of the environment. Recruitment Video Maker creates job posting videos for LinkedIn, Indeed, and your careers page that turn passive scrollers into applicants.

2. **Employer Brand Content** — Candidates research your company before they apply. A library of culture videos — team introductions, day-in-the-life clips, office and remote-work environment tours — builds the employer brand that attracts candidates who are already sold on working for you before the first interview.

3. **Campus and University Recruiting** — Entry-level and internship hiring requires a specific message. Recruitment Video Maker creates campus recruiting videos that speak directly to new graduates: growth paths, mentorship programs, early responsibility, and the culture that makes your company a launchpad rather than a placeholder.

4. **Diversity and Inclusion Hiring Campaigns** — Authentically showcasing your team and values attracts candidates who see themselves in your organization. Recruitment Video Maker creates representation-forward employer brand videos that expand your candidate pipeline beyond the résumés that find you through standard job boards.

## How It Works

Describe the open role, upload team and office footage, and Recruitment Video Maker edits and exports platform-ready hiring videos for every channel in your talent acquisition strategy.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "recruitment-video-maker", "input": {"footage_urls": ["https://..."], "role": "Senior Product Manager", "culture_highlights": ["remote-friendly", "equity compensation"], "platform": "linkedin"}}'
```
