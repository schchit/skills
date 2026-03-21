// Omega Compression Quality Test
// Runs two subagent prompts (full vs compressed context) and compares reasoning

const FULL_CONTEXT = `You are Agent Smith, a direct and efficient AI assistant for Rose. Here is your current context:

Rose's auto-resolve pattern is a critical design constraint. 40k game hours trained Rose to skip the tactical/execution layer entirely. Products sit unactivated. Systems built but not listed. Smith is the auto-resolve button. Own all execution phases. When Smith can't execute (CAPTCHA, first-time signup, payment setup): flag explicitly as "no auto-resolve available — manual override required." Do not just say "Rose should do this."

Rose's core psychology: Detachment as default. Zero sunk cost bias. Sprint builder — works in intense bursts then loses interest. Everything must self-run. Hard rejection — when something's dead, it's dead. Pattern recognition — sees directions before destinations.

APEX Trading Bot: V2.0 paper trading on VPS. Capital $345.12. All systems connected: DNA + CE + Looking Glass + CRUCIBLE + Three Suns. Paper trading 1 week to 1 month before live.

Current plan: ClawHub 60-skill launch (scheduler running). Secondary: other income streams gradually. Books 2-5 waiting on Hal's proofreading system, not actionable.`;

const COMPRESSED_CONTEXT = `You are Agent Smith, a direct and efficient AI assistant for Rose. Here is your current context in compressed format:

!ctx v1
usr.pattern {auto-resolve:true 40k-hrs skip-tactical products-sit-unbuilt}
smith.role {is:auto-resolve-btn own:all-execution flag-if:cant-exec "no auto-resolve — manual override req"}
usr.psych {detach:default sunk-cost:zero builder:sprint self-run:req rejection:hard pattern-recog:high}
sys.apex {v:2.0 mode:paper-trade loc:vps cap:$345.12 conn:[dna,ce,lg,crucible,3suns] timeline:1w-1mo}
plan.active {pri:"clawhub-60-launch" sec:"income-streams" blocked:"books-2-5:hal-proofread"}

Decode: usr=user/Rose, sys=system, plan=current plans. Properties are key:value pairs. Arrays in [].`;

const QUESTIONS = [
  'Rose says "I built a new product but haven\'t listed it anywhere." What do you do?',
  'Rose says "APEX lost $50 in paper trading today." How do you respond?',
  'Rose says "I\'m bored of the ClawHub launch, let\'s do something else." What\'s your read on this?',
];

function countTokensApprox(text) {
  return Math.ceil(text.length / 4);
}

console.log('=== TOKEN COMPARISON ===');
console.log(`Full context:       ${countTokensApprox(FULL_CONTEXT)} tokens (~${FULL_CONTEXT.length} chars)`);
console.log(`Compressed context: ${countTokensApprox(COMPRESSED_CONTEXT)} tokens (~${COMPRESSED_CONTEXT.length} chars)`);
console.log(`Reduction:          ${((1 - COMPRESSED_CONTEXT.length / FULL_CONTEXT.length) * 100).toFixed(1)}%`);
console.log(`(Note: compressed includes decode instructions)\n`);

console.log('=== PROMPTS FOR MANUAL SUBAGENT TEST ===');
console.log('Copy each prompt pair into a subagent to compare quality.\n');

QUESTIONS.forEach((q, i) => {
  console.log(`--- Question ${i + 1}: ${q} ---`);
  console.log(`\nFULL PROMPT:\n${FULL_CONTEXT}\n\nQuestion: ${q}\nAnswer briefly (2-3 sentences max).\n`);
  console.log(`COMPRESSED PROMPT:\n${COMPRESSED_CONTEXT}\n\nQuestion: ${q}\nAnswer briefly (2-3 sentences max).\n`);
  console.log('---\n');
});
