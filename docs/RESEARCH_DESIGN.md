# Kryptovox — Research Design
**Version 0.1 | March 2026**

---

## The Central Problem

Thousands of people, across dozens of countries, across thousands of years, have reported encounters with large bipedal creatures that match no known animal. The modern scientific response has been dismissal without investigation.

Dismissal without investigation is not science. It is a social reflex.

Kryptovox treats this body of testimony the way any serious researcher would treat an anomalous dataset: with rigour, without predetermined conclusions, and with genuine curiosity about what the data actually shows.

---

## Research Questions

### Primary Questions

**RQ1 — Descriptor Consistency**
Do independent witness accounts of bipedal cryptid creatures show statistically significant clustering in physical descriptors beyond what would be expected by chance or cultural transmission?

**RQ2 — Historical Continuity**
Do the physical descriptors and behavioural patterns reported in modern testimony match those recorded in historical and folkloric accounts from cultures with no plausible contact with each other or with modern witnesses?

**RQ3 — Testimony Authenticity**
Do emotional and structural markers in Kryptovox accounts show patterns consistent with genuine traumatic experience rather than fabricated or confabulated narrative?

### Secondary Questions

**RQ4 — Geographic and Temporal Distribution**
Is there a statistically significant pattern in where and when encounters are reported? Does this pattern correlate with terrain type, human population density, or proximity to wilderness areas?

**RQ5 — Phenomenon Distinctness**
Are Dogman and Bigfoot empirically distinct phenomena (different descriptor profiles, different geographic distributions, different behavioural patterns) or do they overlap sufficiently to suggest a common identity?

**RQ6 — The Slovenian Thread**
Does Slovenian folkloric tradition contain accounts that match the modern Dogman/Bigfoot descriptor profile, and if so, what is the chain of transmission and geographic distribution within Slovenia?

---

## Hypotheses

**H1:** Kryptovox accounts will show descriptor clustering significantly above chance across the following traits: eye luminosity, height range (7–9ft bipedal), approach-then-retreat behaviour, and olfactory reports — independent of geographic region.

**H2:** Pre-20th century historical accounts from at least 5 culturally isolated regions will contain ≥3 matching descriptors from the Kryptovox core profile.

**H3:** Emotional testimony markers in Kryptovox accounts (voice breaks, crying, long pauses) will correlate with specific narrative moments (first sighting, eye contact, creature vocalisation) at a rate inconsistent with fabricated storytelling.

**H4:** Dogman and Bigfoot accounts will show statistically distinct descriptor profiles in facial structure, height, and terrain preference, suggesting two distinct phenomena rather than one.

**H5:** Slovenian folkloric records will yield ≥2 entity types that match ≥4 descriptors from the Kryptovox core profile.

---

## Methodology

### Design
Mixed methods — quantitative descriptor analysis combined with qualitative narrative and folkloric analysis.

Neither method alone is sufficient:
- Quantitative without qualitative misses the texture of testimony and the specificity of historical records
- Qualitative without quantitative is anecdote. We need both.

---

### Study 1 — Modern Testimony Corpus Analysis

#### Sampling Strategy

**Inclusion criteria:**
- First-person account (witness speaking directly, not researcher summarising)
- Audio or video available (enables emotional marker analysis)
- Minimum descriptor threshold: account must include at least 3 physical descriptors
- English language (Phase 1 — other languages in Phase 2)

**Exclusion criteria:**
- Confirmed hoaxes (documented admissions)
- Second-hand accounts ("my friend told me")
- Pure written accounts with no audio (cannot analyse emotional markers)
- Accounts with insufficient geographic detail (state/province minimum)

**Target sample:** 300 accounts minimum (statistical power for clustering analysis)

**Source channels (priority order):**
1. Dogman Encounters — 500+ episodes, consistent interview format, single interviewer reduces bias
2. Sasquatch Chronicles — high volume, mixed format
3. BFRO Podcast — official Bigfoot Field Researchers Organisation accounts
4. Bigfoot Society — additional volume

**Why Dogman Encounters first:**
Single consistent interviewer (Vic Cundiff) means the elicitation method is controlled. Same questions, same follow-up style, same environment. This reduces interviewer effect and makes accounts more comparable.

---

#### Extraction Protocol

**Two-stage extraction:**

Stage 1 — Automated (Claude Haiku)
- Full transcript processed against extraction schema
- Flags low-confidence fields for human review
- Outputs structured JSON per account
- Confidence score per field (0–1)

Stage 2 — Human review
- All fields flagged <0.70 confidence reviewed manually
- Emotional marker timestamps verified against audio
- Final record approved by human reviewer

**Inter-rater reliability:**
- 10% of accounts extracted independently by two coders
- Cohen's Kappa calculated for each field category
- Target κ ≥ 0.75 (substantial agreement) for quantitative fields
- Disagreements resolved by discussion and schema refinement

---

#### Variables

**Independent variables:**
- Geographic region (country, terrain type, elevation, proximity to water)
- Temporal (decade, season, time of day)
- Witness context (alone/group, hunting/hiking/driving, armed/unarmed)
- Source channel

**Dependent variables — physical descriptors:**
- Height estimate
- Eye luminosity (Y/N, colour, described as self-illuminated Y/N)
- Hair/fur colour and texture
- Facial structure (canine/simian/human/hybrid)
- Smell (Y/N, description category)
- Sound produced (type)
- Locomotion (bipedal only / quadrupedal observed also)

**Dependent variables — behavioural descriptors:**
- Approach type (actively approached / stationary observed / fled immediately)
- Reaction to witness (aggressive / curious / indifferent / fled)
- Threat display (Y/N)
- Departure pattern

**Dependent variables — testimony markers:**
- Emotional break events (type, timestamp, narrative trigger)
- Minimisation phrases ("I know how this sounds")
- Specificity score (count of unique sensory details — texture, temperature, sound frequencies)
- Internal consistency score (do early and late account details match)
- Reluctance indicators (pauses before key details, hedging language)

---

#### Statistical Analyses

**Descriptor clustering**
Hierarchical clustering on physical descriptor vectors. Do accounts group into distinct subtypes, or is there one coherent profile? Test against random baseline.

**Geographic distribution**
Kernel density estimation of encounter locations. Test for non-random spatial distribution. Correlate with terrain covariates (forest density, elevation, watershed proximity, human population density).

**Temporal analysis**
Distribution across time of day and season. Chi-square test against uniform distribution. Trend analysis across decades.

**Cross-phenomenon comparison**
Dogman vs Bigfoot: multivariate comparison of descriptor profiles. Discriminant analysis to identify which descriptors best distinguish the two phenomena.

**Emotional marker analysis**
Frequency of emotional breaks per narrative moment category. Test whether breaks cluster at specific types of moments (eye contact, creature vocalisation, approach) vs being uniformly distributed.

---

### Study 2 — Historical Record Analysis

#### Source Selection Protocol

**Priority tiers:**

Tier 1 — Primary sources in original language
- Egyptian: Book of the Dead, Pyramid Texts (Anubis/Wepwawet)
- Norse: Prose Edda, Poetic Edda (Fenrir, úlfhéðinn — wolf-warrior berserkers)
- Greek/Roman: Pliny the Elder's Natural History (Cynocephali accounts), Ctesias's Indica
- Medieval European: Werewolf trial records 1400–1700 (genuine court documents from France, Germany, Estonia)
- Slovenian: Štrekelj's folk poetry collection (1895–1923), ZRC SAZU ethnographic archive, Traditiones journal

Tier 2 — Reliable secondary ethnographic sources
- Pacific Northwest indigenous oral tradition (academic ethnographies)
- Himalayan expedition records (Shipton 1951 footprint, Hillary, Messner)
- Central Asian Almas accounts (Myra Shackley's fieldwork)
- Australian Yowie (Charles Healy's 19th century newspaper archive)

Tier 3 — Ethnographic surveys
- Pan-African wildman accounts (systematic literature review)
- South American accounts

**Exclusion:** Modern cryptozoology literature — too risk of circular referencing. Only pre-1970 sources or academic ethnographies with documented oral history methodology.

---

#### Descriptor Mapping Protocol

Each historical account coded using a modified version of the Kryptovox schema — adapted for what historical sources can and cannot tell us.

Fields available in historical records: height, physical build, facial type, hair/fur, eye characteristics, smell, sound, terrain preference, behaviour toward humans.

Fields unavailable: precise GPS location, exact date, witness emotional markers (in most cases).

**Cultural isolation scoring:**
For each historical account, score the plausibility of contact with other accounts in the database:
- 0: No plausible contact (pre-contact indigenous culture, geographically isolated)
- 1: Possible contact via trade routes
- 2: Probable contact (same cultural sphere)
- 3: Likely contact (post-printing press, literate culture)

High-scoring matches between accounts with isolation score 0 are the strongest evidence.

---

#### The Cross-Cultural Comparison

**Method:**
For each physical descriptor in the Kryptovox core profile, calculate the percentage of historical accounts that include a matching descriptor — controlling for isolation score.

**Null hypothesis:**
Historical accounts will not show descriptor overlap with modern testimony beyond what would be expected from a common cultural template (e.g., global human tendency to imagine large predators).

**How we address the cultural template objection:**
Humans do have universal cognitive templates for danger. Large, dark, predatory, eyes in the dark. These templates exist and will appear in any folklore corpus.

The specific test is: do historical accounts include *specific, unusual* descriptors that also appear in modern testimony — descriptors not predicted by generic predator templates?

Candidates for unusual descriptors:
- Self-illuminated eyes (not simply reflective — witnesses consistently specify the light appears to come *from within*)
- Bipedal canine locomotion specifically (not simply large wolf — upright, human-gait)
- The specific smell (musk + rot + sulphur combination)
- The specific behavioural pattern: observed watching, then retreat when noticed

If these specific descriptors appear independently in historically isolated accounts, that is not explained by universal predator templates.

---

### Study 3 — Emotional Authenticity Analysis

#### Theoretical Framework

This study applies validated forensic psychology tools to Kryptovox testimony.

**Criteria-Based Content Analysis (CBCA)**
Developed for use in child abuse cases, subsequently validated for adult testimony. 19 criteria grouped into:
- General characteristics (logical structure, unstructured production, quantity of detail)
- Specific contents (contextual embedding, descriptions of interactions, reproduction of conversation, unexpected complications)
- Peculiarities of content (unusual details, superfluous details, accurately reported details misunderstood)
- Motivation-related contents (spontaneous corrections, admitting lack of memory, raising doubts about own testimony, self-deprecation)
- Offence-specific elements

**Why CBCA applies here:**
CBCA does not require the event to have occurred. It measures whether testimony has the *structure* of genuine experiential memory vs constructed narrative. This is the correct tool for our purpose.

**Trauma testimony research:**
Genuine trauma memory has specific characteristics:
- Fragmented structure (not linear)
- Sensory specificity (texture, temperature, smell — not just visual)
- Time distortion (subjective duration differs from objective)
- Rehearsed-feeling core memory surrounded by uncertainty about peripheral details
- Intrusive thoughts / reluctance to revisit

We will code Kryptovox transcripts for all of these and compare against baseline rates in known fabricated accounts.

#### Control Conditions

**Control 1 — Confirmed hoaxes**
Several high-profile Bigfoot/Dogman hoaxes have been admitted. These accounts are coded with the same schema. If our authenticity markers cannot distinguish admitted hoaxes from other accounts, the markers are invalid.

**Control 2 — Fictional encounter narratives**
A sample of fictional first-person cryptid encounter stories (from horror fiction, creepypasta) coded with same schema. These should score low on authenticity markers.

**Control 3 — Legitimate wildlife encounter trauma**
Accounts of genuine traumatic wildlife encounters (bear attacks, mountain lion encounters — documented real events) coded for emotional markers. Expected to show similar emotional structure to Kryptovox accounts if our coding is valid.

If Kryptovox accounts cluster with genuine wildlife trauma and away from fiction/confirmed hoaxes on emotional marker measures, that is meaningful.

---

## Addressing the Main Objections

### "People are influenced by Bigfoot/Dogman pop culture"

**Response:**
- Include accounts from pre-internet era (1970s–1990s) where relevant
- Track which specific descriptors appear in popular media vs which appear in testimony
- The self-illuminated eyes descriptor is *not* a standard pop-culture Bigfoot trait — it rarely appears in fiction but consistently appears in testimony
- Accounts from non-English-speaking countries (pre-translation) are less contaminated by English-language media

### "People are lying for attention"

**Response:**
- Many witnesses explicitly do not want attention. They ask for anonymity. Many took years to tell anyone.
- The emotional marker analysis directly tests this. Liars and truthful witnesses show measurably different testimony structures (CBCA has been validated in court systems)
- Internal consistency scoring: fabricators tend to over-construct (too neat, too linear, no uncertainty)
- Vic Cundiff has interviewed witnesses who were visibly distressed, crying, reluctant. This pattern is consistent across 500+ accounts. The scale makes coordinated fabrication implausible.

### "These are misidentifications of known animals"

**Response:**
- Many witnesses are experienced outdoorspeople — hunters, forestry workers, rangers — who explicitly state they know what known animals look like and this was not one
- The specific combination of traits (bipedal, canine face, human height) does not match any known animal
- This objection does not explain the historical record from cultures that had never heard of Bigfoot

### "Confirmation bias — the channel only airs believable accounts"

**Response:**
- True. Vic Cundiff selects for coherent, detailed accounts. This is acknowledged as a sampling limitation.
- However: the consistency analysis is *within* this selected sample. If even within a pre-selected "credible" sample the descriptors cluster significantly, that is still meaningful.
- The emotional marker analysis is unaffected by this — we are not claiming the creatures exist, we are asking whether the testimony structure is consistent with genuine experience.

### "Ancient people just feared wolves and bears"

**Response:**
- The generic predator template objection is addressed by focusing on *specific* descriptors not predicted by fear of wolves or bears
- A bear does not have self-illuminated eyes, a canine face, and walk bipedally
- The Cynocephali accounts (Greek/Roman) describe bipedal dog-headed humans — not wolves. This is a specific, unusual description with no predator-template explanation

---

## Ethical Considerations

**Witness anonymity:**
All modern witnesses are identified by anonymous ID only. No names, no locations more specific than state/province. This is standard in testimony research.

**Sensationalism policy:**
All findings presented in measured academic language. We do not make claims beyond what the data supports. We do not use the project to promote belief or disbelief.

**Historical source integrity:**
Original language sources cited precisely. No paraphrasing that introduces bias. Translations credited and cross-checked.

**On the question of belief:**
The research team's personal beliefs about the existence of these creatures are explicitly not relevant to the methodology and will not be stated in the paper. The data speaks or it doesn't.

---

## Output Plan

### Paper 1 — The Descriptor Analysis (RQ1 + RQ4 + RQ5)
*"Statistical Consistency in Anomalous Bipedal Creature Encounter Testimony: A Corpus Analysis of 300+ First-Person Accounts"*

Target journals:
- Journal of Scientific Exploration
- Fortean Studies
- Folklore (Taylor & Francis)
- Journal of Folklore Research

### Paper 2 — The Historical Record (RQ2 + RQ6)
*"Persistent Archetypes: Bipedal Canine Entities Across Isolated Cultural Records — A Comparative Ethnographic Analysis"*

### Paper 3 — Testimony Authenticity (RQ3)
*"Credibility Indicators in Anomalous Experience Testimony: Applying CBCA to a Large-Scale Cryptid Encounter Corpus"*

### Public Output
- Kryptovox.com — interactive findings map + accessible summary
- Open dataset — anonymised structured account database, CC licence
- Podcast / documentary consideration (after paper 1 is submitted)

---

## Timeline (Phase-Gated, Not Calendar)

| Phase | Gate | Description |
|---|---|---|
| Design | ✅ Complete | Research questions, methodology, schema |
| Pilot | 20 accounts extracted | Test schema against real data, refine |
| Corpus 1 | 100 accounts | First statistical tests, adjust methodology |
| Corpus 2 | 300 accounts | Full descriptor analysis, Paper 1 draft |
| Historical | Concurrent | Folklore layer, Paper 2 draft |
| Authenticity | Concurrent | Emotional marker analysis, Paper 3 draft |
| Publication | After peer review | Submit Paper 1, iterate |

---

*Hidden voices. Made audible.*
*Maintained by Jonek* 🎩
