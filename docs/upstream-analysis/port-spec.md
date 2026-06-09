# SGMT to Python port spec (from source)

This spec maps the Java SGMT v1.0.0 source onto the planned Python 3.14 port, subsystem by subsystem. The acceptance bar is data/logic equivalence: structure (relations, directions, layers) plus correct-answer position, judged against the Matzen 2010 norming spreadsheet. Distractor content and pixels are out of bar (seeds unpublished). The paper is the fundamental spec; bug-catalogue ids are cross-referenced inline.

## Porting order / dependencies

The subsystems map onto five phases. Port the JUnit tests first within each phase - they are the executable spec.

1. Model (phase 1): core-model + fillpattern + surface. These are the value objects. The dominant decision here is identity-vs-value equality for surface features and fills (`surface-equals-no-object-override`, `fill-no-equals-hashcode`). Decide once, apply consistently, and pin with tests before building anything on top.
2. Transforms (phase 2): locationtransform + structure-base + structure-supplemental. Directions and relations. Port `TopLeftCornerOutSGMLocationTransformTest` and the logic-op derivation rule verbatim.
3. Build (phase 3): generation (SGMLayer, SGMLayerGenerator, SGMMatrix, SGMMatrixSetGenerator) and a reconstructed headless entry point (the GUI's `generateMatrix` lifted to a pure function). Port `SGMMatrixSetGeneratorTest`.
4. Oracle (phase 4): structural and normative checks against the spreadsheet. Drive generation by explicit `*Type` enums, never the UNSPECIFIED stochastic path (`gen-unspecified-logic-50pct`). The difficulty classifier feeds the normative oracle; the learned estimator must be re-derived or re-trained.
5. Renderer (phase 5): SVG canonical, rasterise to PNG. Out of the acceptance bar; needed only when a bitmap is wanted.

Cross-phase invariant: a single `java.util.Random` instance is threaded through the whole build. If byte-exact seed reproduction is ever wanted, the port must replicate Java's 48-bit LCG (`next(bits)`, `nextInt(bound)` power-of-two fast path plus rejection loop, `nextBoolean`, `nextDouble`) bit-for-bit and preserve exact draw order. For the acceptance bar this is unnecessary except where it touches correct-answer position.

---

## Subsystem: core-model

The in-memory data model: a matrix is a grid of cells; each cell holds an ordered list of surface features; layers are matrices applying one base relation plus supplementals; `SGMMatrix` composites layers cell-by-cell and generates answer choices.

Key classes: `SGMMatrix` (composites layers, picks bottom-right cell as correct answer before distractor RNG, may relocate it), `AbstractSGMMatrix` (size + grid; clone is dead), `SGMLayer` (one relation, logic-op vs non-logic paths), `SGMBaseCell` (value set-equality of features), `SGMCompositeCell` (shallow-copy wrapper), `SGMDerivedCell` (provenance not in equals), `SGMLocation`/`SGMMatrixSize` (correct value equality, port as frozen dataclass/NamedTuple), exceptions (size-mismatch guard is dead).

Porting-relevant semantics:
- Identity-vs-value: cell equality is value-based set-equality; surface features inside are identity-compared by Java collections (`core-surface-equals-no-object-override`). Cell hashCode is identity-derived while equals is value-based (`core-cell-hashcode-equals-contract`) - do not hash cells without a consistent `__hash__`.
- Cell equality has a real bug: `containsFeatureCheck` ignores its parameter (`core-cell-containsfeaturecheck-ignores-param`), degenerating equals to one-directional plus a dead loop. Fix to genuine mutual-subset.
- Provenance: `SGMDerivedCell` must compare by visible content only; including baseCell/parentCell breaks distractor dedup (`core-derivedcell-provenance-not-in-equals`).
- Mutable shared state: composite cells and combined lists share feature references; distractor case 2 clones before mutating (`core-composite-shallow-copy-shared-features`). Preserve clone-before-mutate or make features immutable value objects.
- Correct-answer position: always the bottom-right composited cell, set before distractor RNG; can be relocated by a conditional `nextInt` draw (`core-correctanswer-reposition-rng`, `gen-correct-answer-relocation`).
- Integer notes: rotation stored as `rotation % 360` (Java signed remainder differs from Python; `rot-only-45-degrees`, surface notes). Dead size-check (`core-matrix-size-check-self-compare`). `clone()` on matrix/layer is dead (`core-matrix-clone-unsupported`). `checkCompatibility` is dead everywhere (`core-feature-checkcompatibility-dead`).

Determinism notes: answer dedup uses a manual linear value-equality scan, never a hash set - replicate with a list, not a Python set, or the build becomes non-deterministic. `SGMLocation.equals` has no null guard but the NPE path does not exist in shipped code (`core-location-equals-null-npe`).

---

## Subsystem: fillpattern

Five shadings plus the RNG selector. `SGMFillPattern` (description + paint), `AbstractSGMFillPattern` (no equals/hashCode), Black/White/Grey75/Grey40/Grey10, `SGMFillPatternGenerator`.

Porting-relevant semantics:
- The Grey10/Grey40 "Red" collision is the headline fill bug (`fill-grey10-grey40-red-collapse` and merged ids). Both report DESCRIPTION "Red", and surface equality compares fills by description, so two of five shadings are value-equal. Fix to five distinct labels; the project decided to keep five shadings distinct. Render still differs because the change-fill cycle advances by index, not description.
- Index-based cycling: ChangeFillPattern advances `(indexOf+1) % size`; FillPatternRepetition seeds by `index % size`. Deterministic given identity holds.
- Identity-vs-value: fills have no equals/hashCode, so `List.indexOf`/`contains` use identity (`fill-changefill-indexof-identity`, `fill-pattern-cycling-identity`). Port fills as an enum/value type so `index()` is value-based; this removes the latent reset-to-White hazard on `indexOf == -1`.
- Palette split (`fill-bare-generator-only-3-of-5`, `fill-repetition-only-three-fills`): the no-arg generator and FillPatternRepetition use only 3 fills (White/Grey75/Black); only ChangeFillPattern uses all 5. Fix-to-paper for the generator; flag-and-decide for FillPatternRepetition because the normed PNGs were generated with the 3-fill subset.
- Alpha is non-monotonic and load-bearing for rendering only (`fill-paint-alpha-nonuniform`).

Determinism notes: `generateFillPattern(random)` consumes exactly one `nextInt(3)`; the allowed-list overload one `nextInt(size)`. Mapping order 0->White, 1->Grey75, 2->Black is load-bearing. Lists are searched in insertion order.

---

## Subsystem: surface (shapes + equality)

`SGMSurfaceFeature` (typed `equals(SGMSurfaceFeature)` only), `AbstractSGMSurfaceFeature` (shared equality, no `equals(Object)`/`hashCode`), bounds-based Rectangle/Ellipse, path-based Triangle/Diamond/Trapezoid/Tee via `AbstractPathBasedSGMSurfaceFeature`, standalone Line, `SGMSurfaceFeatureGenerator`.

Porting-relevant semantics:
- Identity-vs-value is the root decision (`surface-equals-no-object-override`, `core-surface-equals-no-object-override`). Java collection ops use identity; the typed overload is dead for `contains`/`HashSet`. Implement `__eq__`/`__hash__` by value (shape type, scale, rotation, position, fill) and re-derive the logic ops and difficulty dedup against that choice. This is the single biggest source of Logic-Stim divergence.
- Clone drops size (`surface-clone-drops-size-rect-ellipse`, `surface-clone-drops-size-pathbased`): copy ctors call only `super(other)`, leaving private width/height 0.0, so `customEqualsCheck` mis-compares clones. Derive width/height from shape bounds in value-equality, or copy them in the clone path. Line is the exception (copies length).
- Two-gate equality (`surface-equals-not-symmetric-typeguard`): the base description compare distinguishes the seven shape types; `customEqualsCheck` for path shapes uses a loose `instanceof` and cannot separate the four path shapes alone. The port's base value-equality must compare a shape-type field.
- getDescription returns the shape-type string; fill description is compared inside customEqualsCheck (where the Grey collision lives).
- rotation `% 360` sign behaviour differs Java vs Python; normalise identically. Position compared by exact float `==`; mirror Java's exact expressions.
- Generator produces 6 shapes (Ellipse, Rectangle, Triangle, Tee, Diamond, Trapezoid); Line is commented out (`surface-line-fill-compared-contradicts-intent`, `fill-line-equality-includes-fill`). Exclude Line from generation; if re-enabled, decide whether fill participates in line equality.
- Header mis-naming is cosmetic (`surface-header-misnamed-multiple`).

Determinism notes: `SGMSurfaceFeatureGenerator` draw order is data-dependent (extra `nextInt(2)` only in the height else-branch; then `nextBoolean` swap; then fill; then `nextInt(6)` type). Square/circle prevention is in the width/height branch - port it exactly. Clone producing zero size is deterministic but collapses value-equality on size unless fixed alongside clone.

---

## Subsystem: locationtransform (directions)

The five traversal directions plus the Logic marker. `SGMLocationTransform` (interface), `AbstractSGMLocationTransform`, Horizontal/Vertical/DiagonalBottomLeftTopRight/DiagonalTopLeftBottomRight/TopLeftCornerOut, `LogicSGMLocationTransform` (stub, next/parent throw), `SGMLocationTransformGenerator`.

Each transform exposes `populateBaseLocations` (seed cells), `createNextLocation` (forward walk), `getParentLocationForStructureFeatureUse` (backward step the relation transforms from - NOT always the inverse of next).

Porting-relevant semantics:
- Value equality drives cycle termination: `SGMLocation` has proper value equals/hashCode; the generation loop runs `while not current.equals(base)`. The port's Location MUST have value `__eq__`/`__hash__` or the walk never terminates. This contrasts with surface features (identity).
- Constructor argument order: `SGMLocation(row, column)`, `SGMMatrixSize(numRows, numColumns)`. Keep the order or rows/cols silently swap.
- Integer wrap arithmetic with explicit `if x >= N: x = 0` / `if x < 0: x = N-1`. All ints.
- TopLeftCornerOut parent rule is a distinct "above-else-left" rule, not the inverse of the wavefront (`loc-tlco-getparent-no-bottomrow-special`). The JUnit test is the spec; port branch-for-branch.
- Vertical getParent uses numColumns instead of numRows (`loc-vert-getparent-numcolumns`) - masked at 3x3; fix to numRows.
- Validate-then-populate: the Java ctor calls the overridable populate before validation (`loc-diag-validate-after-super`). In Python validate size first.
- Exception messages have a wrong diagonal name and elided spaces (`loc-diag-tlbr-wrong-exception-text`, `loc-exception-msg-missing-spaces`) - write correct messages.
- Logic problems bypass next/parent (those throw); special-case logic in the layer generator.

Determinism notes: one RNG draw - `nextInt(3)` for non-square-or-even, `nextInt(5)` for odd-square. Integer-index type mapping (0 Horizontal, 1 Vertical, 2 TopLeftCornerOut, 3 DiagBLTR, 4 DiagTLBR) is fixed and is NOT the enum declaration order nor the Matzen direction digits. Base locations are ArrayList insertion order - use an ordered list, never a set.

---

## Subsystem: structure-base (relations + logic)

`ShapeRepetition` and the three logic ops, plus `BaseSGMStructureFeatureGenerator`. A base feature carries a location transform and exposes `provideBaseSurfaceFeatures(index)` and `transformSurfaceFeatures(...)`.

Porting-relevant semantics:
- Identity-vs-value dominates: AND/OR/XOR combine features with `List.contains`/`!contains`, which is identity in Java (`base-logic-identity-contains`, `core-logicop-contains-identity`, `base-logic-identity-works-only-by-sharing`). It produces paper-correct sets only because feature instances are shared and never cloned. Fix to value equality (the paper's intent) and re-validate on the Logic Stim folder.
- Logic-op dedup type mismatch (`base-logic-dedup-typemismatch`): the assignment guard `list.contains(featureIndex)` compares an Integer to a `List<SGMSurfaceFeature>`, always false, so a base location can receive the same feature twice. Fix to check feature membership.
- Single-arg transform throws for logic ops (`base-logic-singlearg-transform-throws`); the layer builder must branch on logic-op type and call the two-arg derivation.
- Logic spatial derivation (consumed in SGMLayer): base locations are the top-left 2x2; derived cell `[r][c]` comes from `([r-2][c],[r-1][c])` when `r>1` else `([r][c-2],[r][c-1])`, filled row-major. The outer comment claims a diagonal traversal but the code is row-major and correct (`gen-logic-op-traversal-comment-mismatch`) - port the code, ignore the comment.
- ShapeRepetition cycles `index % size`; transform is identity (repetition is the location transform walking the same shape list).
- Output list order matters: OR = cell1 then cell2-extras; XOR = cell1-only then cell2-only; AND = cell1-order intersection. Preserve.
- Logic-op base features are forced White-only fill; unique shape classes per layer are enforced by a re-roll loop.

Determinism notes: draw order is `nextInt(2)`/`nextInt(1)` type (`base-rng-nextint1-consumes-draw`), then for logic `numSurfaceFeatures` in [3,5], a per-feature generation loop, `logicalType` `nextInt(3)`, then the stochastic assignment while-loop (`base-rng-logic-assignment-loop`). `containsCheck` (value-based) is the one correct value-equality site. All RNG is out of bar except where it reaches correct-answer position.

---

## Subsystem: structure-supplemental (rotation/scaling/fill/numerosity)

`ApplyScaling`, `ApplyRotation`, `FillPatternRepetition`, `ChangeFillPattern`, `TranslationalNumerosity`, their abstract bases, and `SupplementalSGMStructureFeatureGenerator`. `AbstractRepetitionSGMStructureFeature` clones each existing feature then mutates one attribute from the previous cell's first feature.

Porting-relevant semantics:
- Fill identity: ChangeFillPattern `indexOf` is identity-based and works only via shared references (`fill-changefill-indexof-identity`); port fills as value types. ChangeFillPattern seeds all base cells with `get(0)` while FillPatternRepetition seeds by `index % size` (`fill-changefill-base-uses-get0-only`) - replicate the asymmetry.
- Numerosity: base path `setScale(scaling)` absolute vs transform path `setScale(scaling * feature.getScale())` multiplicative (`numerosity-scale-base-vs-transform-mismatch`) - replicate both. Transform produces `prev.size()+1` clones via `i <= size` (`numerosity-transform-count-offbyone`) - keep `<=`, not `<`. Transform has no null guard (`numerosity-transform-null-deref`) - decide the null contract. numPositions uses a special formula for TopLeftCornerOut (`numerosity-topleftcornerout-formula`).
- Repetition first-feature-only workaround (`repetition-firstfeature-only`): always reads previous-cell `get(0)`, size guard commented out. Replicate for oracle equivalence (the norming set was generated with it active).
- Rotation hardcoded 45 degrees (`rot-only-45-degrees`); comment mislabeled "Apply scaling" (`rot-wrong-comment`). Replicate the 45-degree step for the orientation oracle.
- Type mapping by switch index, not enum ordinal (`rng-type-mapping-enum-vs-switch`): 0 Scaling, 1 FillPatternRepetition, 2 Rotation, 3 Numerosity, 4 ChangeFill. Use an explicit mapping dict.
- checkCompatibility dead everywhere (`supp-checkcompatibility-unimplemented`); omit.

Determinism notes: location transform is drawn FIRST, then `nextInt(5)` for type (UNSPECIFIED only) (`rng-locationtransform-then-type-order`); numerosity draws one extra `nextInt(2)+1` (`rng-numerosity-extra-draw`). Specified-type paths skip the type draw. The location-transform diagonal-exclusion gate must be ported identically or every subsequent draw desyncs.

---

## Subsystem: generation (the stochastic pipeline)

`SGMMatrixSetGenerator` (seeds one Random, loops to fill a score distribution), `SGMLayerGenerator`, the structure/surface/location generators, and the `SGMMatrix` answer-choice constructor.

Porting-relevant semantics:
- Drive the oracle by explicit `*Type` enums, never the UNSPECIFIED batch path (`gen-unspecified-logic-50pct`): the batch path makes a 50% logic coin-flip on 3x3, which cannot reproduce any fixed Structure code.
- Supplementals are skipped when the base is a logic op (`gen-supplemental-disabled-when-logic-base`) - replicate; logic layers are always single-relation.
- Correct-answer position can be relocated by a conditional draw (`gen-correct-answer-relocation`) - model it for the "Correct Answer" column.
- Wrong-answer strategy branches on layer count (`gen-wronganswer-type-by-layercount`); case 3 adds feature refs without cloning (`gen-case3-no-clone-shared-ref`); numerosity detection is by description string (`gen-numerosity-detect-by-description-string`). All distractor-side; out of bar.
- baseSurfaceFeatures HashSet is identity-dedup'd (`gen-base-surface-hashset-identity`) - affects difficulty count; replicate identity for the difficulty path.
- Diagonal directions only on odd-square (`gen-diagonal-only-odd-square`) - replicate the gate.
- Dead size guard (`gen-layer-size-self-compare`); unbounded generation loop with discard-advances-RNG (`gen-unbounded-generation-loop`); no zero-parameter guard (`gen-numlayers-zero-guard`).

Determinism notes: one shared Random threaded through layer, structure, surface, location, and answer-choice generation. Draw order per matrix: numLayers (`nextInt(max)+1`), then correctAnswerPosition (`nextInt(numAnswerChoices)`), then per-layer [numStructureFeatures, base feature, conditional supplementals], then wrong answers. Discarded candidates still consume RNG. Base vs supplemental generators draw the location transform at different points.

---

## Subsystem: difficulty + rendering + ui

`SGMMatrixDifficultyClassifier` (37-element feature vector to a learned regression `Evaluator`), `SGMScore`, `SGMScoreDistribution`, the Java2D image classes, and `SGMBuilderFrame` (the de-facto headless generator).

Porting-relevant semantics:
- Difficulty index mapping must be ported exactly. Fix the [35]/[36] overwrite (`diff-featurescore-35-36-index-overwrite`). `featureScores[27]` uses an identity-deduped surface-feature set (`diff-unique-surface-identity-dedup`) - decide identity vs value knowing the estimator was fit against the identity count. ChangeFillPattern collapses to 'B' in the debug string and has no feature slot (`diff-changefill-fillrepetition-collapse-to-B`, `diff-changefillpattern-no-feature-slot`). The debug `sb` string is println-only and is NOT the spreadsheet Structure code. The learned estimator is external (Cognitive Foundry) and must be re-derived or re-trained; the regression coefficients are not in the source.
- `SGMScore` has a compareTo/equals NaN asymmetry (`diff-score-equals-vs-compareto-nan`); `deleteCharAt` can throw on zero layers (`diff-sb-deletecharat-empty`).
- Rendering: SVG canonical in the port. AffineTransform composition is reverse-of-call (scale-about-position, rotate, translate); rotation degrees to radians; stroke 2.0; fill via paint. The answer cell is hard-coded bottom-right and is a different concept from `correctAnswerPosition` (`render-answer-cell-hardcoded-bottom-right`) - keep them separate. RasterSettings is dead in `generateMatrix` but live in `SGMMatrixSetGenerator` (`render-rastersettings-unused-in-generate`).
- UI / batch path: `Main.java` is empty; there is no CLI path (`ui-no-headless-batch-entrypoint`). Reconstruct a headless `generate_matrix` that takes seed and all per-layer options as parameters (the GUI reads them from Swing widgets inside the method body). The retry guard is commented out (`ui-no-retry-on-insufficient-answers`) - follow `SGMMatrixSetGenerator`'s retry with a hang bound. The GUI caps layers at 2 and cannot produce the 3-Layer or Logic Stim folders (`ui-gui-cannot-make-3layer-or-logic-stim`) - target engine parity (N layers; logic transform implied by a logic base type). RNG draw order in `generateMatrix` is load-bearing for distractors only (`ui-generate-rng-draw-order-coupling`); in the UI path `correctAnswerPosition` is user-supplied, not drawn.

Determinism notes: HashMaps keyed by Class/enum/Integer are safe to port to dict (counts only, order-independent). The only identity hazard is the surface-feature sets. The while-loop retry in `generateMatrix` is a no-op (always finishes after one pass). Rendering is deterministic but out of bar.