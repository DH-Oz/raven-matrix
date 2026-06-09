# PORT-NOTES — cared-about upstream findings (co-located index)

Derived from `docs/upstream-analysis/bug-catalog.md` (full location + evidence there).
Only the findings that touch the **acceptance bar** (structure + correct-answer position)
are listed; distractor-variety / RGBA / cosmetic findings are omitted on purpose.

Disposition: **REPLICATE** = reproduce the upstream behaviour (oracle was made with it);
**FIX-TO-PAPER** = genuine bug, follow the paper; **FLAG-AND-DECIDE** = needs a human call.
The dominant theme is identity-vs-value equality (a Phase 4 decision).

## surface (shapes/equality)
- **FIX-TO-PAPER** `surface-clone-drops-size-rect-ellipse` — The copy constructor for RectangleSGMSurfaceFeature and EllipseSGMSurfaceFeature calls only super(other), which correctly copies the Java Shape object (Rectangl
- **FIX-TO-PAPER** `surface-equals-no-object-override` — AbstractSGMSurfaceFeature defines a typed overload equals(SGMSurfaceFeature) but never overrides equals(Object) or hashCode()
- **REPLICATE** `surface-equals-not-symmetric-typeguard` — AbstractSGMSurfaceFeature.equals(SGMSurfaceFeature) correctly combines two guards: the parent's getDescription() string compare (which distinguishes all seven c

## core model (cells/matrix/feature)
- **FIX-TO-PAPER** `core-cell-containsfeaturecheck-ignores-param` — containsFeatureCheck (lines 188-200) takes a List parameter named `surfaceFeature` but its loop body iterates the instance field `this.surfaceFeatures`, ignorin
- **FIX-TO-PAPER** `core-logicop-contains-identity` — AbstractSGMSurfaceFeature defines equals(SGMSurfaceFeature other) — a typed overload — but does not override Object.equals(Object)
- **FLAG-AND-DECIDE** `core-surface-equals-no-object-override` — AbstractSGMSurfaceFeature defines only the typed overload equals(SGMSurfaceFeature) with no @Override boolean equals(Object) and no hashCode
- **REPLICATE** `core-correctanswer-reposition-rng` — The correct-answer position is RNG-determined in two stages
- **REPLICATE** `core-derivedcell-provenance-not-in-equals` — SGMDerivedCell adds baseCell and parentCell fields but inherits SGMBaseCell.equals, which compares only surfaceFeatures (by value, bidirectionally)

## structure/base (logic + shaperep)
- **FIX-TO-PAPER** `base-logic-dedup-typemismatch` — At lines 99-100 of AbstractLogicOperationSGMStructureFeature.java, the dedup guard `list.contains(featureIndex)` is called on a `List<SGMSurfaceFeature>` with a
- **FIX-TO-PAPER** `base-logic-identity-contains` — AbstractSGMSurfaceFeature defines equals(SGMSurfaceFeature) as a typed overload — not an override of Object.equals(Object)
- **FLAG-AND-DECIDE** `base-logic-identity-works-only-by-sharing` — The Java logic ops (AND/OR/XOR) call `List.contains(feature)` which in Java dispatches to `Object.equals()` — reference identity — because `AbstractSGMSurfaceFe
- **REPLICATE** `base-logic-singlearg-transform-throws` — AbstractLogicOperationSGMStructureFeature overrides the single-arg transformSurfaceFeatures(list) to throw UnsupportedOperationException (lines 167-175)

## supplemental: numerosity
- **FLAG-AND-DECIDE** `numerosity-transform-null-deref` — transformSurfaceFeatures (lines 190-193) dereferences existingSurfaceFeaturesAtLocation.get(0) with no null guard
- **REPLICATE** `numerosity-scale-base-vs-transform-mismatch` — The asymmetry between the base path (absolute setScale) and transform path (multiplicative setScale) is real and verified at lines 153 and 201 respectively
- **REPLICATE** `numerosity-topleftcornerout-formula` — TranslationalNumerositySGMStructureFeature constructor (lines 100-117) uses two distinct formulas for numPositions: ceil(sqrt(rows+cols-1)) when the location tr
- **REPLICATE** `numerosity-transform-count-offbyone` — The `<=` bound in `transformSurfaceFeatures` at line 190 is intentional and correct

## supplemental: repetition
- **FLAG-AND-DECIDE** `repetition-firstfeature-only` — In AbstractRepetitionSGMStructureFeature.transformSurfaceFeatures (lines 122-134), when iterating over all features in the current cell to apply a supplemental 

## supplemental: scaling
- **FLAG-AND-DECIDE** `scale-wrong-comment-and-clone-shared-fill` — The copy constructor in AbstractSGMSurfaceFeature (lines 108-115) shallow-copies the SGMFillPattern reference: `this.setFillPattern(other.getFillPattern())`

## locationtransform (directions)
- **REPLICATE** `loc-tlco-getparent-no-bottomrow-special` — getParentLocationForStructureFeatureUse for TopLeftCornerOut uses a simple "column-first, then row" rule — (row-1, col) if row>0, else (row, col-1) — which is d

## fillpattern + change/repeat fill
- **FLAG-AND-DECIDE** `fill-changefill-indexof-identity` — applyTransform (ChangeFillPatternSGMStructureFeature.java:102-105) uses List.indexOf to find the previous cell's fill in baseFillPatterns
- **FLAG-AND-DECIDE** `fill-no-equals-hashcode` — AbstractSGMFillPattern has no equals/hashCode, so fills compare by reference identity
- **FLAG-AND-DECIDE** `fill-pattern-cycling-identity` — The `applyTransform` method in `ChangeFillPatternSGMStructureFeature` uses `List.indexOf` to locate the current fill pattern, which resolves to Java object-iden
- **REPLICATE** `fill-changefill-base-uses-get0-only` — ChangeFillPattern.provideBaseSurfaceFeatures fixes all base-location cells to baseFillPatterns.get(0) (the first fill in the configured list, not necessarily Wh
- **SEE-CATALOG** `fill-changefill-indexof-identity (dup)` — 

## supplemental: rotation
- **FLAG-AND-DECIDE** `rot-only-45-degrees` — The rotation step is hardcoded to 45 degrees in SupplementalSGMStructureFeatureGenerator (line 234-235, confirmed)

## generation (set/layer generators)
- **FLAG-AND-DECIDE** `gen-unspecified-logic-50pct` — SGMMatrixSetGenerator calls SGMLayerGenerator.generateLayer(), which calls the three-argument overload of BaseSGMStructureFeatureGenerator.generateStructureFeat
- **REPLICATE** `gen-base-surface-hashset-identity` — SGMLayer.baseSurfaceFeatures is a HashSet<SGMSurfaceFeature>
- **REPLICATE** `gen-correct-answer-relocation` — After the wrong-answer generation loop, SGMMatrix checks whether the stored correctAnswerPosition exceeds positionInAnswerChoices (the count of successfully pla
- **REPLICATE** `gen-diagonal-only-odd-square` — The parity/squareness gate is real and must be replicated: diagonal transforms (BL→TR and TL→BR) are only reachable in the UNSPECIFIED random path when `numRows
- **REPLICATE** `gen-logic-op-traversal-comment-mismatch` — The outer comment at SGMLayer.java:203-204 ("starting in third row and moving diagonally up and to the right") is stale and misleading
- **REPLICATE** `gen-supplemental-disabled-when-logic-base` — When the base structure feature is a logic operation (AND/OR/XOR), `SGMLayerGenerator` skips the supplemental-feature loop entirely, so a logic-op layer always 

## rendering
- **REPLICATE** `render-answer-cell-hardcoded-bottom-right` — The source uses two distinct "answer position" concepts that must not be conflated in the port

## ui / headless entry
- **FLAG-AND-DECIDE** `ui-gui-cannot-make-3layer-or-logic-stim` — The GUI hard-caps numLayers at 2 (line 1029: `int numLayers = (OneLayer.isSelected()?1:2)`), so it cannot produce the "3 Layer Stim" folder of the oracle

## rng / determinism
- **REPLICATE** `rng-type-mapping-enum-vs-switch` — The integer-to-feature-type mapping in the switch (0=Scaling, 1=FillRepetition, 2=Rotation, 3=Numerosity, 4=ChangeFill) is an internal convention with no connec

