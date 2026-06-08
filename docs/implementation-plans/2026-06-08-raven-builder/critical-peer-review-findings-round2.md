# Critical Peer Review (Round 2) — raven-builder implementation plan

**Reviewer:** Claude Opus 4.8 (1M context) · critical-peer-review (falsification-first, source-opened)
**Date:** 2026-06-09
**Classification:** implementation-plan
**Documents reviewed:** `phase_02.md`, `phase_04.md`, `phase_05.md`, `phase_06.md`, `test-requirements.md`, `docs/design-plans/2026-06-08-raven-builder.md`
**Mandate:** confirm C1/C2/I1/I2/I3/I4 are genuinely resolved (not reworded), and detect any NEW Critical/Important the edits introduced. No auto-fixing.

**Verdict: APPROVED.** All six targeted findings (C1, C2, I1, I2, I3, I4) are RESOLVED against the Java source. F1, F3 addressed; F2 honesty note present. No new Critical or Important introduced. Two Low-severity residuals (internal citation-range inconsistency; loose `(l.159)` fill pointer) — neither blocks execution.

---

## Source Inventory (what I read, and the ground truth pinned)

All line claims verified against the pre-extracted upstream at
`/home/brian/people/Mark/raven-matrix/scratch/SandiaGeneratedMatrixTool-1.0.0-source/Source/gov/sandia/cognition/generator/matrix/`.

| Java artifact | Lines | Ground truth established |
|---|---|---|
| `surface/SGMSurfaceFeatureGenerator.java` | 134–202 | width `nextInt(3)` @134 (always); height **conditional** — deterministic for width=½ (@137-138) and width=¾ (@139-140), `nextInt(2)` **only** in the `else` (width=¼) @142; `nextBoolean()` swap @144 (always); fill via `generateFillPattern(null,…)` @159-161; shape `nextInt(6)` @164. **Pre-fill draws = 2 or 3.** Live switch cases 0–5 @167-202; commented Line case (stale `case 4`) @197-201. |
| `fillpattern/SGMFillPatternGenerator.java` | 60–99 | `null` allowed-list → `nextInt(3)` over `[White, Grey75, Black]` @71-85. Confirms the surface generator's fill draw is one `next_int(3)`. |
| `SGMMatrix.java` (relocation) | 531–552 | relocation conditional `correctAnswerPosition > positionInAnswerChoices` @531; inner draw `nextInt(positionInAnswerChoices)` @538 guarded by `positionInAnswerChoices > 0` @536. |
| `SGMMatrix.java` (cell-list dedup) | 575–596 | `containsCheck(List<SGMCell>, SGMCell)` @575, iterates cells, skips nulls, calls `answer.equals(answerChoice)`; the distractor-dedup call site is @492. |
| `SGMBaseCell.java` | 188–230 | feature-list `containsFeatureCheck(SGMSurfaceFeature, List)` @188; `equals(SGMCell)` @202 — size check + bidirectional feature `containsFeatureCheck`. No `hashCode` override of value semantics (identity hash @180-186). |
| `SGMMatrixDifficultyClassifier.java` | 191–389 | `evaluate(SGMMatrix)` signature @191; `sb` init @208; layer loop @210; **letter ladder** first append `'A'` @234 … last append `'V'` @289; **digit map** @308-382; trailing `_` delete @389. |

**Positive control on the citation audit:** I located the exact `sb.append('A')` (@234) and `sb.append('V')` (@289) bounding the letter ladder, and the `sb.append('1')` (@313) starting the digit map, to confirm the ladder is *inside* `208–389` but *outside* `308–382`. This is the falsifier for I1: the old citation provably omits the ladder; the new one provably includes it.

---

## Hidden Assumptions (load-bearing, with status)

1. **The reviewer's pre-extracted `scratch/` copy is byte-identical to the submodule zip the plan cites.** Load-bearing for every line-number verdict. Status: the plan (phase_04 header, RESUME.md §14-15) names this same extract path as the source-of-truth; I read it directly. Signpost if wrong: line numbers would not land on the claimed tokens — they did. Accepted.
2. **The Python `rng.next_int`/`next_boolean` consume one draw each, 1:1 with the JVM.** Load-bearing for the C2 draw-count test being discriminating. Status: established in phase_02 (golden-vector port, AC4.2). Accepted as a cross-phase dependency, not a Phase-4 claim.
3. **`generateFillPattern` is reached via the `null` allowed-list path during surface generation** (so fill = exactly one `next_int(3)`). Load-bearing for the C2 reference-RNG sequence. Status: verified — `SGMSurfaceFeatureGenerator` calls the two-arg overload with `allowedFillPatterns` which, when `null`, dispatches to the one-arg `nextInt(3)` form. Accepted.
4. **`positionInAnswerChoices` is the count of filled contiguous wrong-answer slots** (so "correct position > it" = "correct sits past the block"). Load-bearing for C1's plain-language description. Status: verified against the increment logic @498-501 and the relocation guard @531. Accepted.

No load-bearing assumption is left unverified.

---

## Per-finding verdicts

### C1 — `relocate_correct_answer=False` skips a conditional `nextInt` — **RESOLVED**

The default is now described as an **RNG-consumption toggle**, not only a position toggle, in three reinforcing places:
- Decisions §1 caveat (phase_04:39): byte-stream identity "only attainable under `relocate_correct_answer=True`; the optional Java differential is scoped to that flag."
- Decisions §3 (phase_04:43): explicitly "**It is also an RNG-consumption toggle, not only a position toggle**," cites `SGMMatrix.java:531–548`, the `nextInt(positionInAnswerChoices)` @538, the `positionInAnswerChoices > 0` guard, and states the default "consumes one fewer draw than the JVM and every later draw shifts."
- Task 6 (phase_04:236): repeats the mechanism and adds the correct anti-pattern guard — "do not 'compensate' with a throwaway draw — the honor-config path is deliberately a different stream."

Source check: the conditional @531, the inner-guard @536, the draw @538 are all real and correctly described. The optional Java differential is scoped to `=True` (Decisions §1). The claim that AC4.1/AC2.* are unaffected is correct — internal determinism and the structural oracle do not depend on JVM byte-stream parity.

*Citation precision note (Low):* the block is cited `531–548`; it actually closes at 552 (`positionInAnswerChoices++` @551). All RNG-relevant lines (531, 536, 538) are inside the cited span, so the under-citation of the tail is immaterial.

### C2 — per-surface draw order — **RESOLVED**

The contaminated "size → fill → shape / one-draw advance" provenance is gone and replaced with the correct variable-count sequence in every location:
- **Header (phase_04:11)** now re-pins against `SGMSurfaceFeatureGenerator.java:134–164`, names the prior summary as wrong, and states the order: `nextInt(3)` width → **conditional `nextInt(2)` height** (`else` @142, smallest width only) → **`nextBoolean()` swap** @144 → fill `nextInt(3)` @159 → shape `nextInt(6)` @164, **pre-fill = 2 or 3**. Switch cases pinned 164–202; commented Line (`case 4`) @197-201.
- **Task 2 implementation (phase_04:102-109)** restates the 6-step order, instructs "read the source — do not trust this summary blind," and pins the live switch order (0=Ellipse … 5=Trapezoid) with the warning that the commented `case 4` must not mislead the index.
- **Task 2 test (phase_04:113)** is now discriminating: it replays the pinned sequence on a **separate reference `JavaRandom(seed)`** advancing by the **variable** count (2 or 3 pre-fill + fill + shape), asserts the generator's RNG is left in the **same internal state**, and **pins two seeds** — one forcing the height draw (3 pre-fill), one skipping it (2 pre-fill). It explicitly says "Do **not** assume a single fixed pre-fill draw count."

Source check: every claim matches. Width @134 always; height `else`-branch `nextInt(2)` @142 only for the smallest width; deterministic height for width=½ (@137-138) and width=¾ (@139-140); swap @144 always; fill @159 → `nextInt(3)`; shape @164 → `nextInt(6)`. Pre-fill = 2 or 3, confirmed. Line-number pointers correct; "~180–210" pointer corrected to 164–202.

*Citation precision note (Low):* the header and Task 2 write fill as "`nextInt(3)` (l.159)". Line 159 is the *call site* (`SGMFillPatternGenerator.generateFillPattern`); the actual `nextInt(3)` lives at `SGMFillPatternGenerator.java:71`. The plan correctly routes the port through `generate_fill(rng)` (Task 1) which does `next_int(3)`, so the test's reference sequence is right. The `(l.159)` pointer is loosely the call site, not the draw — harmless, but it is the one place a literal-minded executor could go looking at the wrong file.

### I1 — `label()` citation omitted the letter ladder — **RESOLVED**

Reconciled to `208–389` consistently, with the ladder called out, in all required locations:
- **Design glossary (design:154):** `208–389` "letter ladder 232–289, digit map 308–382 … the narrower `308–382` omits the letter ladder."
- **Design Phase-5 components (design:336):** `208–389` "the whole `sb`-build incl. the letter ladder at 232–289, not just the `308–382` digit map."
- **phase_05 Step 2 (phase_05:56), docstring instruction (phase_05:61), completion check (phase_05:183):** all `208–389`, with the ladder at 232–289 named and the old `308–382` flagged as "would omit how letters are assigned."

The earlier Step-2 vs docstring split (`210–389` vs `308–382`) is gone; everything normative says `208–389`. The old `308–382` survives **only** as the explicitly-flagged counter-reference. Source check: ladder appends span 234–289, digit map 308–382, all inside 208–389. Correct.

*Internal-inconsistency note (Low):* the phase_05 `Codebase verified` header (phase_05:11) cites `191–389` (the `evaluate` method-signature boundary @191) while the canonical citation is `208–389` (the `sb`-build boundary). Both ranges include the ladder, so I1's defect is resolved either way; this is a stylistic boundary mismatch, not a reopening. Worth a one-character tidy in a later pass, not a blocker.

### I2 — cell-level dedup helper undefined / misnamed — **RESOLVED**

The two helpers are now distinct, correctly named, and consistently described in BOTH phases, and the misnamed `contains_feature_check` is gone from all normative content:
- **phase_02 Task 4 (phase_02:269):** `contains_check(list[SurfaceFeature], …)` is named the **feature-list** helper mirroring `SGMBaseCell.containsFeatureCheck` (SGMBaseCell.java:188), explicitly "**distinct from**" the cell-list helper `SGMMatrix.containsCheck` (SGMMatrix.java:575), which is "a separate **Phase-4** artifact (`_contains_cell`, with a cell-level `_cell_value_equals`)." States the cell helper *uses* the feature-list helper internally.
- **phase_04 Decisions §2 (phase_04:40):** keeps them separate — (a) Phase-2 `contains_check(list[SurfaceFeature], SurfaceFeature)` → `containsFeatureCheck` (SGMBaseCell.java:188); (b) Phase-4 `_contains_cell(list[Cell], Cell)` → `SGMMatrix.containsCheck` (SGMMatrix.java:575, call @492), resting on `_cell_value_equals(Cell, Cell)` → `SGMCell.equals` (SGMBaseCell.java:202). "Distractor dedup is over **cells**, not feature lists."
- **phase_04 Task 6 (phase_04:234, 239):** defines both helpers, with `_cell_value_equals` mirroring `SGMCell.equals` (equal feature count AND each feature value-present via the Phase-2 feature-list `contains_check`), and adds a direct unit test of both on hand-built cells. Explicit: "**Do not reuse the feature-list `contains_check` for this**."

Source check: the cell-value-equality mirror is faithful — `SGMCell.equals` @202-230 is exactly "size equal + bidirectional `containsFeatureCheck`," and `_cell_value_equals` is specified the same way. `containsCheck` @575-596 (skip null, `answer.equals`) is mirrored by `_contains_cell` (skip None/blank, `_cell_value_equals`). The misnamed `contains_feature_check` now appears only in the prior-review report and RESUME.md (both correctly *describing* the defect being fixed), never in a normative plan instruction.

### I3 — AC4.3 near-tautological / probabilistic — **RESOLVED**

AC4.3 is now discriminating and consistent across all three statements:
- **phase_04 AC block (phase_04:27):** "a **pinned first-drawn surface feature differs** (seeds chosen … so its shape draw differs — a specific inequality, not a probabilistic 'some differ')."
- **phase_04 Task 7 (phase_04:265):** two specific seeds whose `JavaRandom` streams produce a **different `next_int(6)` shape index** for the **first base surface feature** under a fixed single-layer config; assert (a) structural equality and (b) "that **named, located feature**'s `shape` is **exactly `!=`**." Names the falsifier: "if `build()` failed to thread the surface RNG, the asserted feature would be identical and the test would fail."
- **test-requirements AC4.3 (test-requirements:66):** "Two **pinned** seeds … **an exact `!=` on a specific located feature's `shape`** … Discriminating, not a probabilistic 'some differ'."

This pins a specific seed pair, a specific located feature, and a specific attribute (`shape`) inequality — no longer hedged. Resolved.

### I4 — 840-sweep scope overclaim — **RESOLVED**

phase_05 now scopes the sweep to structure→label only:
- **Task 4 (phase_05:154-155):** "`label()` reads only `matrix.layers[].structures`, so the sweep validates **only the structure→label path**. `build()` still runs the full answer/distractor pipeline (with a fabricated default `correct_answer_position` and `seed=0`), but **that path is not under test here** — its output is neither asserted nor inspected." Offers the optional structure-only-matrix tightening.
- **Architecture (phase_05:5)** and **Decisions §"840-sweep" (phase_05:32)** and **completion check (phase_05:186)** all reflect the structure→label framing.

Matches the Java: `evaluate` reads `matrix.getSGMLayers() → layer.getStructureFeatures()` only (@210-214); the answer path is not touched by `label()`. Resolved.

### F1 — corner-out hand-table row — addressed

phase_05 Task 3 (phase_05:123) marks `ShapeRep+corner-out→A6` as a "**labeller-internal-consistency** entry only … **no published stimulus uses it** … **It does NOT count toward DR6's independent-reference-frame guarantee**; flag it as such in its provenance comment." Correct — the norming naming scheme excludes shape-repetition from direction 5 (CLAUDE.md QA target), so this row is labeller-derived, not externally grounded.

### F2 — gate bounded by reviewer honesty — addressed (optional note present)

phase_05 Task 4 (phase_05:168) carries the honest bound: the sweep is "a consistency check on a parser/labeller pair written by the same executor," a real bug "can hide as a mutually-compensating parse+label error," the gate's strength "is bounded by executor honesty," and "the hand-derived table (AC2.1) … is the only independent guard." Plainly stated.

### F3 — `render/__init__.py` must not re-export `raster` — addressed

phase_06 pins this as a hard rule in three places: Task 1 file note (phase_06:42), the Import-hygiene constraint (phase_06:59, tied to the Phase-8 `tests/test_import_hygiene.py` AC7.1), Task 3 (phase_06:117), and the completion check (phase_06:141). The `resvg_py` import stays inside `rasterise`. Correct and load-bearing for AC7.1.

---

## New-issue scan (did the edits introduce any Critical/Important?)

I checked the edited passages for newly-introduced overclaims, broken cross-references, and internal contradictions.

- **Ripple check (clean):** `contains_feature_check`, `size → fill → shape`, and `308–382`-as-citation now appear in normative plan content **only** as explicitly-flagged "was wrong / would omit" counter-references. Remaining raw hits are in `critical-peer-review-findings.md` (the prior report) and `RESUME.md` (the fix-instruction list) — both correctly describing the defects being fixed, not plan instructions the executor follows. No stale citation leaked into a load-bearing claim.
- **C2 test logic (sound):** advancing a *separate* reference `JavaRandom` by the variable count and asserting equal internal state is a genuine draw-count discriminator (it would catch a port that drew a fixed pre-fill count, or dropped the conditional height / the swap). Not tautological.
- **I2 helper wiring (sound):** `_cell_value_equals` using the feature-list `contains_check` internally is exactly the Java nesting (`SGMCell.equals` calls `containsFeatureCheck`); no circularity introduced.
- **No new universal-quantifier overclaims** in the edited spans. The C1/C2/I4 edits all *narrow* claims (scope to `=True`, scope to structure→label, "2 or 3 not 1") rather than broaden them.

**No new Critical or Important found.** Two Low residuals only (the `191–389` vs `208–389` header boundary; the `(l.159)` fill pointer pointing at the call site rather than `SGMFillPatternGenerator.java:71`).

---

## ACH (did the edits resolve, or merely reword?)

Two hypotheses per finding: **H-resolved** (the edit changes the substantive claim to match source) vs **H-reworded** (cosmetic, defect persists). Evidence = the source-verified token each edit now points at.

| Evidence | H-resolved | H-reworded |
|---|---|---|
| C2 test advances reference RNG by 2-or-3, pins two branch-covering seeds | + | − (a reword would keep one fixed advance) |
| C1 names the @538 draw + @536 guard + scopes differential to `=True` | + | − |
| I1 normative range = `208–389`, ladder 232–289 named; `308–382` only as counter-ref | + | − |
| I2 `_contains_cell`/`_cell_value_equals` defined + assigned in Task 6 + a dedicated unit test | + | − (a reword would not add the helper definition + test) |
| I3 pins specific seed pair + named located feature + exact `!= shape` | + | − |
| I4 "neither asserted nor inspected" + optional structure-only build | + | − |

Every finding's evidence is a substantive, source-matching change (a definition added, a count corrected, a scope narrowed, a specific assertion pinned) — not achievable by rewording alone. H-resolved dominates with zero contradictions. **All six are genuinely resolved.**

---

## Verification (independent checks run)

- Read the four Java source files end-to-end across the cited ranges; confirmed every load-bearing line number lands on the claimed token (134, 137-143, 144, 159-161, 164, 167-202 / 531, 536, 538 / 575-596, 188, 202-230 / 191, 208, 234, 289, 308-382, 389).
- Confirmed `SGMFillPatternGenerator.java:71` is the actual fill `nextInt(3)`, validating the C2 reference sequence (and surfacing the loose `(l.159)` pointer).
- Grep ripple-audit across `docs/` for `contains_feature_check`, `size → fill → shape`, `308`, `one-draw` — all live-plan hits are corrected or flagged-as-wrong; raw hits confined to the prior report + RESUME.md.
- Cross-checked AC4.3 wording across phase_04 (×2) and test-requirements for consistency — aligned.
- Cross-checked the I1 `208–389` citation across design (×2) and phase_05 (×3) — aligned, with the lone `191–389` header noted as Low.

---

## Pre-Mortem (assume the verdict is wrong — what would the next pass reveal?)

1. **The executor implements the C2 draw-order test but mis-identifies which width value forces the height draw**, picking two seeds that both skip (or both force) the height draw, silently degrading the test to single-branch. Mitigation already in the plan: phase_04:113 explicitly requires "one whose width forces the height draw (3 pre-fill draws) and one whose width skips it (2 pre-fill draws)." Residual risk is executor discipline, not a plan defect — but a reviewer of the *code* should re-confirm both branches are seeded.
2. **The `(l.159)` fill pointer sends the executor to the surface file expecting a literal `nextInt(3)` and they hard-code the catalogue draw at the wrong abstraction**, missing that `generateFillPattern` also has the `allowedFillPatterns != null` path (@98-99, a different bound). Low likelihood — the plan routes fill through `generate_fill` (Task 1) and the supplemental fill cycles are separately pinned — but the pointer should say `SGMFillPatternGenerator.java:71`.
3. **`_cell_value_equals` is implemented mirroring `SGMCell.equals` but the executor reproduces the upstream Java bug** where `containsFeatureCheck` (@192) iterates the instance field `surfaceFeatures` instead of its `surfaceFeature` parameter. This is a real latent bug in the *Java* I noticed while verifying I2 — it does not affect the plan's helper-distinction claim (which is what I2 was about), and the symmetric double-loop in `equals` @215-228 masks it in practice. Flagging for the code-review phase, not the plan: if the port faithfully copies the parameter-ignoring loop, behaviour matches Java; if it "fixes" it, it diverges. Either is defensible but should be a conscious, recorded choice. **Out of scope for this round** — it is neither C1–I4 nor introduced by the edits.

None of these reopen a finding; (3) is a heads-up for the implementation/code-review phase.

---

## Diagnostic timeout

- *Most likely or most coherent?* The verdict rests on token-level source matches, not narrative — each "RESOLVED" is anchored to a specific line I read.
- *Anchored to the prior review's framing?* I re-derived the source ground truth independently before comparing, and found the prior review's own citations accurate (C1 531-548, C2 134-164, I1 308-382-omits-232-289, I2 575/188, the draw-count 2-or-3). The prior review was correct; the edits address it.
- *What would change my mind?* If the submodule zip differed from the `scratch/` extract — but the plan names that extract as its source, so they share provenance.
- *What didn't I check?* I did not re-verify the Phase-3 transform line claims, the resvg_py API, or the non-C1–I4 "Verifies" mappings (the prior review spot-checked those clean as F4); out of this round's mandate.

---

## Overall Assessment

**APPROVED — ready to proceed to execution handoff.**

- **C1: RESOLVED.** **C2: RESOLVED.** **I1: RESOLVED.** **I2: RESOLVED.** **I3: RESOLVED.** **I4: RESOLVED.** F1, F3 addressed; F2 honesty note present.
- **No new Critical or Important introduced.**
- **Low-severity residuals (optional, non-blocking):**
  - L1 — phase_05:11 header cites `191–389` vs the canonical `208–389`; both include the ladder, tidy for consistency.
  - L2 — phase_04 `(l.159)` fill pointer is the call site; the actual `nextInt(3)` is `SGMFillPatternGenerator.java:71`. Repoint for the executor.
- **Heads-up for the code-review phase (not this round's scope):** the upstream `containsFeatureCheck` (SGMBaseCell.java:192) iterates the instance field, not its parameter — decide consciously whether the port copies the quirk or corrects it, and record the choice.

Because the verdict is APPROVED with only Low residuals (N ≤ 3, no Important), this does not trigger the halt-and-discuss gate. The two Low items can be folded into the execution pass or a quick editing touch-up at the author's discretion.
