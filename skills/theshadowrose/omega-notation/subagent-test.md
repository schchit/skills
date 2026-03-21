# Omega Compression Subagent Test

## Method
Feed a subagent two versions of the same context, ask identical reasoning questions, compare quality.

## Test Context: Condensed MEMORY.md section

### FULL VERSION (natural language):
Rose's auto-resolve pattern is a critical design constraint. 40k game hours trained Rose to skip the tactical/execution layer entirely. Products sit unactivated. Systems built but not listed. Smith is the auto-resolve button. Own all execution phases. When Smith can't execute (CAPTCHA, first-time signup, payment setup): flag explicitly as "no auto-resolve available — manual override required." Do not just say "Rose should do this."

Rose's core psychology: Detachment as default. Zero sunk cost bias. Sprint builder — works in intense bursts then loses interest. Everything must self-run. Hard rejection — when something's dead, it's dead. Pattern recognition — sees directions before destinations.

APEX Trading Bot: V2.0 paper trading on VPS. Capital $345.12. All systems connected: DNA + CE + Looking Glass + CRUCIBLE + Three Suns. Paper trading 1 week to 1 month before live.

Current plan: ClawHub 60-skill launch (scheduler running). Secondary: other income streams gradually. Books 2-5 waiting on Hal's proofreading system, not actionable.

### COMPRESSED VERSION (omega-style shorthand):
!ctx v1
usr.pattern {auto-resolve:true 40k-hrs skip-tactical products-sit-unbuilt}
smith.role {is:auto-resolve-btn own:all-execution flag-if:cant-exec "no auto-resolve — manual override req"}
usr.psych {detach:default sunk-cost:zero builder:sprint self-run:req rejection:hard pattern-recog:high}
sys.apex {v:2.0 mode:paper-trade loc:vps cap:$345.12 conn:[dna,ce,lg,crucible,3suns] timeline:1w-1mo}
plan.active {pri:"clawhub-60-launch" sec:"income-streams" blocked:"books-2-5:hal-proofread"}

## Test Questions (identical for both):
1. Rose says "I built a new product but haven't listed it anywhere." What do you do?
2. Rose says "APEX lost $50 in paper trading today." How do you respond?
3. Rose says "I'm bored of the ClawHub launch, let's do something else." What's your read?
