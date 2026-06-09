import gov.sandia.cognition.generator.matrix.SGMCell;
import gov.sandia.cognition.generator.matrix.SGMLayer;
import gov.sandia.cognition.generator.matrix.SGMLayerGenerator;
import gov.sandia.cognition.generator.matrix.SGMMatrix;
import gov.sandia.cognition.generator.matrix.SGMMatrixSize;
import gov.sandia.cognition.generator.matrix.structure.SGMStructureFeature;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Headless golden-fixture emitter for SGMT matrices.
 *
 * Drives the deterministic core of SGMMatrixSetGenerator.generateMatrices WITHOUT
 * the SGMMatrixDifficultyClassifier: that classifier is only used to FILL a score
 * distribution (the outer accept/reject loop), and the upstream JUnit test loads
 * it from a serialized XML (SerializedMatrixSGMDifficultyClassifier.xml) that is
 * NOT shipped in the source distribution. The structure + surface + answer layout
 * of a single matrix is produced entirely by SGMLayerGenerator.generateLayer and
 * the SGMMatrix constructor, both of which take a seeded java.util.Random and
 * touch no classifier. So we replicate one generation iteration here, byte-faithful
 * to the upstream RNG-consumption order:
 *   numLayers           = random.nextInt(maxLayersPerMatrix) + 1
 *   correctAnswerPos    = random.nextInt(numAnswerChoices)
 *   layers              = generateLayer(...) x numLayers
 *   matrix              = new SGMMatrix(size, numAnswerChoices, pos, layers, random)
 * and, exactly like the upstream loop's `continue` guard, we re-run when the matrix
 * fails to produce enough answer choices.
 *
 * Output: one JSON object on stdout, hand-formatted for byte-stable regeneration
 * (fixed key order, two-space indent, LF newlines). Descriptions (relation, shape,
 * fill, direction) are read by reflection because getDescription() lives on the
 * concrete classes, not the SGMStructureFeature / SGMSurfaceFeature interfaces.
 *
 * Run with -Djava.awt.headless=true (surface features carry java.awt.Shape state).
 */
public final class SgmtDump {

    // Fixed config matrix: (maxLayers, maxStructFeatures, numAnswers) x one seed.
    private static final int[][] CONFIGS = {
        {1, 1, 8},
        {1, 2, 8},
        {2, 1, 8},
        {2, 2, 8},
        {3, 2, 8},
    };
    private static final long SEED = 42L;
    private static final int CELL_PIXEL_SIZE = 100;

    private SgmtDump() {
    }

    public static void main(String[] args) throws Exception {
        SGMMatrixSize size = new SGMMatrixSize(3, 3);
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"seed\": ").append(SEED).append(",\n");
        sb.append("  \"matrix_size\": {\"rows\": 3, \"cols\": 3},\n");
        sb.append("  \"cell_pixel_size\": ").append(CELL_PIXEL_SIZE).append(",\n");
        sb.append("  \"matrices\": [\n");
        boolean firstMatrix = true;
        for (int[] cfg : CONFIGS) {
            SGMMatrix matrix = generate(size, cfg[0], cfg[1], cfg[2]);
            if (!firstMatrix) {
                sb.append(",\n");
            }
            firstMatrix = false;
            appendMatrix(sb, cfg, matrix);
        }
        sb.append("\n  ]\n");
        sb.append("}\n");
        System.out.print(sb);
    }

    /** Replicate one deterministic generateMatrices iteration (no classifier). */
    private static SGMMatrix generate(
        SGMMatrixSize size, int maxLayers, int maxStruct, int numAnswers) {
        Random random = new Random(SEED);
        while (true) {
            int numLayers = random.nextInt(maxLayers) + 1;
            int correctAnswerPosition = random.nextInt(numAnswers);
            List<SGMLayer> layers = new ArrayList<SGMLayer>(numLayers);
            for (int i = 0; i < numLayers; i++) {
                layers.add(SGMLayerGenerator.generateLayer(
                    size, maxStruct, CELL_PIXEL_SIZE, random));
            }
            SGMMatrix matrix = new SGMMatrix(
                size, numAnswers, correctAnswerPosition, layers, random);
            if (matrix.getNumAnswerChoicesGenerated() < numAnswers) {
                continue;  // upstream `continue`: re-draw on the same stream.
            }
            return matrix;
        }
    }

    private static void appendMatrix(StringBuilder sb, int[] cfg, SGMMatrix m) {
        List<SGMLayer> layers = m.getSGMLayers();
        sb.append("    {\n");
        sb.append("      \"config\": {\"max_layers\": ").append(cfg[0])
          .append(", \"max_structure_features\": ").append(cfg[1])
          .append(", \"num_answer_choices\": ").append(cfg[2]).append("},\n");
        sb.append("      \"layer_count\": ").append(layers.size()).append(",\n");
        sb.append("      \"correct_answer_position\": ")
          .append(m.getCorrectAnswerPosition()).append(",\n");

        // structure: per layer, the relation + direction of each structure feature
        sb.append("      \"structure\": [");
        for (int li = 0; li < layers.size(); li++) {
            if (li > 0) {
                sb.append(", ");
            }
            sb.append("{\"layer\": ").append(li).append(", \"features\": [");
            List<SGMStructureFeature> feats = layers.get(li).getStructureFeatures();
            for (int fi = 0; fi < feats.size(); fi++) {
                if (fi > 0) {
                    sb.append(", ");
                }
                SGMStructureFeature f = feats.get(fi);
                String relation = desc(f);
                String direction = desc(f.getLocationTransform());
                sb.append("{\"relation\": ").append(jsonStr(relation))
                  .append(", \"direction\": ").append(jsonStr(direction))
                  .append("}");
            }
            sb.append("]}");
        }
        sb.append("],\n");

        // cells: the 3x3 composited grid, each with its surface features
        SGMCell[][] cells = m.getSGMCells();
        sb.append("      \"cells\": [");
        boolean firstCell = true;
        for (int r = 0; r < cells.length; r++) {
            for (int c = 0; c < cells[r].length; c++) {
                if (!firstCell) {
                    sb.append(", ");
                }
                firstCell = false;
                appendCell(sb, r, c, cells[r][c]);
            }
        }
        sb.append("],\n");

        // answer_choices: the distractors + correct answer, in slot order
        List<SGMCell> answers = m.getAnswerChoices();
        sb.append("      \"answer_choices\": [");
        for (int ai = 0; ai < answers.size(); ai++) {
            if (ai > 0) {
                sb.append(", ");
            }
            appendAnswer(sb, ai, answers.get(ai));
        }
        sb.append("]\n");
        sb.append("    }");
    }

    private static void appendCell(StringBuilder sb, int r, int c, SGMCell cell) {
        sb.append("{\"row\": ").append(r).append(", \"col\": ").append(c)
          .append(", \"surface_features\": [");
        List<SGMSurfaceFeature> sfs = cell.getSurfaceFeatures();
        for (int i = 0; i < sfs.size(); i++) {
            if (i > 0) {
                sb.append(", ");
            }
            appendSurface(sb, sfs.get(i));
        }
        sb.append("]}");
    }

    private static void appendAnswer(StringBuilder sb, int slot, SGMCell cell) {
        sb.append("{\"slot\": ").append(slot);
        if (cell == null) {
            sb.append(", \"surface_features\": null}");
            return;
        }
        sb.append(", \"surface_features\": [");
        List<SGMSurfaceFeature> sfs = cell.getSurfaceFeatures();
        for (int i = 0; i < sfs.size(); i++) {
            if (i > 0) {
                sb.append(", ");
            }
            appendSurface(sb, sfs.get(i));
        }
        sb.append("]}");
    }

    private static void appendSurface(StringBuilder sb, SGMSurfaceFeature sf) {
        sb.append("{\"shape\": ").append(jsonStr(desc(sf)))
          .append(", \"fill\": ").append(jsonStr(sf.getFillPattern().getDescription()))
          .append(", \"scale\": ").append(num(sf.getScale()))
          .append(", \"rotation\": ").append(sf.getRotation())
          .append(", \"x\": ").append(num(sf.getPosition().getX()))
          .append(", \"y\": ").append(num(sf.getPosition().getY()))
          .append("}");
    }

    /** getDescription() via reflection (not on the interfaces). */
    private static String desc(Object o) {
        try {
            return (String) o.getClass().getMethod("getDescription").invoke(o);
        } catch (Exception e) {
            return o.getClass().getSimpleName();
        }
    }

    /** Render a double with no locale variance and integers without a .0 tail. */
    private static String num(double v) {
        if (v == Math.floor(v) && !Double.isInfinite(v)) {
            return Long.toString((long) v);
        }
        return Double.toString(v);
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
