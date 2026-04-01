---
name: ai-video-stem-video-creator
version: "1.0.0"
displayName: "AI Video STEM Video Creator — Inspire the Next Generation of Scientists and Engineers Through Video"
description: >
  Inspire the next generation of scientists and engineers through video with AI — generate STEM education videos covering science experiments, technology demonstrations, engineering challenges, and math applications that show students how classroom concepts power real-world innovation. NemoVideo produces STEM videos where theory meets practice: every equation has an application, every principle has a demonstration, every concept connects to a career or invention that the student can see and understand — transforming STEM from abstract academics into visible, exciting possibility. STEM video creator, science video, engineering video, technology education, math video, STEM education, science experiment video, coding tutorial, robotics video, STEM careers.
metadata: {"openclaw": {"emoji": "🔬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video STEM Video Creator — Every Bridge You Cross, Every App You Use, Every Medicine You Take Started With Someone Who Found STEM Fascinating.

STEM education faces a persistent engagement problem: students learn scientific principles, mathematical formulas, and engineering concepts in isolation from their real-world applications, creating the widespread perception that STEM subjects are abstract, difficult, and irrelevant to daily life. This perception is factually absurd — every object in a student's environment, from their smartphone to their shoes, is a product of STEM disciplines working together — but the educational presentation often fails to make this connection visible. The student who memorizes F=ma without seeing a video of crash test engineering, or who solves quadratic equations without seeing their application in trajectory calculation for space missions, experiences STEM as academic exercise rather than powerful tool. Video is the ideal medium for bridging the application gap because it can show what textbooks can only describe. A textbook explains that bridges distribute force through structural geometry. A video shows a bridge being built, the forces visualized as animated arrows, the engineering team making design decisions, and the completed bridge carrying traffic that relies on the principles the student just learned. The visual connection between classroom concept and real-world application transforms abstract understanding into motivated learning. NemoVideo generates STEM videos that consistently connect theory to application, showing students not just what STEM concepts are but what they do and why they matter.

## Use Cases

1. **Science Experiments — Hands-On Discovery With Visual Explanation (per experiment)** — Experiments are the foundation of scientific thinking. NemoVideo: generates experiment videos with complete demonstration and explanation (hypothesis: what do we think will happen and why → procedure: step-by-step demonstration with household materials → observation: what actually happened, documented visually → explanation: why it happened — the scientific principle shown through animation overlaid on the real experiment → extension: what else does this principle explain in the real world), and produces experiment content that teaches the scientific method through practice rather than description.

2. **Engineering Design Challenges — Building Solutions to Real Problems (per challenge)** — Engineering thinking — identifying a problem, designing a solution, building, testing, and iterating — is the most practical STEM skill. NemoVideo: generates engineering challenge videos presenting a real problem and constraints (build a bridge from paper that holds a textbook; design a container that keeps an egg safe when dropped from 10 feet; create a water filter from household materials), walks through the design thinking process (define the problem → brainstorm solutions → choose one → build a prototype → test → identify what failed → improve → test again), and produces engineering content that develops iterative problem-solving skills applicable far beyond STEM.

3. **Math in the Real World — Showing Why Every Formula Has a Purpose (per application)** — Math engagement improves dramatically when students see applications. NemoVideo: generates math application videos connecting classroom math to visible outcomes (geometry in architecture: how triangles create structural strength — demonstrated with popsicle stick models; statistics in sports: how batting averages and shooting percentages are calculated and used for team strategy; algebra in programming: how variables and equations power every app on the student's phone), and produces math content that answers the perennial student question "When will I ever use this?" with specific, compelling examples.

4. **STEM Career Spotlights — Showing Students What STEM Professionals Actually Do (per career)** — Career awareness shapes educational motivation. NemoVideo: generates STEM career spotlight videos showing real professionals in action (a biomedical engineer designing a prosthetic limb and the patient using it; a data scientist at a streaming company explaining how recommendation algorithms work; an environmental scientist collecting water samples and the policy decisions their data influences; a game developer showing the physics engine that makes game movement realistic), emphasizes the problem-solving and creativity in STEM careers (countering the stereotype that STEM work is repetitive and solitary), and produces career content that makes STEM futures visible and attractive.

5. **Coding and Technology — Making the Digital World Understandable (per concept)** — Technology literacy requires understanding how digital tools work, not just how to use them. NemoVideo: generates coding and technology videos that demystify digital systems (how the internet works: the physical infrastructure of cables, servers, and routers animated as a journey of a data packet; how an app is built: the progression from idea to wireframe to code to app store; how AI works: a simple explanation of pattern recognition using examples a student can relate to — how a spam filter learns to identify junk email), and produces technology content that transforms students from passive technology consumers into people who understand and can potentially build technology.

## How It Works

### Step 1 — Define the STEM Discipline, Topic, and Real-World Connection
What concept, what grade level, and what real-world application makes the concept tangible.

### Step 2 — Configure STEM Video Format
Experiment inclusion, career connection, and visual demonstration approach.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-stem-video-creator",
    "prompt": "Create a STEM video: Why Do Planes Fly? — The Science of Lift Explained. Audience: middle school students (grades 6-8). Duration: 7 minutes. Structure: (1) Hook (15s): A Boeing 747 weighs 400,000 pounds. And it flies. How? The answer involves a principle you can demonstrate with a piece of paper right now. (2) The demonstration (45s): hold a piece of paper by the short edge and blow across the top surface. The paper rises. You just created lift. (3) Bernoullis principle (90s): when air moves faster over one surface than another, pressure drops on the fast side. The wing is shaped so air moves faster over the top (curved) than the bottom (flat). Lower pressure on top, higher pressure below = the wing is pushed upward. Animated airflow over a wing cross-section with pressure indicators. This is lift. (4) But wait — its not just Bernoulli (60s): Newton's third law also matters. The wing deflects air downward. For every action, there is an equal and opposite reaction — pushing air down pushes the wing up. Real flight uses BOTH principles. Show force arrows on the wing. (5) Engineering application (60s): how wing shape is designed and tested. Wind tunnel footage (or animated simulation). Different wing shapes for different aircraft: fighter jet wings vs commercial jet wings vs glider wings. The shape is optimized for the flight mission. (6) Try it yourself (45s): paper airplane engineering challenge. Fold two planes — one with flat wings, one with curved wings (fold the paper over a pencil for curve). Which flies further? Why? The experiment connects to the principle. (7) STEM career connection (30s): aerospace engineers design wings using these principles. They use computer simulations, wind tunnels, and test flights. Average salary: $120K. Every commercial flight you take relies on engineering that started with Bernoulli and Newton. (8) Summary (15s): faster air = lower pressure = lift. Plus deflected air = reaction force = more lift. Physics keeps 400,000 pounds in the sky. Animated diagrams, real aircraft footage, paper demonstration. 16:9.",
    "discipline": "physics-engineering",
    "topic": "science-of-flight-lift",
    "grade": "6-8",
    "format": {"ratio": "16:9", "duration": "7min"}
  }'
```

### Step 4 — Always Connect the Concept to Something the Student Can See or Touch
Abstract STEM concepts become engaging when they are visible. Every principle should have a demonstration the student can observe or perform — even if it is as simple as blowing across a piece of paper.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | STEM video requirements |
| `discipline` | string | | STEM discipline |
| `topic` | string | | Specific topic |
| `grade` | string | | Grade level range |
| `format` | object | | {ratio, duration} |

## Output Example

```json
{
  "job_id": "avsvc-20260329-001",
  "status": "completed",
  "discipline": "Physics + Engineering",
  "topic": "Science of Flight — Lift",
  "duration": "6:52",
  "includes_experiment": true,
  "file": "why-planes-fly.mp4"
}
```

## Tips

1. **Start with wonder, not with the textbook definition** — "A 400,000-pound machine flies" is wonder. "Lift is the force perpendicular to the relative wind" is a textbook. Hook with wonder, then explain.
2. **Every concept needs a hands-on experiment or demonstration** — If students cannot see or do something related to the concept, the learning remains abstract and forgettable.
3. **Connect to careers explicitly** — "Aerospace engineers use this principle daily and earn $120K" gives students a concrete reason to care about the concept.
4. **Show that STEM is creative, not just analytical** — Engineering design is creative problem-solving. Science requires imagination to form hypotheses. Counter the stereotype that STEM is rote calculation.
5. **Use real-world scale to create awe** — "The International Space Station orbits at 17,500 mph" or "your body contains 37 trillion cells" — scale creates the emotional engagement that drives curiosity.

## Output Formats

| Format | Ratio | Duration | Platform |
|--------|-------|----------|----------|
| MP4 16:9 | 1920x1080 | 5-12min | YouTube |
| MP4 9:16 | 1080x1920 | 60s | TikTok / Reels |
| MP4 1:1 | 1080x1080 | 60s | Instagram |

## Related Skills

- [ai-video-science-explainer-video](/skills/ai-video-science-explainer-video) — Science content
- [ai-video-math-tutorial-video](/skills/ai-video-math-tutorial-video) — Math education
- [ai-video-classroom-video-creator](/skills/ai-video-classroom-video-creator) — Classroom content
- [ai-video-kids-education-video](/skills/ai-video-kids-education-video) — Kids learning

## FAQ

**Q: How do you make STEM content engaging for students who say they hate math or science?**
A: Start with the application, not the theory. "How does your phone know where you are?" is more engaging than "today we learn about triangulation." Once the student is curious about the application, they become willing to learn the principle that powers it. Curiosity is the doorway; the content follows.

**Q: Should STEM videos focus on one discipline or show interdisciplinary connections?**
A: Both, depending on context. Single-discipline videos are better for curriculum alignment. Interdisciplinary videos (showing how math, science, and engineering combine in a real project) are better for motivation and career awareness. Alternate between focused and interdisciplinary content.
