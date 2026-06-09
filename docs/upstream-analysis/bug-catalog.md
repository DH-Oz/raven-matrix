# SGMT upstream - bug & discrepancy catalogue

This catalogue consolidates every confirmed bug, paper divergence, and porting gotcha found across the SGMT v1.0.0 Java source. The governing policy is that the Matzen et al. (2010) paper is the fundamental spec: where the source diverges from the paper, the port fixes to the paper; where the source has an internal coding error with no paper dimension, the port fixes the error; where the behaviour is intentional and load-bearing for oracle equivalence, the port replicates it; and where Python's default value-semantics differ from Java's identity-semantics in a way the paper does not settle, the choice is flagged for a human decision. The single dominant theme is identity-vs-value equality: `AbstractSGMSurfaceFeature` defines only a typed `equals(SGMSurfaceFeature)` overload and no `equals(Object)`/`hashCode`, so every Java collection operation over surface features (logic-op `contains`, `HashSet` dedup, `indexOf` fill cycling) uses reference identity, and it only produces paper-correct output because feature instances are shared by reference and never cloned along the relevant paths. A naive Python port with value-based `__eq__` changes those outputs unless every site is re-derived consciously. The "acceptance bar" below means structure (relations, directions, layers) plus correct-answer position; distractor content and pixels are out of bar per the project decision.

| id | severity | kind | resolution | affects acceptance bar? |
|----|----------|------|------------|-------------------------|
| surface-clone-drops-size-rect-ellipse | high | logic-error | fix-to-paper | yes (Size relation, distractor dedup) |
| core-surface-equals-no-object-override | high | identity-vs-value | flag-and-decide | yes (logic ops, difficulty) |
| core-logicop-contains-identity | high | identity-vs-value | fix-to-paper | yes (Logic Stim) |
| base-logic-identity-contains | high | identity-vs-value | fix-to-paper | yes (Logic Stim) |
| base-logic-identity-works-only-by-sharing | high | identity-vs-value | flag-and-decide | yes (Logic Stim) |
| surface-equals-no-object-override | high | identity-vs-value | fix-to-paper | yes (logic ops) |
| base-logic-dedup-typemismatch | high | logic-error | fix-to-paper | yes (Logic Stim feature sets) |
| base-logic-singlearg-transform-throws | high | other | replicate | yes (Logic Stim layer build) |
| core-derivedcell-provenance-not-in-equals | high | other | replicate | yes (distractor dedup, correct-answer guard) |
| numerosity-transform-count-offbyone | high | off-by-one | replicate | yes (Number relation, correct answer) |
| gen-correct-answer-relocation | high | rng-coupling | replicate | yes (correct-answer position) |
| gen-unspecified-logic-50pct | high | paper-divergence | flag-and-decide | yes (oracle path selection) |
| gen-supplemental-disabled-when-logic-base | high | paper-divergence | replicate | yes (logic layer composition) |
| loc-tlco-getparent-no-bottomrow-special | high | other | replicate | yes (TopLeftCornerOut propagation) |
| ui-gui-cannot-make-3layer-or-logic-stim | high | other | flag-and-decide | yes (oracle coverage) |
| render-answer-cell-hardcoded-bottom-right | high | other | replicate | yes (grid blank vs choice index) |
| core-surface-equals-fill-collapse | medium | paper-divergence | fix-to-paper | no (distractors) |
| core-surface-equals-dead-commented | medium | commented-out | flag-and-decide | no (Line excluded) |
| core-composite-shallow-copy-shared-features | medium | other | replicate | no (distractors) |
| core-correctanswer-reposition-rng | medium | rng-coupling | replicate | yes (correct-answer position) |
| fill-generator-only-three-of-five | medium | paper-divergence | fix-to-paper | no (distractor variety) |
| fill-grey10-grey40-red-and-misnamed | medium | copy-paste | fix-to-paper | no (distractors) |
| fill-pattern-cycling-identity | medium | identity-vs-value | flag-and-decide | yes (shading sequence) |
| fill-changefill-indexof-identity | medium | identity-vs-value | fix-to-paper | yes (shading sequence) |
| fill-changefill-grey-collapse-equality | medium | copy-paste | fix-to-paper | no (answer-choice equality) |
| fill-repetition-only-three-fills | medium | paper-divergence | flag-and-decide | no (distractors) |
| numerosity-transform-null-deref | medium | logic-error | flag-and-decide | yes (multi-layer numerosity) |
| numerosity-scale-base-vs-transform-mismatch | medium | logic-error | replicate | yes (scale composition) |
| repetition-firstfeature-only | medium | logic-error | flag-and-decide | yes (numerosity+scaling/rotation) |
| rng-type-mapping-enum-vs-switch | medium | rng-coupling | replicate | partial (mode-dependent) |
| rng-locationtransform-then-type-order | high | rng-coupling | replicate | no (determinism only) |
| rng-numerosity-extra-draw | medium | rng-coupling | replicate | no (determinism only) |
| rot-only-45-degrees | medium | paper-divergence | flag-and-decide | yes (Orientation relation) |
| fill-changefill-base-uses-get0-only | medium | logic-error | replicate | yes (shading base seed) |
| numerosity-topleftcornerout-formula | medium | other | replicate | yes (numerosity layout) |
| loc-diag-tlbr-wrong-exception-text | low | copy-paste | fix-to-paper | no |
| gen-wronganswer-type-by-layercount | medium | rng-coupling | replicate | no (distractors) |
| gen-base-surface-hashset-identity | medium | identity-vs-value | replicate | yes (difficulty score) |
| gen-fillpatternrepetition-three-of-five | low | paper-divergence | flag-and-decide | no (distractors) |
| gen-diagonal-only-odd-square | medium | paper-divergence | replicate | yes (direction availability) |
| diff-featurescore-35-36-index-overwrite | medium | copy-paste | fix-to-paper | no (difficulty only) |
| diff-unique-surface-identity-dedup | medium | identity-vs-value | flag-and-decide | no (difficulty only) |
| diff-changefill-fillrepetition-collapse-to-B | medium | logic-error | flag-and-decide | no (difficulty/debug) |
| diff-changefillpattern-no-feature-slot | medium | logic-error | flag-and-decide | no (difficulty only) |
| fill-grey10-grey40-red-collapse | medium | copy-paste | fix-to-paper | no (distractors) |
| fill-grey10-filename-header | medium | mis-named | fix-to-paper | no |
| fill-grey10-grey40-description-red | medium | copy-paste | fix-to-paper | no (distractors) |
| fill-grey10-grey40-red-collapse (dup) | medium | copy-paste | fix-to-paper | no |
| fill-bare-generator-only-3-of-5 | medium | paper-divergence | fix-to-paper | no (distractors) |
| fill-repetition-palette-only-3 | medium | paper-divergence | fix-to-paper | no (distractors) |
| fill-surface-equality-ignores-rgba-uses-description | medium | identity-vs-value | fix-to-paper | no (distractors) |
| fill-paint-alpha-nonuniform | medium | other | replicate | no (rendering) |
| fill-generator-default-omits-grey10-grey40 | medium | logic-error | fix-to-paper | no (distractors) |
| surface-equals-not-symmetric-typeguard | medium | logic-error | replicate | yes (shape-type discrimination) |
| surface-clone-drops-size-pathbased | medium | logic-error | fix-to-paper | no (distractor dedup) |
| scale-wrong-comment-and-clone-shared-fill | low | identity-vs-value | flag-and-decide | yes (fill cycling) |
| core-matrix-size-check-self-compare | low | logic-error | fix-to-paper | no (dead guard) |
| gen-layer-size-self-compare | low | logic-error | fix-to-paper | no (dead guard) |
| core-cell-containsfeaturecheck-ignores-param | medium | logic-error | fix-to-paper | yes (cell equality) |
| core-cell-hashcode-equals-contract | low | logic-error | flag-and-decide | no (no HashSet use) |
| core-location-equals-null-npe | low | other | flag-and-decide | no (latent) |
| core-feature-checkcompatibility-dead | low | dead-code | n/a (omit) | no |
| base-checkcompat-stub | low | dead-code | n/a (omit) | no |
| supp-checkcompatibility-unimplemented | low | dead-code | replicate (omit) | no |
| core-matrix-clone-unsupported | low | dead-code | replicate | no |
| base-rng-nextint1-consumes-draw | low | rng-coupling | replicate | no (determinism only) |
| base-rng-logic-assignment-loop | low | rng-coupling | replicate | no (determinism only) |
| rot-wrong-comment | low | other | replicate | no (cosmetic) |
| loc-vert-getparent-numcolumns | low | logic-error | fix-to-paper | no (3x3 masks it) |
| loc-diag-validate-after-super | low | logic-error | replicate (clean) | no |
| loc-exception-msg-missing-spaces | low | other | fix-to-paper | no |
| surface-header-misnamed-multiple | low | mis-named | n/a (omit) | no |
| surface-customcheck-fill-uses-other-not-cast | low | other | replicate | no |
| surface-line-fill-compared-contradicts-intent | low | commented-out | fix-to-paper | no (Line excluded) |
| fill-line-equality-includes-fill | low | commented-out | flag-and-decide | no (Line excluded) |
| fill-changefill-indexof-identity (dup) | medium | identity-vs-value | flag-and-decide | yes (shading) |
| fill-no-equals-hashcode | low | identity-vs-value | flag-and-decide | yes (fill cycling) |
| gen-case3-no-clone-shared-ref | medium | identity-vs-value | flag-and-decide | no (distractors) |
| gen-numerosity-detect-by-description-string | low | other | flag-and-decide | no (distractors) |
| gen-unbounded-generation-loop | medium | other | flag-and-decide | no (set-generation termination) |
| gen-numlayers-zero-guard | low | off-by-one | flag-and-decide | no (param validation) |
| gen-logic-op-traversal-comment-mismatch | low | dead-code | replicate | yes (logic cell order, code correct) |
| ui-generate-rng-draw-order-coupling | medium | rng-coupling | flag-and-decide | no (distractors) |
| ui-no-retry-on-insufficient-answers | medium | dead-code | flag-and-decide | no (answer-choice count) |
| ui-no-headless-batch-entrypoint | medium | other | flag-and-decide | no (architecture) |
| render-rastersettings-unused-in-generate | low | dead-code | flag-and-decide | no (rendering) |
| diff-score-equals-vs-compareto-nan | low | other | flag-and-decide | no (difficulty binning) |
| diff-sb-deletecharat-empty | low | off-by-one | flag-and-decide | no (zero-layer guard) |

Note: several fill-description findings (`fill-grey10-grey40-red-and-misnamed`, `fill-grey10-grey40-red-collapse`, `fill-grey10-grey40-description-red`, `fill-surface-equality-ignores-rgba-uses-description`, `fill-changefill-grey-collapse-equality`) are the same root bug seen from different subsystems. They are merged in the High/Medium narrative below under "The Grey10/Grey40 'Red' collision".

---

## High severity

### surface-clone-drops-size-rect-ellipse + surface-clone-drops-size-pathbased
- Location: `RectangleSGMSurfaceFeature.java:110-114`, `EllipseSGMSurfaceFeature.java:110-114`, `AbstractPathBasedSGMSurfaceFeature.java:117-121` (copy ctors).
- Kind: logic-error.
- Source: copy constructors call only `super(other)`, which copies scale/rotation/fill/shape but never the private `width`/`height` fields, leaving them 0.0 on every clone. `customEqualsCheck` reads those private fields (`getWidth()*getScale()`, `getHeight()*getScale()`), so any two clones compare size-equal (0.0 == 0.0) and an original mis-compares against its own clone. Rendering is unaffected because it reads `getShape().getBounds()`, which is copied. `Line` is the exception: its copy ctor does copy length.
- Paper/intent: size is one of the five named attributes; the Size relation (letter D) and distractor distinctness depend on correct size comparison. Clones pervade generated matrices (used by ChangeFillPattern, FillPatternRepetition, Numerosity, and the distractor path).
- Resolution: fix-to-paper. Derive width/height from the shape bounding box in the port's value-equality method, or propagate them through the copy path. Test: clone then assert symmetric equality.
- Acceptance bar: yes for Rectangle/Ellipse (Size relation); path-based variant is primarily distractor dedup.

### Surface-feature equality has no `equals(Object)`/`hashCode` (core-surface-equals-no-object-override, surface-equals-no-object-override, base-logic-identity-contains, core-logicop-contains-identity, base-logic-identity-works-only-by-sharing)
- Location: `AbstractSGMSurfaceFeature.java:169-210` (typed `equals(SGMSurfaceFeature)` only); `LogicalANDSGMStructureFeature.java:77`, `LogicalORSGMStructureFeature.java:90`, `LogicalXORSGMStructureFeature.java:77,84`; `SGMLayer.java:167` (`HashSet`).
- Kind: identity-vs-value.
- Source: the typed overload is invisible to `List.contains`, `HashSet`, and `indexOf`, all of which dispatch through `Object.equals` (reference identity). AND/OR/XOR therefore intersect/union/symmetric-difference by object reference. This produces paper-correct sets only because `provideBaseSurfaceFeatures` returns the stored instances and `transformSurfaceFeatures`/`getSurfaceFeatures` propagate the same references without cloning. The author knew `List.contains` was wrong for value-equality (`BaseSGMStructureFeatureGenerator.containsCheck` lines 306-323 has the explicit comment and uses the typed overload) but did not apply it to the logic ops.
- Paper/intent: the paper (pp. 227-240) defines AND/OR/XOR as value-based set operations over shapes (type, fill, size, orientation). Value equality is the intent.
- Resolution: fix-to-paper. Implement `__eq__`/`__hash__` by value (shape type, scale, rotation, position, fill) on all surface features, and use ordinary membership tests. Test: two distinct-but-value-equal features must intersect/union/xor correctly. Strategy must be applied consistently across logic ops, `SGMLayer.baseSurfaceFeatures`, and the difficulty classifier's `uniqueSurfaceFeatures` (see `gen-base-surface-hashset-identity`, `diff-unique-surface-identity-dedup`, which point the opposite way for difficulty).
- Acceptance bar: yes. This is the single most dangerous determinism difference for the Logic Stim folder, where correct-answer position is judged.

### base-logic-dedup-typemismatch (and the secondary bug in base-logic-identity-works-only-by-sharing)
- Location: `AbstractLogicOperationSGMStructureFeature.java:99-101`.
- Kind: logic-error.
- Source: the dedup guard `list.contains(featureIndex)` is called on a `List<SGMSurfaceFeature>` with an `int` (autoboxed `Integer`). No `SGMSurfaceFeature` can equal an `Integer`, so the check is always false; the `add` is unconditional. A base location can receive the same feature object more than once in one assignment pass, corrupting the set semantics of the logic op into a multiset.
- Paper/intent: the assignment is meant to add each feature at most once per base location (the surrounding bookkeeping maps confirm intent).
- Resolution: fix-to-paper. Check feature membership, not the integer index: `list.contains(getBaseSurfaceFeatures().get(featureIndex))` with value equality.
- Acceptance bar: yes (logic-op base feature sets).

### base-logic-singlearg-transform-throws
- Location: `AbstractLogicOperationSGMStructureFeature.java:167-175` (single-arg override throws); abstract two-arg variant lines 177-179.
- Kind: other (dispatch pattern).
- Source: the single-arg `transformSurfaceFeatures(list)` throws `UnsupportedOperationException`; the real op is the two-arg variant. `SGMLayer` dispatches via `instanceof AbstractLogicOperationSGMStructureFeature` (lines 175-241) onto a separate code path with two parent cells.
- Resolution: replicate. The port's layer builder must branch on logic-op type and call the two-arg derivation; a uniform single-method walk would hit the throwing path.
- Acceptance bar: yes (Logic Stim layer build).

### core-derivedcell-provenance-not-in-equals
- Location: `SGMDerivedCell.java` (no equals override) vs `SGMBaseCell.equals` lines 202-230.
- Kind: other.
- Source: `SGMDerivedCell` adds `baseCell`/`parentCell` provenance but inherits `SGMBaseCell.equals`, which compares only `surfaceFeatures` (by value, bidirectionally). This is intentional and load-bearing: `SGMMatrix.generateAnswerChoices` uses equals (lines 491, 590) to dedup distractors and confirm a candidate is not the correct answer.
- Resolution: replicate. The port must NOT include provenance fields in cell equality. Minor note: `SGMBaseCell.hashCode` includes location but the typed `equals(SGMCell)` does not (asymmetry, see `core-cell-hashcode-equals-contract`).
- Acceptance bar: yes (distractor dedup and correct-answer guard).

### numerosity-transform-count-offbyone
- Location: `TranslationalNumerositySGMStructureFeature.java:190`.
- Kind: off-by-one (intentional in source).
- Source: `for (int i = 0; i <= surfaceFeaturesAtPreviousLocation.size(); i++)` produces `prev.size()+1` clones, implementing the number-change increment along the transform direction. The list is pre-sized `prev.size()+1`; the comment confirms intent. `provideBaseSurfaceFeatures` correctly uses strict `<` with `initialNumerosity`.
- Paper/intent: the number-change relation grows the count per cell (1->2->3 across a 3-cell run), consistent with the paper's numerosity variants.
- Resolution: replicate. A porter who mechanically uses `<` would produce `n` instead of `n+1` copies, breaking the Number relation and the correct-answer cell.
- Acceptance bar: yes (Number relation, correct answer).

### gen-correct-answer-relocation + core-correctanswer-reposition-rng
- Location: `SGMMatrix.java:531-552`; primary draw at `SGMMatrixSetGenerator.java:150`.
- Kind: rng-coupling (intentional, not a logic error).
- Source: the primary `correctAnswerPosition = random.nextInt(numAnswerChoices)` is drawn before construction and is the value the spreadsheet records. If the distractor loop exits before filling a contiguous block up to that slot, the constructor draws a second `random.nextInt(positionInAnswerChoices)`, swaps cells, and overwrites `correctAnswerPosition` (line 548). For the normed set the fallback almost never fires, but it is conditional and consumes an extra draw.
- Paper/intent: the paper (lines 202-203) says the correct answer appears in a user-specified or randomly assigned position. The relocation is the implementation of that and matches intent.
- Resolution: replicate. The final position is not always the primary draw; the relocation block and its conditional draw must be modelled if matching the "Correct Answer" column exactly.
- Acceptance bar: yes (correct-answer position).

### gen-unspecified-logic-50pct
- Location: `BaseSGMStructureFeatureGenerator.java:140-151`; routed via `SGMLayerGenerator` -> three-arg overload.
- Kind: paper-divergence (path selection, not a code bug).
- Source: the batch path (`SGMMatrixSetGenerator`) calls the fully UNSPECIFIED overload, so on a 3x3 the base relation is a logic op 50% of the time (`nextInt(2)`), regardless of user intent. The five-arg explicit-type overload that honours a chosen relation/direction is only called from the GUI.
- Paper/intent: every oracle stimulus has a fixed Structure code; logic problems are a named, separate subtype, not a coin-flip. The stochastic path cannot reproduce any spreadsheet row deterministically.
- Resolution: flag-and-decide. Oracle-driven generation must drive type and direction via the explicit-type path (the `*Type` enums), mirroring the GUI, not via the UNSPECIFIED batch path.
- Acceptance bar: yes (oracle path selection).

### gen-supplemental-disabled-when-logic-base
- Location: `SGMLayerGenerator.java:100-113`.
- Kind: paper-divergence (intentional constraint, present in both source and paper).
- Source: when the base feature is a logic op, the supplemental loop is skipped entirely, so a logic-op layer always has exactly one relation regardless of the drawn `numStructureFeatures` (which is still consumed). Recorded as a deliberate fix in revision logs.
- Paper/intent: logic problems are a self-contained category with no transformation relations mixed in; the "Logic Stim" oracle folder uses only X/Y/Z codes with no transformation letters.
- Resolution: replicate exactly. Omitting the guard would allow combinations that never appear in the oracle.
- Acceptance bar: yes (logic layer composition).

### loc-tlco-getparent-no-bottomrow-special
- Location: `TopLeftCornerOutSGMLocationTransform.java:165-190`.
- Kind: other (intentional design).
- Source: the parent rule is "the cell above, else the cell to the left" - `(row-1, col)` if `row>0` else `(row, col-1)`. This is NOT the inverse of the diagonal wavefront `createNextLocation`. The JUnit test pins exact parents across seven shapes and is the executable spec. Confirmed divergence at `(0,1)`: parent is `(0,0)`, not the inverse-of-next `(1,0)`.
- Resolution: replicate branch-for-branch; pass the JUnit test verbatim. A porter deriving parent as the inverse of "next" will be wrong.
- Acceptance bar: yes (TopLeftCornerOut feature propagation, direction digit 5).

### ui-gui-cannot-make-3layer-or-logic-stim
- Location: `SGMBuilderFrame.java:1029,1230` (numLayers cap) and absence of a Logic location-transform control; engine path `SGMMatrixSetGenerator.java:144`.
- Kind: other (architectural limitation of the GUI).
- Source: the GUI hard-caps `numLayers` at 2 (`OneLayer.isSelected()?1:2`), so it cannot produce the "3 Layer Stim" folder. `LogicSGMLocationTransform` is hardwired inside `BaseSGMStructureFeatureGenerator` when a logic base type is chosen; it is not a selectable `LocationTransformType`. The engine (`SGMMatrixSetGenerator`) supports N layers via `nextInt(getMaxLayersPerMatrix())+1`.
- Resolution: flag-and-decide. Target engine parity, not GUI parity: expose N-layer generation, and select `LogicSGMLocationTransform` implicitly when a logic base type is chosen.
- Acceptance bar: yes (full oracle coverage; the GUI alone cannot reach 3-layer stimuli).

### render-answer-cell-hardcoded-bottom-right
- Location: `SGMMatrixImage.java:179-180,268-269,293-294`; separate field `SGMMatrix.correctAnswerPosition`.
- Kind: other.
- Source: two distinct "answer position" concepts. The grid blank is always bottom-right (hard-coded). The answer-choice index (`correctAnswerPosition`, 0-based) records which of the 8 tiles is correct. The oracle "Correct Answer" column is the second concept (choice index 1-8), not the grid blank.
- Paper/intent: paper p.530 confirms the empty cell is always bottom-right; lines 202-203 confirm the choice index is separately assigned.
- Resolution: replicate. Keep the two concepts separate in the port; do not conflate the grid blank with the choice index.
- Acceptance bar: yes (the choice index is the in-bar quantity).

### rng-locationtransform-then-type-order
- Location: `SupplementalSGMStructureFeatureGenerator.java:166-178`.
- Kind: rng-coupling.
- Source: in the UNSPECIFIED path, `generateLocationTransform` is called first (consuming `nextInt(3)` or `nextInt(5)` only when the transform type is UNSPECIFIED), then `nextInt(5)` for the feature type. The batch path always enters both draws.
- Resolution: replicate the exact order and conditionality; any reordering desyncs the whole stream.
- Acceptance bar: no (determinism only; out of bar per seeds-unpublished policy), but listed high because it governs all downstream draws if seed reproduction is ever attempted.

---

## Medium severity

### The Grey10/Grey40 "Red" description collision (merged: fill-grey10-grey40-red-and-misnamed, fill-grey10-grey40-red-collapse, fill-grey10-grey40-description-red, fill-surface-equality-ignores-rgba-uses-description, fill-changefill-grey-collapse-equality, core-surface-equals-fill-collapse, fill-grey10-filename-header)
- Location: `Grey10SGMFillPattern.java:48` and `Grey40SGMFillPattern.java:48` both `DESCRIPTION = "Red"`; consumed by every shape's `customEqualsCheck` (`RectangleSGMSurfaceFeature.java:190-191`, Ellipse, Line, `AbstractPathBasedSGMSurfaceFeature.java:186-187`). `Grey10SGMFillPattern.java:2` header mis-named "Grey25SGMFillPattern.java".
- Kind: copy-paste / paper-divergence.
- Source: surface equality compares fills by `getDescription()`. Grey10 and Grey40 both report "Red", so two features differing only by those greys compare equal, collapsing five named shadings to four distinguishable labels (White, Black, Grey, Red). The change-fill cycle itself is unaffected (it advances by identity `indexOf`, not description), so rendering still differs; only equality collapses.
- Paper/intent: paper p.190 specifies five distinct fill patterns.
- Resolution: fix-to-paper. Give the five fills distinct labels (or key fill equality on enum identity); the project already decided to keep five shadings distinct. The header rename is cosmetic.
- Acceptance bar: no. Impact is distractor vocabulary and, in edge cases, matrix acceptance (too few unique distractors). The previously suggested "shifts correctAnswerPosition" claim is inaccurate: position is drawn before construction.

### The 3-of-5 fill palette in the bare generator and FillPatternRepetition (merged: fill-generator-only-three-of-five, fill-bare-generator-only-3-of-5, fill-generator-default-omits-grey10-grey40, fill-repetition-only-three-fills, fill-repetition-palette-only-3, gen-fillpatternrepetition-three-of-five)
- Location: `SGMFillPatternGenerator.java:71-83` (no-arg `nextInt(3)`); `SupplementalSGMStructureFeatureGenerator.java:220-232` (FillPatternRepetition list of 3 with `// TODO - stochastically pick fill patterns`).
- Kind: paper-divergence / incomplete fix.
- Source: the bare `generateFillPattern(random)` emits only White/Grey75/Black (`nextInt(3)`), so Grey10/Grey40 are unreachable there; it is used for initial ShapeRepetition fills and for distractor fills (`SGMMatrix.java:364-365,405-406`). FillPatternRepetition is wired with only [White, Black, Grey75]. The bug-1273 fix that added the two greys was applied only to ChangeFillPattern (all five).
- Paper/intent: paper p.190 says five fill patterns exist; revision history confirms five was the intent.
- Resolution: fix-to-paper for the generator and the repetition palette is the principled choice; flag-and-decide for FillPatternRepetition specifically, because the 845 normed PNGs were generated with the 3-fill subset, so replicating the subset preserves oracle equivalence while fixing it diverges. Decide whether oracle fidelity or paper completeness governs the repetition path.
- Acceptance bar: no (distractor and fill variety only).

### Fill cycling depends on identity indexOf (merged: fill-pattern-cycling-identity, fill-changefill-indexof-identity, scale-wrong-comment-and-clone-shared-fill, fill-no-equals-hashcode)
- Location: `ChangeFillPatternSGMStructureFeature.java:102-105`; fills constructed in `SupplementalSGMStructureFeatureGenerator.java:253-264`; copy ctor `AbstractSGMSurfaceFeature.java:108-115`.
- Kind: identity-vs-value.
- Source: `applyTransform` does `baseFillPatterns.indexOf(prev.getFillPattern())`, which uses object identity because no fill class overrides `equals`. It works at runtime because `provideBaseSurfaceFeatures` plants a list-member reference and `clone()` shallow-copies the same reference, so the previous feature always carries a list instance and `indexOf` returns the right index. On `indexOf == -1`, `(-1+1)%size = 0` silently resets to the first fill (White) with no error.
- Paper/intent: shading-change cycles deterministically through five distinct fills; the paper does not prescribe a mechanism.
- Resolution: fix-to-paper for ChangeFillPattern (`fill-changefill-indexof-identity`): represent fills as an enum / value type so `index()` is value-based; flag-and-decide for the broader fill type design (`fill-no-equals-hashcode`, `fill-pattern-cycling-identity`). Value equality subsumes identity here and removes the latent reset-to-White hazard. The `scale-wrong-comment-and-clone-shared-fill` location tag pointing at `ApplyScalingSGMStructureFeature.java:84` is spurious; the real concern is the fill-sharing in the copy ctor.
- Acceptance bar: yes for the shading sequence (whichever fill each cell gets), in the sense that a wrong port silently produces all-White.

### core-cell-containsfeaturecheck-ignores-param
- Location: `SGMBaseCell.java:188-200`.
- Kind: logic-error.
- Source: `containsFeatureCheck(feature, surfaceFeature)` iterates the instance field `this.surfaceFeatures` instead of the parameter, so the second loop in `equals(SGMCell)` checks each of this's features against this (trivially true). Net effect: equality degenerates from bidirectional mutual-subset to one direction (`other` subset of `this`) plus a dead loop. With the size guard it is reliable for sets of distinct features but admits false positives when `other` has duplicate features whose distinct values are all in `this` (a bag-equality failure).
- Resolution: fix-to-paper. Iterate the parameter (`for otherFeature in surfaceFeature`) so the two loops implement genuine set equality.
- Acceptance bar: yes (cell equality underpins distractor dedup and the correct-answer guard).

### numerosity-transform-null-deref
- Location: `TranslationalNumerositySGMStructureFeature.java:174-194` vs guard at line 131.
- Kind: logic-error.
- Source: `transformSurfaceFeatures` dereferences `existingSurfaceFeaturesAtLocation.get(0)` with no null guard, while its sibling `provideBaseSurfaceFeatures` guards the identical access. `SGMLayer` sets the argument to null for empty cell slots and passes it directly. Trigger: a numerosity supplemental traverses a not-yet-populated derived-cell slot in a multi-layer matrix.
- Resolution: flag-and-decide. Make the null contract explicit (skip vs error) and test it; the base-path precedent suggests returning null on null input.
- Acceptance bar: yes (multi-layer numerosity paths).

### numerosity-scale-base-vs-transform-mismatch
- Location: `TranslationalNumerositySGMStructureFeature.java:153` (base, absolute) vs `:201` (transform, multiplicative).
- Kind: logic-error label is wrong; this is intentional (bug-1293 fix).
- Source: base path sets `setScale(scaling)` (absolute); transform path sets `setScale(scaling * feature.getScale())` (multiplicative), so numerosity composes with a prior ApplyScaling contribution. On a numerosity-only layer both yield the same result (initial scale 1.0).
- Resolution: replicate both branches exactly.
- Acceptance bar: yes (scale composition feeds size equality of the correct answer).

### repetition-firstfeature-only
- Location: `AbstractRepetitionSGMStructureFeature.java:122-134`.
- Kind: logic-error (intentional workaround).
- Source: when applying scaling/rotation/fill-repetition across a multi-feature cell, the previous-cell reference is always `surfaceFeaturesAtPreviousLocation.get(0)`, and the size-equality guard is commented out. This is the bug-1293 workaround that lets numerosity coexist with scaling/rotation; `SGMLayerGenerator` can stochastically co-select them on one layer.
- Resolution: flag-and-decide. The norming oracle was generated with the workaround active, so replicating it preserves equivalence; fixing it to a proper n-to-n mapping diverges from the oracle for numerosity+scaling/rotation combinations. Human call.
- Acceptance bar: yes (those combinations affect the correct-answer cell).

### rng-type-mapping-enum-vs-switch
- Location: `SupplementalSGMStructureFeatureGenerator.java:174-267`.
- Kind: rng-coupling.
- Source: the integer-to-type switch (0=Scaling, 1=FillPatternRepetition, 2=Rotation, 3=Numerosity, 4=ChangeFill) does not match the enum ordinals (UNSPECIFIED=0, APPLY_ROTATION=1, APPLY_SCALING=2, ...). `nextInt(5)` is drawn only in the UNSPECIFIED branch; SPECIFIED branches assign with no draw.
- Resolution: replicate with an explicit mapping dict, not `.ordinal()`. Do not draw in SPECIFIED mode. Test each `*Type` constant maps to the right class.
- Acceptance bar: partial. The oracle path is always SPECIFIED, so the UNSPECIFIED draw is off-path, but the ordinal mis-map affects any mode.

### rng-numerosity-extra-draw
- Location: `SupplementalSGMStructureFeatureGenerator.java:242-251` (case 3).
- Kind: rng-coupling.
- Source: only the numerosity case draws an extra `random.nextInt(2)+1` for `initialNumerosity`; the other four cases draw nothing beyond the location transform.
- Resolution: replicate this single extra draw exactly in the numerosity branch.
- Acceptance bar: no (determinism only).

### rot-only-45-degrees
- Location: `SupplementalSGMStructureFeatureGenerator.java:233-241`; `ApplyRotationSGMStructureFeature`.
- Kind: paper-divergence.
- Source: rotation step is hardcoded 45 degrees ("Only support 45 degree rotation right now"). All features start at rotation 0; accumulation is mod 360. Over a 3x3 only 3 orientation values appear per run (0, 45, 90).
- Paper/intent: paper line 191 describes four or five orientations per shape as a domain-size count, not a step-size requirement. The 45-degree step is an acknowledged placeholder.
- Resolution: flag-and-decide. The orientation oracle (letter C) was generated with this step, so replicate it for equivalence; record the discrepancy and treat variable step as a future extension.
- Acceptance bar: yes (Orientation relation values feed correct-answer comparison).

### fill-changefill-base-uses-get0-only
- Location: `ChangeFillPatternSGMStructureFeature.java:62-95` vs FillPatternRepetition base seeding.
- Kind: logic-error label is wrong; intentional design.
- Source: ChangeFillPattern seeds all base cells with `baseFillPatterns.get(0)` (single starting fill, since it is a change relation), while FillPatternRepetition seeds by `sgmBaseLocationIndex % size` (distinct fills per base location). get(0) is not necessarily White; it is the first list element.
- Resolution: replicate the asymmetry.
- Acceptance bar: yes (shading base seed determines the start of the cycle).

### numerosity-topleftcornerout-formula
- Location: `TranslationalNumerositySGMStructureFeature.java:105-117`.
- Kind: other (intentional fix).
- Source: `numPositions` uses `ceil(sqrt(rows+cols-1))` for TopLeftCornerOut and `ceil(sqrt(maxDimension + initialNumerosity-1))` otherwise, where `maxDimension = max(rows, cols)`. Deliberate revision-1.3 fix. Drives `positionStepSize` and `scaling`.
- Resolution: replicate both branches including the maxDimension selection.
- Acceptance bar: yes (numerosity item sizes/positions in the correct-answer cell).

### gen-wronganswer-type-by-layercount
- Location: `SGMMatrix.java:260-267`.
- Kind: rng-coupling.
- Source: wrong-answer strategy is `nextInt(4)` for >1 layer, `nextInt(3)+1` for 1 layer (excludes case 0, the layer-subset strategy, which needs >=2 layers). A single shared Random threads the whole set, so a wrong branch desyncs all subsequent matrices.
- Resolution: replicate. Correct-answer position is drawn before construction, so it is not corrupted, but distractor content for following matrices would desync.
- Acceptance bar: no (distractors).

### gen-base-surface-hashset-identity
- Location: `SGMLayer.java:167,196,274`; consumed by `SGMMatrixDifficultyClassifier`.
- Kind: identity-vs-value.
- Source: `baseSurfaceFeatures` is a `HashSet<SGMSurfaceFeature>` dedup'd by identity (no `equals(Object)`/`hashCode`), so freshly constructed features are all distinct entries. A value-based Python set would deduplicate genuinely equal features and change the count the difficulty classifier sees.
- Resolution: replicate identity semantics for the difficulty path (the norming `% Correct` values implicitly encode the identity-based count). This conflicts with the fix-to-value decision for the logic ops; resolve per call site, not uniformly.
- Acceptance bar: yes for the difficulty score (the normative oracle), no for structure.

### gen-diagonal-only-odd-square
- Location: `SGMLocationTransformGenerator.java:104-114`.
- Kind: paper-divergence label; actually an intentional, correctly-mapped gate.
- Source: diagonals are reachable in the UNSPECIFIED path only when `numRows` is odd and `numRows == numColumns` (`nextInt(5)`); otherwise `nextInt(3)` gives Horizontal/Vertical/TopLeftCornerOut. The internal case ints align with spreadsheet digits 3 (BL->TR) and 4 (TL->BR).
- Resolution: replicate the gate. The mapping is already aligned with spreadsheet digits.
- Acceptance bar: yes (direction availability for 3x3, which is odd-square).

### diff-featurescore-35-36-index-overwrite
- Location: `SGMMatrixDifficultyClassifier.java:620-626`.
- Kind: copy-paste.
- Source: the NOVEL_SURFACE_FEATURE branch writes `featureScores[35]` instead of `[36]`, so `[36]` is always 0 and `[35]` (combination count) is silently overwritten when both distractor types occur.
- Resolution: fix-to-paper. Write `[36]` in the novel-surface branch. Test independent population of both slots.
- Acceptance bar: no (difficulty only).

### diff-unique-surface-identity-dedup
- Location: `SGMMatrixDifficultyClassifier.java:204-205,387,396-398` + `SGMLayer.java:167`.
- Kind: identity-vs-value.
- Source: `uniqueSurfaceFeatures` is a `HashSet` dedup'd by identity, so `featureScores[27]` counts object instances (number of base-cell slots that received features), not value-distinct shapes.
- Resolution: flag-and-decide. The trained estimator was fit against this count; switching to value-dedup changes feature 27 and breaks calibration until re-trained. Safer to replicate identity until the port has its own estimator.
- Acceptance bar: no (difficulty only).

### diff-changefill-fillrepetition-collapse-to-B + diff-changefillpattern-no-feature-slot
- Location: `SGMMatrixDifficultyClassifier.java:267-286` (debug string) and `:453-486` (feature slots).
- Kind: logic-error.
- Source: both FillPatternRepetition and ChangeFillPattern append 'B' to the debug string, and ChangeFillPattern has no slot in the 37-element feature vector (slots 8-12 cover only FillPatternRepetition, ApplyRotation, ApplyScaling, Numerosity). Any matrix using ChangeFillPattern is under-counted. The norming corpus predates ChangeFillPattern, so the trained estimator is internally consistent for the corpus; the gap only affects user-generated ChangeFillPattern matrices.
- Resolution: flag-and-decide. Either merge ChangeFillPattern into slot [8] (preserves estimator validity, matches the corpus) or add a new slot (needs retraining data that does not exist). The debug `sb` string must never be confused with the spreadsheet Structure code.
- Acceptance bar: no (difficulty/debug only).

### surface-equals-not-symmetric-typeguard
- Location: `AbstractSGMSurfaceFeature.java:169-180` plus each `customEqualsCheck` instanceof guard.
- Kind: logic-error label; actually a correct two-gate design.
- Source: equality requires both the parent's `getDescription()` (distinct DESCRIPTION per shape) AND `customEqualsCheck` (which for path shapes uses a loose `instanceof AbstractPathBasedSGMSurfaceFeature` that alone cannot separate Triangle/Diamond/Trapezoid/Tee). Correctness depends on the description compare firing first.
- Resolution: replicate. The port's base value-equality must compare a shape-type field; the subtype check should handle only subtype-specific numeric fields. Folding type-checking into the subtype method alone over-matches across the four path shapes.
- Acceptance bar: yes (shape-type discrimination, letter A).

### core-composite-shallow-copy-shared-features + gen-case3-no-clone-shared-ref
- Location: `SGMCompositeCell.java:67-68`, `SGMBaseCell.combineWithIgnoringLocation:156-163`, `SGMMatrix.java:368-399` (case 2 clones) and `:456-468` (case 3 no clone).
- Kind: other / identity-vs-value.
- Source: composite cells and combined lists share feature references (shallow). Distractor case 2 explicitly clones before mutating fill/scale; case 3 adds references without cloning but never mutates them. The aliasing contract is intentional and documented.
- Resolution: replicate (case 2 clone-before-mutate is mandatory); flag-and-decide for case 3 (if the port makes features immutable value objects, sharing is harmless). Equality is value-based throughout, so sharing does not corrupt dedup.
- Acceptance bar: no (distractor mechanics).

### ui-no-headless-batch-entrypoint + ui-no-retry-on-insufficient-answers + ui-generate-rng-draw-order-coupling
- Location: `Main.java:30-34` (empty stub); `SGMBuilderFrame.java:1086-1373` (`generateMatrix`).
- Kind: other / dead-code / rng-coupling.
- Source: there is no CLI batch path; `generateMatrix` reads the RNG seed and every per-layer relation/direction/supplemental from Swing widgets inside the method body, and its retry guard is commented out ("taking this out to prevent GUI from hanging"). In the UI path `correctAnswerPosition` is user-supplied, not RNG-drawn; the batch path draws it.
- Resolution: flag-and-decide. The port must reconstruct a headless generator that takes seed and all per-layer options as parameters, and should follow `SGMMatrixSetGenerator`'s retry (matching the paper's 8-choice requirement) with a hang-prevention bound. `getAnswerChoices()` is pre-padded with nulls to `numAnswerChoices`, so `featureScores[1]` is unaffected; the real impact of no-retry is blank cells in the answer grid.
- Acceptance bar: no for the RNG-draw distractor coupling; the architecture work is prerequisite to reaching the oracle at all.

### gen-unbounded-generation-loop
- Location: `SGMMatrixSetGenerator.java:140-189`.
- Kind: other.
- Source: `while(!done)` has no max-iteration guard. Two discard paths (under-generated answer choices via `continue`; full difficulty bin via `addSGMScore` returning false) both consume RNG before discarding, so discarded candidates advance the shared stream. An unsatisfiable distribution hangs forever.
- Resolution: flag-and-decide. Replicate discard-still-advances-RNG for determinism; add a max-iteration or timeout guard as a new safeguard and decide the failure mode.
- Acceptance bar: no (set-generation termination).

### fill-paint-alpha-nonuniform
- Location: fillpattern constructors (Black a=0.75, White a=0.0, Grey75 a=0.4, Grey40 a=0.5, Grey10 a=0.6).
- Kind: other.
- Source: alpha is deliberately non-monotonic in grey level (darker greys carry higher alpha); White at alpha 0.0 is transparent fill, visible only via its black stroke.
- Resolution: replicate. The SVG renderer must not assume uniform opacity or a simple grey-to-alpha mapping.
- Acceptance bar: no (rendering).

---

## Low severity

### core-matrix-size-check-self-compare + gen-layer-size-self-compare
- Location: `SGMMatrix.java:171-182` (line 173).
- Kind: logic-error.
- Source: `!layer.getSGMMatrixSize().equals(layer.getSGMMatrixSize())` is a self-comparison, always false, so the guard never fires and the exception is dead. The exception message also reads `this.getSGMMatrixSize()`, which is null at that point (set at line 185).
- Resolution: fix-to-paper. Compare the constructor parameter `sgmMatrixSize` to each layer's size and use the parameter in the message. Do not replicate the dead guard.
- Acceptance bar: no.

### core-cell-hashcode-equals-contract
- Location: `SGMBaseCell.java:179-186` (hashCode) vs `:202-230` (equals).
- Kind: logic-error.
- Source: `hashCode` delegates to `surfaceFeatures.hashCode()` (identity-derived, since features lack `hashCode`) while `equals` is value-based - a contract violation. Harmless in Java because cells are never put in a `HashSet`/`HashMap`; dedup uses a linear scan.
- Resolution: flag-and-decide. In Python, either implement `__hash__` consistent with `__eq__` over feature values and location, or make cells unhashable and keep the linear-scan dedup. Do not use cells as dict keys without a consistent hash.
- Acceptance bar: no.

### core-location-equals-null-npe
- Location: `SGMLocation.java:114-125`.
- Kind: other.
- Source: typed `equals(SGMLocation)` has no null guard. Null-location cells are deliberately built for answer/distractor cells (`SGMMatrix.java:475,564`) but are never passed to `combineWith` and cell equality compares only features, so the NPE path does not exist in the shipped code.
- Resolution: flag-and-decide. The null-location design is intentional; add an explicit guard in the port to avoid a latent AttributeError if a future path compares a null location.
- Acceptance bar: no.

### checkCompatibility dead code (core-feature-checkcompatibility-dead, base-checkcompat-stub, supp-checkcompatibility-unimplemented)
- Location: `SGMFeature.checkCompatibility` and all 11+ concrete implementations across surface and structure subsystems.
- Kind: dead-code.
- Source: declared on the interface, propagated abstract, implemented everywhere as `throw new UnsupportedOperationException("Not supported yet.")`, zero call sites. `SGMLayerGenerator.java:100` has a TODO acknowledging the compatibility gate was planned but never built.
- Resolution: omit from the port. Do not invent semantics.
- Acceptance bar: no.

### core-matrix-clone-unsupported
- Location: `SGMMatrix.clone:661-664`, `SGMLayer.clone:369-372`.
- Kind: dead-code.
- Source: both throw `UnsupportedOperationException`; no call site invokes clone on a matrix or layer (the `clone()` calls in the source operate on surface features, which clone correctly).
- Resolution: replicate (no working matrix/layer deep-copy to provide; the generator never needs one).
- Acceptance bar: no.

### RNG draws that look free but consume state (base-rng-nextint1-consumes-draw, base-rng-logic-assignment-loop)
- Location: `BaseSGMStructureFeatureGenerator.java:150` (`nextInt(1)`); `AbstractLogicOperationSGMStructureFeature.java:80-155` (while-loop).
- Kind: rng-coupling.
- Source: `nextInt(1)` always returns 0 but advances the LCG by one draw. The logic-op assignment while-loop draws an unbounded, data-dependent number of times until every base feature is assigned and all 4 base locations are populated.
- Resolution: replicate exactly for any seed-reproducible output.
- Acceptance bar: no (determinism only; out of bar).

### rot-wrong-comment
- Location: `ApplyRotationSGMStructureFeature.java:94`.
- Kind: other.
- Source: the comment reads "Apply scaling to the feature" (copy-pasted from ApplyScaling) above a correct `setRotation` call.
- Resolution: replicate the correct rotation logic; a porter scanning by comment could wrongly copy the scale logic.
- Acceptance bar: no (cosmetic, but a porting trap).

### loc-vert-getparent-numcolumns
- Location: `VerticalSGMLocationTransform.java:108`.
- Kind: logic-error.
- Source: `getParentLocationForStructureFeatureUse` wraps the row using `getNumColumns()-1` instead of `getNumRows()-1`. Masked at square 3x3 (the only size the tool builds), so it never produced a wrong result in the released tool.
- Resolution: fix-to-paper. Use `numRows`. The 3x3 oracle is unaffected, but the intent must be ported correctly.
- Acceptance bar: no (3x3 masks it).

### loc-diag-validate-after-super
- Location: `DiagonalBottomLeftTopRightSGMLocationTransform.java:77-86` (and TL->BR, Logic).
- Kind: logic-error (init anti-pattern).
- Source: `super()` calls the overridable `populateBaseLocations()` before the subclass size validation runs, so invalid sizes build out-of-range locations transiently before the guard throws. Net external behaviour is still a clean throw.
- Resolution: replicate cleanly - validate size first, then populate, in the port's `__init__`. Do not replicate the Java init order.
- Acceptance bar: no.

### Exception-message cosmetics (loc-diag-tlbr-wrong-exception-text, loc-exception-msg-missing-spaces)
- Location: `DiagonalTopLeftBottomRightSGMLocationTransform.java:83-85` (wrong diagonal name, copy-pasted); both diagonal classes and `LogicSGMLocationTransform.java:70-71` (elided spaces from string concatenation).
- Kind: copy-paste / other.
- Source: message text is wrong or malformed; the guard logic is correct.
- Resolution: fix-to-paper. Write correct messages from the start.
- Acceptance bar: no.

### Misnamed file headers (surface-header-misnamed-multiple, fill-grey10-filename-header)
- Location: `AbstractPathBasedSGMSurfaceFeature.java:2`, `TeeSGMSurfaceFeature.java:2`, `TriangleSGMSurfaceFeature.java:2` (all "RectangleSGMSurfaceFeature.java"); `Grey10SGMFillPattern.java:2` ("Grey25SGMFillPattern.java").
- Kind: mis-named.
- Source: copy-paste header artefacts; no runtime effect.
- Resolution: omit; use correct module names in the port.
- Acceptance bar: no.

### surface-customcheck-fill-uses-other-not-cast
- Location: `RectangleSGMSurfaceFeature.java:190`, Ellipse, AbstractPathBased, Line.
- Kind: other.
- Source: fill comparison calls `getFillPattern()` on the interface-typed `other`, while dimension comparison uses the cast `otherCasted`. Both reference the same object; the distinction is stylistic. The cast is needed only for subtype-only dimension accessors.
- Resolution: replicate the structure; in Python compare via attributes on a single typed object.
- Acceptance bar: no.

### Line fill equality vs intent (surface-line-fill-compared-contradicts-intent, fill-line-equality-includes-fill)
- Location: `LineSGMSurfaceFeature.java:180-196` vs commented-out `AbstractSGMSurfaceFeature.java:183-209`; Line generation is commented out in `SGMSurfaceFeatureGenerator.java:197-201`.
- Kind: commented-out.
- Source: the live `customEqualsCheck` compares fill for lines, contradicting the revision-log intent ("fill pattern is irrelevant for them"). Line is never generated, so the bug has zero impact on the oracle.
- Resolution: fix-to-paper (exclude fill from line equality, matching stated intent) is the safe call; flag-and-decide if Line is ever re-enabled. Add a TODO noting the decision.
- Acceptance bar: no (Line excluded from generation).

### gen-logic-op-traversal-comment-mismatch
- Location: `SGMLayer.java:203-241`.
- Kind: dead-code (stale comments; code is correct).
- Source: the outer comment claims a diagonal-up-right traversal but the loop is plain row-major, and the two inner branch comments are swapped. The code derives the third cell of each row left-to-right (`row<=1`) and each column top-to-bottom (`row>1`), which matches the paper exactly.
- Resolution: replicate the code, ignore the comments. A porter trusting the comment would implement a wrong diagonal traversal.
- Acceptance bar: yes for the behaviour (the code is correct; the trap is in the comments).

### gen-numerosity-detect-by-description-string
- Location: `SGMMatrix.java:330-336`.
- Kind: other.
- Source: case 2 detects a numerosity layer by string-comparing `getDescription()` against `"Numerosity"`. All nine structure-feature descriptions are currently distinct, so no mis-detection occurs; the fragility is latent.
- Resolution: flag-and-decide. Use isinstance dispatch in the port; record as an ADR. A collision would desync the RNG (non-numerosity branch draws an extra featureIndex).
- Acceptance bar: no (distractors).

### gen-numlayers-zero-guard
- Location: `SGMMatrixSetGenerator.java:144,150`; `SGMLayerGenerator.java:88`.
- Kind: off-by-one.
- Source: no setter validates `maxLayersPerMatrix`, `numAnswerChoices`, or `maxStructureFeaturesPerLayer` >= 1. `nextInt(0)` throws in Java; an idiomatic Python port using `randrange` also raises, so there is no silent divergence. The GUI and test always supply safe values.
- Resolution: flag-and-decide. Add boundary validation; avoid a `% n` port idiom that would silently produce wrong values.
- Acceptance bar: no.

### render-rastersettings-unused-in-generate
- Location: `SGMBuilderFrame.java:1086-1373` (param unread) vs `SGMMatrixSetGenerator.java:159` (param actively read).
- Kind: dead-code.
- Source: the `RasterSettings` parameter is dead inside `generateMatrix` (which uses frame fields), but it is NOT dead overall: `SGMMatrixSetGenerator.generateMatrices` reads `rasterSettings.getSGMCellRasterImagePixelSize()` to size layer generation.
- Resolution: flag-and-decide. Drop the dead parameter from the UI-equivalent method, but keep and wire a sizing config through the batch generator path.
- Acceptance bar: no (rendering/sizing).

### diff-score-equals-vs-compareto-nan
- Location: `SGMScore.java:76-115`.
- Kind: other.
- Source: `compareTo` uses `Double.compare` (NaN total ordering) while `equals` uses `==` (NaN != NaN); `hashCode` canonicalises NaN. Contract violation only triggered by NaN scores (degenerate regression output), which the tool does not normally produce. The TreeSet binner in `SGMScoreDistribution` relies on `compareTo`.
- Resolution: flag-and-decide. Pick one consistent comparison semantics in the port (total ordering throughout, or raise on NaN construction).
- Acceptance bar: no (difficulty binning).

### diff-sb-deletecharat-empty
- Location: `SGMMatrixDifficultyClassifier.java:389`.
- Kind: off-by-one.
- Source: `sb.deleteCharAt(sb.length()-1)` trims a trailing underscore appended per layer; with zero layers it throws. The generator guarantees at least one layer (`nextInt(max)+1`), so the path never fires in production.
- Resolution: flag-and-decide. Guard `if len(sb) > 0` so a port test that builds a zero-layer matrix directly does not crash.
- Acceptance bar: no.