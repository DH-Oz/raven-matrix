# Java build spike — upstream SGMT v1.0.0

**Date:** 2026-06-09
**Task:** Phase 1, Task 5 (timeboxed spike). Records whether the upstream Java
builds, so later phases can optionally emit golden fixtures for a Java
differential. Outcome, not success, is the deliverable.

## Verdict

**yes** — golden fixtures are available. The upstream source compiles and
produces a self-contained, runnable jar with a single documented fix (drop
`-Werror`). The compiled classes include the headless generator
(`SGMMatrixSetGenerator`) and the difficulty classifier
(`SGMMatrixDifficultyClassifier`).

## Toolchain present

Selected by the repo-root `.envrc` (`JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64`).
The system default is already JDK 8, so the build works with or without sourcing
`.envrc`.

| Tool    | Version                                                              |
|---------|---------------------------------------------------------------------|
| `java`  | OpenJDK 1.8.0_492 (8u492, Ubuntu 24.04 build `25.492-b09`)           |
| `javac` | 1.8.0_492                                                            |
| `ant`   | Apache Ant 1.10.14 (compiled 2023-09-25)                             |

`/usr/lib/jvm/` also holds JDK 21 (`java-21-openjdk-amd64`); the spike used JDK 8
as `.envrc` directs (the NetBeans project pins `javac.source/target=1.6`).

## Build attempt

All work was done in a throwaway temp dir (`mktemp -d`); the read-only
`upstream/` submodule was never modified.

```bash
work=$(mktemp -d)
unzip -q "upstream/Matrices/Matrix Generation Software/SandiaGeneratedMatrixTool-1.0.0-source.zip" -d "$work"
cd "$work/SandiaGeneratedMatrixTool-1.0.0-source"
```

The project is a standard NetBeans Ant project (`build.xml` importing
`nbproject/build-impl.xml`); `nbproject/project.properties` sets
`javac.source=1.6`, `javac.target=1.6`, and
`javac.compilerargs=-Xlint -Werror -Xlint:-serial -Xlint:-path`.

### Plain `ant` — FAILED (one warning, escalated by `-Werror`)

```
[javac] Compiling 72 source files to .../Build/classes
[javac] warning: [options] bootstrap class path not set in conjunction with -source 1.6
[javac] error: warnings found and -Werror specified
[javac] 1 error
BUILD FAILED  (ant exit 1)
```

First (and only) error signature: the JDK 8 obsolete-bootstrap-classpath warning
for `-source 1.6`, turned into an error by the project's `-Werror`. This is a
toolchain-version artifact, **not** a source defect: the dependency classpath
resolved (no missing-jar failure) and `javac` reached all 72 files before the
warning fired.

### `ant` with the documented fix — BUILD SUCCESSFUL

Documented fix applied on the CLI only (project files untouched): override
`javac.compilerargs` to drop `-Werror`.

```bash
ant -Djavac.compilerargs="-Xlint:none" clean jar
```

Result:

```
[javac] Compiling 72 source files to .../Build/classes
[copylibs] Building jar: .../Distribution/gov-sandia-cognition-generator-matrix.jar
BUILD SUCCESSFUL
```

The direct-`javac` fallback was **not needed** — `ant jar` succeeded, so the
fallback was not exercised.

## Runnable artifact

```
Distribution/gov-sandia-cognition-generator-matrix.jar   (120,618 bytes)
Distribution/lib/  -> 7 bundled dependency jars
Build/classes/     -> 80 .class files (72 sources + inner classes)
```

Jar manifest:

```
Main-Class: gov.sandia.cognition.generator.matrix.ui.SGMBuilderFrame
Class-Path: lib/gov-sandia-cognition-common-core.jar lib/gov-sandia-cognition-common-data.jar
            lib/gov-sandia-cognition-learning-core.jar lib/mtj.jar lib/xpp3_min-1.1.4c.jar
            lib/xstream-1.3.1.jar lib/swing-layout-1.0.4.jar
```

The jar runs and resolves its full classpath. A headless invocation proves this:

```bash
java -Djava.awt.headless=true -jar Distribution/gov-sandia-cognition-generator-matrix.jar
# -> java.awt.HeadlessException at JFrame.<init> from SGMBuilderFrame.<init>:47
```

The `HeadlessException` is the *expected* result, and it is the proof of life:
the JVM loaded `SGMBuilderFrame`, found every dependency class (no
`NoClassDefFoundError`), entered the AWT event-dispatch thread, and failed only
when Swing tried to open a window with no display. The release is GUI-driven by
design — `Main.java` is an empty stub — so the default jar entry point is the
Swing frame, which cannot run headless as-is.

## How a headless fixture run would work

`SGMMatrixSetGenerator` and `SGMMatrixDifficultyClassifier` both compiled and are
present in `Build/classes`. A headless fixture emitter is a small custom main
that drives `SGMMatrixSetGenerator` directly (bypassing the Swing
`SGMBuilderFrame`), compiled and run against the bundled `lib/` jars under
`-Djava.awt.headless=true`. That custom main is the reconstructed batch path the
source map flags as needed (the release has no CLI entry point). It would serialise
the generator's RNG-driven surface realisations and distractor sets so the
optional Java differential (design "Additional Considerations") can compare them
against the port. That emitter is out of scope for this spike; the spike only
establishes that the toolchain and artifact exist to build it on.

## Bearing on the equivalence bar

Because the build succeeds, RNG-driven surface/distractor behaviour *can* later be
checked against the reference implementation via the headless emitter above. This
is a bonus: the project's acceptance bar is data/logic equivalence (structure +
correct-answer position + difficulty), not pixel or exact-distractor
reproduction, and the upstream RNG seeds are unpublished. The Java differential
remains optional and best-effort; the port does not depend on it.
