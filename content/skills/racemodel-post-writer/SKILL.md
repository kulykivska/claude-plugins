---
name: racemodel-post-writer
version: 1.0.0
description: |
  Write RaceModel posts for LinkedIn, Threads, and Instagram across English and Ukrainian.
  Applies humanizer rules to remove AI patterns and match authentic voice.
  Platform-specific guidance with multi-language support.
license: MIT
compatibility: any-agent
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - AskUserQuestion
---

# RaceModel Post Writer

Write authentic, platform-native posts for RaceModel across LinkedIn, Threads, and Instagram in English and Ukrainian. This skill combines humanizer patterns with RaceModel brand voice and platform conventions.

## Quick Start

1. **Define your core idea** in one sentence
2. **Choose platforms** you're writing for (LinkedIn, Threads, Instagram)
3. **Pick language(s)** (English, Ukrainian, or bilingual)
4. **Follow the platform template** below
5. **Apply humanizer rules** to remove AI patterns
6. **Review the checklist** before publishing

---

## RACEMODEL BRAND VOICE RULES

Always apply these across all posts, all platforms, all languages:

### ✅ DO
- **"We" voice** — use "we", not "I"
- **Data-driven** — every claim backed by numbers (AUC, accuracy %, race count)
- **Honest framing** — "This predicts 66%, which is better than baseline, but has limits"
- **Direct language** — no fluff, no filler, straight to the point
- **Conversational tone** — how you'd explain to a friend, not a press release
- **Sales intent** — clear CTA (try free, subscribe, register)

### ❌ DON'T
- **No em-dashes** (—) — use commas, colons, or parentheses instead
- **No other projects** — don't mention Jarvis, Aura, TruthLens
- **No bullet carpets** — max 2-3 bullets, not 5+
- **No "stoit zanotity"** (Russian/Ukranian formal markers) — be casual
- **No vague attribution** — "Some say" or "It's believed" = weak
- **No rule of three** — if you list things, do 2 or 4+, not exactly 3
- **No passive voice** — "Our model" not "The model was"

---

## HUMANIZER RULES (Quick Reference)

Remove these AI patterns:

1. **Inflated significance** — "pivotal moment", "crucial role", "underscores importance"
2. **Promotional language** — "exceptional", "remarkable", "groundbreaking"
3. **Vague attributions** — "according to some", "many believe", "it's often said"
4. **Em-dash overuse** — max 1 per sentence (and NO em-dashes at all for RaceModel)
5. **Passive voice** — "was discovered" → "we found"
6. **-ing analysis** — "highlighting the importance" → "this matters because"
7. **Filler phrases** — "It's important to note", "As mentioned", "In conclusion"
8. **Parallel negatives** — "doesn't lack conviction, isn't without merit" → simplify
9. **Repetition** — "important...importance...significantly" → vary your words
10. **Rule of three** — if listing, do 2 or 4+, not 3

---

## PLATFORM TEMPLATES

### LinkedIn (English Only)

**Format:** 200-400 words, professional but conversational, storytelling arc

**Sections:**
1. **Hook** (2-3 sentences) — surprising number or question
2. **Context** (2-3 sentences) — why this matters
3. **What we did** (3-4 sentences) — method, not fluff
4. **Results** (2-3 sentences) — specific numbers
5. **CTA** (1-2 sentences) — try free, register, etc.

**Voice:** Expert but accessible. No corporate speak. Casual parenthetical asides are good.

**Example structure:**
```
Hook: "97 races. One pattern we didn't expect to find."

Context: Most overtake models miss something obvious. They focus on driver skill 
and grid position. But they ignore the circuit itself.

What we did: We built a circuit-prior system that blends:
- Historical DNF rates by track
- Grid disorder dynamics
- Driver form momentum

Results: LORO improved 3.8 to 3.62. On street circuits? Circuit history alone 
accounts for 40% of overtake predictions.

CTA: Try our Strategy tab (free for registered users). See how circuit patterns 
predict your race.
```

**Humanizer fixes:**
- Remove: "This groundbreaking system underscores the importance of circuit analysis"
- Keep: "Most models miss the circuit. We don't."

---

### Threads (English)

**Format:** 100-150 words, hot take + one fact, punchy

**Structure:**
1. **Hook** (1 sentence) — bold claim or surprising fact
2. **Evidence** (1-2 sentences) — 1 number or insight
3. **Why it matters** (1 sentence) — context
4. **CTA** (1 sentence) — link to app

**Voice:** Casual, confident, no corporate tone.

**Example:**
```
Circuit patterns predict overtakes better than driver history.

97 races tested. Accuracy: 66% AUC. Street circuits have 3x higher DNF rates 
than permanent tracks. Not luck. Pattern.

It's why bettors who understand Monaco are ahead of everyone else.

Try Strategy tab (free) → racemodel.io
```

**Humanizer fixes:**
- Remove: "underscores the significance of circuit awareness"
- Keep: "It's why bettors who understand Monaco are ahead"

---

### Threads (Ukrainian)

**Format:** 100-150 words, same as English version but in Ukrainian

**Voice:** Casual Ukrainian, no formal markers, conversational

**Example:**
```
Паттерни трас предіктять обертаки краще ніж історія гонщика.

97 гонок протестовано. Точність: 66% AUC. На вуличних трасах вибування в 3 рази 
вище ніж на постійних. Це не удача. Це паттерн.

Тому що бетори, які розуміють Монако, на крок попереду.

Спробуй Strategy tab (безкоштовно) → racemodel.io
```

**Humanizer fixes:**
- Remove formal Ukrainian: "є свідченням важливості", "слід зазначити"
- Keep: "Це не удача. Це паттерн." (short, punchy)

---

### Instagram (English)

**Format:** 80-150 words caption + strong visual element

**Structure:**
1. **Caption hook** (1-2 sentences) — visual framing
2. **Quick insight** (2-3 sentences) — 1-2 key facts
3. **Hashtags** (20-30) — discovery and reach

**Visual:** Graph, circuit comparison, before/after, or lifestyle angle (person looking at RaceModel on laptop)

**Example caption:**
```
Why did Lando miss P2? 

Circuit history. Our 97-race analysis shows: Monaco has 3x higher DNF rate 
than Silverstone. Every circuit has its own personality.

Street circuits = chaos. Permanent = stability.

Know the circuit, know the odds.

#F1Predictions #RaceStrategy #DataDriven #F1Analysis #Motorsport #BettingEdge 
#F1Community #RaceModel #MotorsportAnalytics #FP1 #Qualifying #StrategyCall 
#PredictiveModels #F1Tech
```

**Humanizer fixes:**
- Remove: "This groundbreaking analysis reveals the critical importance of..."
- Keep: "Circuit history. Our 97-race analysis shows..." (direct, no fluff)

---

### Instagram (Ukrainian)

**Format:** 80-150 words caption + visual

**Example caption:**
```
Чому Ландо упустив P2?

Історія трас. Наш аналіз 97 гонок показує: Монако має вибування в 3 рази більше 
ніж Сілверстоун. Кожна траса має своє лице.

Вулиці = хаос. Постійні = стабільність.

Знаєш трасу — знаєш шанси.

#F1Predictions #RaceStrategy #DataDriven #F1Analysis #MotorSport #BettingEdge 
#F1Community #RaceModel #MotorsportAnalytics
```

**Humanizer fixes:**
- Remove: "які демонструють значущість"
- Keep: casual, conversational Ukrainian

---

## MULTI-LANGUAGE STRATEGY

### When to use English
- **LinkedIn** — always English (professional audience)
- **Threads** — English for international reach, Ukrainian for followers in UA/RU
- **Instagram** — use both (one post, two captions in Stories or carousel)

### When to use Ukrainian
- **Threads** — strong Ukrainian audience
- **Instagram** — Ukrainian-speaking followers
- **Never on LinkedIn** — stick to English

### Bilingual approach
If posting on Instagram to both audiences:
- Option 1: Post once in English, add Ukrainian caption in first comment
- Option 2: Two separate posts (different days)
- Option 3: Carousel with English slide + Ukrainian slide

---

## VOICE MATCHING

Before writing, answer these:

1. **What's the vibe?** (analytical, casual, urgent, encouraging?)
2. **Who am I talking to?** (traders, F1 fans, engineers, investors?)
3. **What's the one thing they should remember?** (if they forget everything else, what stays?)
4. **How would I say this to a friend over coffee?** (that's your voice)

---

## WRITING PROCESS

### Step 1: Core Idea
One sentence. What's the insight? What's the number?

Example: "Circuit patterns predict overtakes more accurately than driver skill"

### Step 2: Pick Platforms
[] LinkedIn (English)
[] Threads (English)
[] Threads (Ukrainian)
[] Instagram (English)
[] Instagram (Ukrainian)

### Step 3: Follow Template
Write first draft using the platform template above.

### Step 4: Apply Humanizer
Remove AI patterns:
- Search for: "pivotal", "groundbreaking", "underscores", "it's important to note"
- Check for passive voice: "was discovered" → "we found"
- Check for rule of three: if listing 3 things, make it 2 or 4+
- Check for em-dashes: replace with commas or colons
- Check for vague: "some say" → "our data shows"

### Step 5: Read Out Loud
Does it sound like YOU? If it sounds like AI, it is.

### Step 6: Checklist

Before publishing:
- [ ] Numbers are accurate (if 66%, it's 66%, not 70%)
- [ ] Every claim is backed by data
- [ ] No AI markers (pivotal, remarkable, underscores)
- [ ] No em-dashes
- [ ] No mention of other projects
- [ ] Sounds conversational, not corporate
- [ ] CTA is clear (free, register, try, link)
- [ ] Platform length OK
- [ ] Language is consistent (no mixing English/Ukrainian awkwardly)
- [ ] Hashtags relevant (Instagram only)

---

## QUICK REFERENCE: PLATFORM LENGTHS

| Platform | Words | Tone | Frequency |
|----------|-------|------|-----------|
| LinkedIn | 200-400 | Expert-casual | 2-3x/week |
| Threads EN | 100-150 | Hot take | 3-4x/week |
| Threads UK | 100-150 | Casual | 2-3x/week |
| Instagram EN | 80-150 | Lifestyle | 2-3x/week |
| Instagram UK | 80-150 | Casual | 2-3x/week |

---

## EXAMPLES BY CONTENT TYPE

### Model Update Post
**Core idea:** "Isotonic calibration improved accuracy from 63% to 66%"

**LinkedIn:** Explain the method, why it matters, results, CTA to try
**Threads:** Just the numbers + context ("how we got here")
**Instagram:** Before/after visual + casual explanation

### Race Analysis Post
**Core idea:** "Circuit patterns beat driver history at predicting overtakes"

**LinkedIn:** Story + data + findings + CTA
**Threads:** Hot take about circuit importance
**Instagram:** Visual comparison (Monaco vs Silverstone) + insight

### Betting/Strategy Post
**Core idea:** "Street circuits have 40% higher overtake volatility"

**LinkedIn:** Why this matters for bettors + data + how to use it
**Threads:** Just the fact + why it's important
**Instagram:** Lifestyle angle (trader looking at odds) + the insight

---

## RED FLAGS (Don't Post If...)

❌ **No numbers** — "our model is good" with no data = weak
❌ **Too corporate** — "It is imperative to note" = AI speak
❌ **Vague claims** — "some analysts believe" = sounds weak
❌ **Em-dashes** — even one = fix it
❌ **Doesn't sound like you** — read it out loud
❌ **No CTA** — always tell people what to do next
❌ **Other projects mentioned** — focus on RaceModel only
❌ **Three-item list** — make it 2 or 4+ items

---

## EXAMPLES OF BEFORE/AFTER

### Before (AI-ish):
```
This groundbreaking circuit analysis underscores the importance of understanding 
track-specific dynamics. Our isotonic calibration system marks a pivotal moment 
in predictive accuracy. It's important to note that circuit patterns are a 
crucial factor in race prediction.
```

### After (Human-written):
```
Here's what we found: circuit patterns beat driver history. We tested 97 races, 
got 66% accuracy. On street circuits? They're chaos. That's not luck, that's 
the track.

Try Strategy tab (free for registered users) and see circuit-specific odds 
for your next race.
```

---

## WHEN TO USE THIS SKILL

✅ Writing any RaceModel post (LinkedIn, Threads, Instagram)
✅ Creating content ideas from race data
✅ Turning model updates into posts
✅ Writing betting/strategy insights
✅ Multi-language posts (EN + UK)

❌ Not for internal Slack/team chat
❌ Not for technical documentation
❌ Not for code comments

---

## HOW TO INVOKE

Use this skill when you need to write RaceModel posts:

```
/racemodel-post-writer
Core idea: [your one-sentence insight]
Platforms: LinkedIn, Threads (EN/UK), Instagram
Language: English / Ukrainian / Both
```

The skill will guide you through the template and apply humanizer rules automatically.

---

**Remember:** Good posts sound like a real person who knows something interesting 
and wants to share it. If it sounds like an AI wrote it, rewrite it.

Now go write something authentic.
