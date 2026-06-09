import java.util.Random;

/**
 * Golden-vector dumper for java.util.Random.
 *
 * Emits deterministic sequences from the real JVM LCG so the Python port
 * (raven_matrix.rng.JavaRandom, Phase 2) can be verified WITHOUT a JVM at test
 * time. Depends ONLY on java.util.Random — never on the SGMT jar — so it stays
 * robust regardless of the upstream build.
 *
 * Why these seeds (0, 1, 42, 2024, -1, 123456789): a spread including the
 * trivial seed 0, small seeds, one negative (-1, exercises the sign handling in
 * the (seed ^ MULTIPLIER) scramble), and one large positive (123456789).
 *
 * Why these bounds (2, 3, 5, 6) plus nextBoolean: upstream SGMT uses ONLY
 * Random.nextInt(bound) and Random.nextBoolean() (source-verified, DR3). 2 is a
 * power of two (the fast path: (bound * next(31)) >> 31); 3 and 5 and 6 are
 * non-powers-of-two that drive the rejection loop. nextBoolean covers the
 * width/height swap. Each (seed, method, bound) gets its OWN freshly-seeded
 * Random so Phase 2 can verify each method independently.
 *
 * Output: a single JSON object on stdout, hand-formatted for byte-stable,
 * deterministic regeneration (fixed key order, two-space indent, LF newlines,
 * no trailing whitespace). Parseable by Python's stdlib json.
 *
 * Run headless and locale-independent; uses only integer/boolean formatting so
 * no locale or platform variance enters the output.
 */
public final class JavaRandomDump {

    private static final long[] SEEDS = {0L, 1L, 42L, 2024L, -1L, 123456789L};
    private static final int[] INT_BOUNDS = {2, 3, 5, 6};
    private static final int COUNT = 1000;

    private JavaRandomDump() {
    }

    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");

        // "seeds": [...]
        sb.append("  \"seeds\": [");
        for (int i = 0; i < SEEDS.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(SEEDS[i]);
        }
        sb.append("],\n");

        // "vectors": [...]
        sb.append("  \"vectors\": [\n");
        boolean first = true;
        for (long seed : SEEDS) {
            // nextInt(bound) for each bound, fresh Random each time.
            for (int bound : INT_BOUNDS) {
                Random r = new Random(seed);
                if (!first) {
                    sb.append(",\n");
                }
                first = false;
                sb.append("    {\"seed\": ").append(seed)
                  .append(", \"method\": \"nextInt\", \"bound\": ").append(bound)
                  .append(", \"count\": ").append(COUNT)
                  .append(", \"values\": [");
                for (int i = 0; i < COUNT; i++) {
                    if (i > 0) {
                        sb.append(", ");
                    }
                    sb.append(r.nextInt(bound));
                }
                sb.append("]}");
            }
            // nextBoolean(), fresh Random, bound = null.
            Random rb = new Random(seed);
            if (!first) {
                sb.append(",\n");
            }
            first = false;
            sb.append("    {\"seed\": ").append(seed)
              .append(", \"method\": \"nextBoolean\", \"bound\": null")
              .append(", \"count\": ").append(COUNT)
              .append(", \"values\": [");
            for (int i = 0; i < COUNT; i++) {
                if (i > 0) {
                    sb.append(", ");
                }
                sb.append(rb.nextBoolean());
            }
            sb.append("]}");
        }
        sb.append("\n  ]\n");
        sb.append("}\n");

        System.out.print(sb);
    }
}
