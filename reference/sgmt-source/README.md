# SGMT 1.0.0 source — extracted read-only mirror

This is the Java source we **port FROM**, extracted for grep/read access so no
one has to unzip anything ad hoc.

- **Canonical artifact (provenance):** the zip vendored in the read-only
  `upstream/Matrices/` submodule —
  `Matrix Generation Software/SandiaGeneratedMatrixTool-1.0.0-source.zip`
  (OSTI `code-54699` · DOI `10.11578/dc.20210416.34` · BSD-3-Clause ·
  © 2010 Sandia Corporation, Contract DE-AC04-94AL85000).
- **This mirror** holds only `Source/` (the port source) and `Test/` (the JUnit
  spec); the third-party `Dependencies/` from the zip are omitted.
- **READ-ONLY.** Never edit these files — they are the immutable thing we port
  FROM. Re-derive the mirror with `bash tools/extract_upstream.sh`.

Package root: `Source/gov/sandia/cognition/generator/matrix/`.
