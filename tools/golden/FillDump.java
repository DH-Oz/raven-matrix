import gov.sandia.cognition.generator.matrix.fillpattern.BlackSGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.Grey10SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.Grey40SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.Grey75SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.WhiteSGMFillPattern;
import java.awt.Color;
import java.awt.Paint;

/**
 * Golden-fixture emitter for the five SGMT fill patterns.
 *
 * Anchors the upstream fill quirks that no seed-42 SgmtDump matrix happened to
 * draw, so the Python port's Fill enum (Phase 2) has a JVM-authoritative anchor:
 *   - Grey10 and Grey40 BOTH report getDescription() == "Red" (a real upstream
 *     quirk, not a typo on our side).
 *   - White is fully transparent (alpha 0).
 *   - every fill's exact 8-bit RGBA, as java.awt.Color rounds the float channels.
 *
 * Built against the SGMT jar (the fillpattern classes live there). FillDump only
 * instantiates the five concrete fills and reads their description + the RGBA of
 * getPaint() (which is a java.awt.Color); it needs no generator, no RNG, no Swing.
 * Run headless for consistency with the other emitters.
 *
 * Output: one JSON object on stdout in the canonical fill order
 * [White, Grey10, Grey40, Grey75, Black], hand-formatted for byte-stable
 * regeneration (fixed key order, two-space indent, LF newlines, no trailing
 * whitespace). Parseable by Python's stdlib json.
 */
public final class FillDump {

    private FillDump() {
    }

    public static void main(String[] args) {
        // Canonical order: White, Grey10, Grey40, Grey75, Black.
        SGMFillPattern[] fills = {
            new WhiteSGMFillPattern(),
            new Grey10SGMFillPattern(),
            new Grey40SGMFillPattern(),
            new Grey75SGMFillPattern(),
            new BlackSGMFillPattern(),
        };

        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"fills\": [\n");
        for (int i = 0; i < fills.length; i++) {
            SGMFillPattern fill = fills[i];
            Paint paint = fill.getPaint();
            Color color = (Color) paint;  // every SGMT fill wraps a java.awt.Color
            if (i > 0) {
                sb.append(",\n");
            }
            sb.append("    {\"class\": ")
              .append(jsonStr(fill.getClass().getSimpleName()))
              .append(", \"description\": ").append(jsonStr(fill.getDescription()))
              .append(", \"rgba\": [").append(color.getRed())
              .append(", ").append(color.getGreen())
              .append(", ").append(color.getBlue())
              .append(", ").append(color.getAlpha())
              .append("]}");
        }
        sb.append("\n  ]\n");
        sb.append("}\n");
        System.out.print(sb);
    }

    private static String jsonStr(String s) {
        StringBuilder out = new StringBuilder("\"");
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            switch (ch) {
                case '"': out.append("\\\""); break;
                case '\\': out.append("\\\\"); break;
                case '\n': out.append("\\n"); break;
                case '\r': out.append("\\r"); break;
                case '\t': out.append("\\t"); break;
                default: out.append(ch);
            }
        }
        return out.append("\"").toString();
    }
}
