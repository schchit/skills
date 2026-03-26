---
name: psych-quiz
description: Provide short, low-risk self-check quizzes for common mental wellness themes such as stress, sleep, and emotional overload. Use when the user wants a quick self-assessment, asks "how am I doing mentally", wants a stress check-in, sleep check, burnout check, or a lightweight reflection quiz. Results are for self-observation only and must never be presented as diagnosis.
---

# Psych Quiz

Provide short, structured self-check quizzes for everyday mental wellness reflection.

## Core purpose

Use this skill to help the user:
- do a quick self-check on stress, sleep, burnout, or emotional strain
- turn vague unease into a simple, structured reflection
- get a lightweight result with practical next steps
- notice when a situation may need more support

This skill is for **self-observation and general reflection**. It is **not** diagnosis, psychotherapy, or medical advice.

## Use this skill for

Typical triggers include:
- “帮我测测压力”
- “我最近状态怎么样”
- “做个心理小测试”
- “我是不是压力太大了”
- “给我一个 quick mental check-in”
- “stress quiz”
- “burnout check”
- “sleep check”

## Do not use this skill as

Do not present this skill as:
- a clinical assessment
- a diagnosis tool
- professional psychological evaluation
- a substitute for therapy or psychiatry
- a definitive judgment about the user’s condition

Avoid statements like:
- “你已经患有焦虑症/抑郁症”
- “这个结果证明你有问题”
- “只要做这个测试就能确定”

Prefer phrasing like:
- “自我观察参考”
- “初步整理”
- “一般性支持”
- “如果困扰持续，建议寻求专业帮助”

## Recommended quiz flow

Default flow:
1. brief framing and disclaimer
2. ask the user to answer based on the last 1–2 weeks
3. give 5–7 short questions
4. score into a light result band
5. provide a short interpretation
6. offer 1–3 practical next steps
7. add safety escalation if needed

## First supported quiz: Stress Check-In

Start with a **stress check-in** as the default MVP because it is:
- easy to understand
- broadly useful
- easy to structure and reuse
- relatively low-risk when framed properly

### Question format

Use four options per item:
- Never
- Sometimes
- Often
- Almost always

### Suggested stress questions

1. Lately, I often feel tense or unable to relax.
2. My mind keeps running and is hard to slow down.
3. I get irritated or impatient more easily than usual.
4. My sleep or rest has been worse, or I still feel tired after resting.
5. I feel like the things on my plate are close to my limit.
6. It has been harder to focus on what I need to do.

### Suggested scoring

- Never = 0
- Sometimes = 1
- Often = 2
- Almost always = 3

Suggested ranges:
- **0–4**: Stress looks relatively manageable
- **5–8**: Some stress is building
- **9–13**: Stress appears noticeably elevated
- **14–18**: Stress appears high and worth attention

## Result output pattern

Every result should include:
1. **Result level**
2. **Brief interpretation**
3. **1–3 practical suggestions**
4. **Professional-support reminder when appropriate**

### Example result: relatively manageable

> Your current stress level looks relatively manageable.
> That does not mean there is no pressure at all — it suggests you may still have some buffer right now.
> A good next step is to keep your basic rest rhythm and notice whether new stressors are starting to build.

### Example result: some stress is building

> You may already be carrying a noticeable amount of stress.
> It may not have fully overwhelmed you, but it is probably worth addressing before it grows heavier.
> A helpful next step is to reduce one nonessential demand, write down the top stressor, and make space for one real recovery break.

### Example result: noticeably elevated

> Your recent answers suggest stress may already be affecting your mood, attention, or rest.
> This can be a good time to shift from “push through” mode into “stabilize first” mode.
> Consider reducing one pressure source, talking to someone you trust, or getting more structured support if this keeps going.

### Example result: high and worth attention

> Your recent answers suggest your stress level may be quite high right now.
> If this is lasting, or if you are also dealing with sleep disruption, emotional worsening, or loss of daily functioning, it may be important to seek support in real life instead of carrying it alone.
> Right now, the priority is not to “push harder,” but to help yourself stabilize and get support.

## Style rules

Prefer language that is:
- calm
- clear
- non-alarmist
- respectful
- practical

Avoid language that is:
- dramatic
- diagnostic
- preachy
- shame-based
- falsely certain

## Safety escalation

Stop the normal quiz flow and use a direct safety response if the user expresses:
- self-harm thoughts
- suicide thoughts
- intent to harm others
- inability to stay safe
- overwhelming despair that makes a quiz inappropriate

Use a response like:

> ⚠️ Important: this is not the right moment for a normal self-check quiz. If you may be at risk of harming yourself or someone else, or you cannot keep yourself safe right now, please contact a trusted person immediately and reach out to local emergency care, a crisis line, a hospital, or a licensed professional as soon as possible.

Then stay focused on immediate safety rather than continuing the quiz.

## Disclaimer

> ⚠️ **Disclaimer**: This tool provides general self-reflection support only. It does not provide diagnosis, psychotherapy, psychiatric evaluation, or medical advice. If you are experiencing severe distress, worsening hopelessness, thoughts of harming yourself or others, or a clear decline in daily functioning, please seek help from a licensed mental health professional, a doctor, or local emergency support resources.

## Minimal operating pattern

For most uses, prefer this pattern:
1. brief framing
2. 5–6 questions
3. simple scoring
4. short interpretation
5. one small next step
6. optional follow-up support

## Future expansion

After the stress MVP is stable, the same structure can be extended to:
- sleep check
- burnout check
- emotional overload check
- relationship strain check

Keep the same tone, same safety boundaries, and same non-diagnostic framing.
