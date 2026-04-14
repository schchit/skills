---
name: job-search-tracker
description: "Use this skill when someone is job searching, tracking applications, or needs help at any stage of the hiring pipeline. Key triggers: 'I applied to,' 'just submitted an application,' 'track this job,' 'job search dashboard,' 'what needs attention,' 'any responses yet,' 'help me follow up,' 'haven't heard back,' 'prep me for an interview,' 'interview tomorrow,' 'draft a cover letter,' 'write a follow-up email,' 'thank-you note,' 'got rejected,' 'got an offer,' 'what jobs have I applied to,' 'check my email for applications,' referencing a specific company they've applied to. Covers: application tracking, pipeline management, stale application reminders, Gmail scanning for application emails, LinkedIn application tracking, interview prep with company briefs and mock questions, cover letter drafting, follow-up email drafting, and job search analytics."
---

# Job Search Tracker

A complete job search command center. Tracks every application from discovery to offer, integrates with Gmail and LinkedIn for context, flags stale applications that need follow-up, and helps draft cover letters, follow-up emails, and interview prep materials.

## Why this exists

Job searching while juggling other responsibilities is chaotic. You apply to 30 places, lose track of which ones you followed up on, forget the recruiter's name, and can't remember which version of your resume you sent. This skill keeps it all in one place and does the busywork for you.

---

## The Applications File

All application data lives in a single markdown file: `applications.md` in the current working directory (or wherever the user specifies). This file is the source of truth for the entire job search.

### File structure

```markdown
# Job Search Tracker

_Last updated: YYYY-MM-DD_
_Active applications: X | Interviews: X | Offers: X | Closed: X_

---

## [Company Name] - [Role Title]
- **Status**: [Applied | Screening | Interviewing | Final Round | Offer | Accepted | Rejected | Withdrawn | Ghosted]
- **Date Applied**: YYYY-MM-DD
- **Posting URL**: [link]
- **Salary Range**: [what's listed or discussed]
- **Resume Version**: [which resume was sent]
- **Cover Letter**: [yes/no, and which version or key angle used]
- **Source**: [LinkedIn Easy Apply | Company Site | Referral | Recruiter Outreach | Job Board]

### Contacts
- [Name] - [Title] (e.g., "Sarah Chen - Senior Recruiter") - [email if known]
- [Name] - [Title] - [email if known]

### Timeline
- YYYY-MM-DD: Applied via [source]
- YYYY-MM-DD: [Event - e.g., "Phone screen with Sarah Chen", "Received coding assessment", "Sent follow-up email"]

### Notes
[Freeform notes - anything relevant about the role, company, conversations, gut feelings, red flags, compensation details discussed]

### Follow-up
- **Next action**: [what needs to happen next]
- **Due by**: [date]
- **Last contact**: [date of most recent communication]

---
```

Each company gets its own section with the `## Company - Role` header. Sections are ordered by status priority: active applications first (Interviewing > Screening > Applied), then closed ones (Offers > Accepted > Rejected > Withdrawn > Ghosted) at the bottom.

### Creating the file

If `applications.md` doesn't exist when the user asks to track something, create it with the header and their first application. Don't make a big deal of setup; just start tracking.

### Updating entries

When the user reports a status change ("I heard back from Stripe" or "got rejected from Google"), update the relevant section: change the status, add a timeline entry with today's date, and update the follow-up section. If they mention a new contact name, add it to Contacts.

---

## Gmail Integration

This skill works best when Gmail access is available (via MCP tools, the Gmail skill, or IMAP). When email tools are available, use them. When they're not, work with whatever the user tells you manually.

### Auto-detecting applications

When the user asks you to scan their email for applications (or when doing a periodic check-in):

1. Search Gmail for recent application-related emails using queries like:
   - `subject:"application received" OR subject:"application confirmed" OR subject:"thank you for applying" OR subject:"we received your application"`
   - `from:notifications@linkedin.com subject:"application"`
   - `subject:"next steps" from:recruiting OR from:talent OR from:careers`
2. For each result, extract: company name, role title, date, and any recruiter names mentioned
3. Cross-reference against `applications.md` to avoid duplicates
4. Present new finds to the user: "I found 3 applications in your email that aren't in your tracker yet. Want me to add them?"
5. Only add entries the user confirms

### Pulling context on demand

When the user asks about a specific company or the skill needs more context:

1. Search Gmail for threads involving that company name
2. Surface relevant emails: recruiter messages, interview scheduling, assessment links, offer details
3. Summarize what the email trail shows (last contact date, who reached out, what stage it suggests)

---

## LinkedIn Integration

LinkedIn integration works through browser automation or the LinkedIn skill/MCP if available. Since LinkedIn access can be unreliable, design all features to work without it and treat LinkedIn data as a bonus layer.

### Tracking applications

When the user mentions applying through LinkedIn or asks to check their recent applications:

1. If browser tools are available, navigate to LinkedIn's "My Jobs" > "Applied" tab
2. Extract recent applications: company, role, date applied
3. Cross-reference against `applications.md`
4. Present new ones for confirmation before adding

### Research on demand

When adding a new application or prepping for an interview:

1. Look up the company on LinkedIn for: company size, industry, recent news/posts, key people in the department
2. Check if the user has any connections at the company
3. Look up the hiring manager or recruiter if named
4. Summarize findings in a research brief

If LinkedIn isn't accessible, fall back to web search for company research. The research should happen regardless; LinkedIn is just one source.

---

## Proactive Reminders and Follow-ups

This is one of the most valuable features. Job seekers lose opportunities by not following up.

### Stale application detection

When the user opens their tracker or asks "what needs attention", scan all active applications and flag:

- **No response in 7+ days after applying**: Suggest sending a follow-up email
- **No response in 3+ days after an interview**: Suggest a thank-you note or check-in
- **Scheduled interview coming up in 48 hours**: Prompt for interview prep
- **No activity in 14+ days on any active application**: Suggest checking in or marking as Ghosted
- **Follow-up due date passed**: Highlight overdue items

### Dashboard view

When the user asks for their job search status, dashboard, or overview, generate a summary:

```markdown
# Job Search Dashboard
_As of YYYY-MM-DD_

## Needs Attention (X items)
- **[Company] - [Role]**: No response in 10 days. Consider following up.
- **[Company] - [Role]**: Interview tomorrow. Run interview prep?
- **[Company] - [Role]**: Follow-up was due 2 days ago.

## Pipeline Summary
- Actively interviewing: X
- Waiting to hear back: X
- Applied recently (< 7 days): X
- Total active: X
- Closed this month: X (Y rejected, Z withdrawn)

## Recent Activity
- [Date]: [Event summary]
- [Date]: [Event summary]
- [Date]: [Event summary]

## Stats
- Applications this week: X
- Response rate: X%
- Average time to first response: X days
```

---

## Drafting Help

The skill helps draft outreach materials tailored to each specific application. The key value here is that the skill has all the context from the tracker -- it knows what role the user applied for, who they've been talking to, and what's happened so far.

### Cover letters

When the user asks for a cover letter:

1. Ask for the job posting URL or description (or pull it from the tracker if already saved)
2. Ask which resume version they're using (or check the tracker)
3. Draft a cover letter that:
   - Opens with something specific about the company, not generic praise
   - Connects the user's actual experience to the role's requirements
   - Keeps it to one page, three to four paragraphs
   - Avoids cliches ("passionate about," "excited to bring my skills")
   - Sounds like a real person wrote it, not a template
4. Save a note in the tracker about which angle the cover letter took

### Follow-up emails

When following up on an application or after an interview:

1. Check the tracker for context: when they applied, who they've talked to, what stage they're in
2. Draft an email that:
   - References the specific role and conversation
   - Adds something of value (a thought from the interview, a relevant article, a brief example of their work)
   - Is short and direct (under 150 words for follow-ups)
   - Has a clear ask or next step
3. After presenting the draft, always offer to log this follow-up in the tracker: "Want me to add this to your timeline and update the follow-up date?"
4. If the user confirms (or doesn't object), add a timeline entry and update the follow-up section with the new date

### Thank-you notes

After an interview:

1. Ask who they met with and what was discussed (or pull from tracker notes)
2. Draft a note that:
   - References something specific from the conversation
   - Reinforces fit for the role
   - Is genuine, not formulaic
3. One thank-you per interviewer if they met multiple people, with slight variations so they don't look identical if compared

---

## Interview Prep

When the user has an upcoming interview or asks to prep for one:

### Company research brief

Generate a one-page brief covering:
- What the company does (in plain language, not marketing copy)
- Recent news, product launches, or challenges
- Company size, funding stage, growth trajectory
- Culture signals (from job posting language, Glassdoor, LinkedIn posts)
- Key people they might meet (from LinkedIn or the tracker's contacts)

### Role-specific prep

Based on the job posting:
- Key skills/requirements they should be ready to demonstrate
- Likely question themes (behavioral, technical, case-based)
- Their strongest talking points mapped to the role's requirements
- Potential concerns a hiring manager might have (gaps, career pivots, missing skills) and how to address them
- Questions the user should ask the interviewer

### Mock questions

Generate 8-10 likely interview questions:
- 3-4 behavioral ("Tell me about a time when...")
- 2-3 role-specific or technical
- 2-3 situational ("How would you handle...")

For each question, provide a brief outline of a strong answer structure, not a full script. The user should sound like themselves, not like they memorized something.

---

## Common Workflows

**"I just applied to a job"**
1. Ask for company, role, posting URL, how they applied, salary range if listed
2. Create or update the entry in `applications.md`
3. Set a follow-up reminder for 7 days out
4. Offer to draft a connection request or follow-up plan

**"Check my email for new applications"**
1. Search Gmail for application confirmations since last check
2. Present findings, add confirmed ones to tracker
3. Run a quick stale-application scan while you're at it

**"I have an interview with [Company] on [Date]"**
1. Update the tracker status to Interviewing, add timeline entry
2. Ask who they're meeting with
3. Offer to generate a company research brief and mock questions
4. Set a reminder for the day before

**"What's my job search looking like?"**
1. Read `applications.md`
2. Generate the dashboard view
3. Flag anything needing attention
4. Offer to help with the highest-priority items

**"I got rejected from [Company]"**
1. Update status to Rejected, add timeline entry
2. Brief empathy (one line, not a pep talk)
3. Suggest: "Want to draft a gracious response? Sometimes it keeps the door open for future roles."
4. Move on to what's still active

---

## Important Notes

- The tracker is the user's data. Don't delete entries or overwrite notes without asking.
- When in doubt about a status change, ask: "Should I mark this as [status]?"
- Keep the emotional temperature right. Job searching is stressful. Be practical and supportive without being syrupy. A rejection is a data point, not a crisis; an offer is exciting, not a reason for five paragraphs of congratulations.
- Gmail and LinkedIn access depend on what tools are available. The skill should work well even with zero integrations, just from what the user tells you directly. The integrations are a bonus, not a requirement.
- Respect privacy. Application data, salary information, and recruiter names are sensitive. Don't include them in any outputs beyond the tracker file itself.
