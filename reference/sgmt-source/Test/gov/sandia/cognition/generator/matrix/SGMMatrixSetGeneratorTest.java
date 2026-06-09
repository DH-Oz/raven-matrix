/*
 * File:                SGMMatrixSetGeneratorTest.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Jan 7, 2008, Sandia Corporation.  Under the terms of Contract 
 * DE-AC04-94AL85000, there is a non-exclusive license for use of this work by 
 * or on behalf of the U.S. Government. Export of this program may require a 
 * license from the United States Government. See CopyrightHistory.txt for
 * complete details.
 * 
 * Reviewers:
 * Review Date:
 * Changes Needed:
 * Review Comments:
 * 
 * Revision History:
 * 
 * $Log: SGMMatrixSetGeneratorTest.java,v $
 * Revision 1.3  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
 * Revision 1.2  2010/12/21 16:10:58  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:08  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:05  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:39  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:29  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.7  2008/03/25 16:04:30  zobenz
 * Cleaned up model settings - All model settings now stored in AnalogyModelSettings.java; added a RasterSettings.java to store just the image rasterization settings for SGM generation and rasterization
 *
 * Revision 1.6  2008/03/13 15:55:08  zobenz
 * Made scorer for output vectors from local networks be a analogy model level setting, instead of individually creating a scorer in each and every output vector cogxel
 *
 * Revision 1.5  2008/03/03 22:03:09  zobenz
 * Made matrix generation settings serializable as part of SGMMatrixSetGenerator
 *
 * Revision 1.4  2008/01/25 22:30:19  zobenz
 * SGMScore now determined during generation of set of SGM matrices using a provided difficulty classifer
 *
 * Revision 1.3  2008/01/16 17:55:46  zobenz
 * Implemented code for Layer, including FuzzyArtBasedLayer implementation
 *
 * Revision 1.2  2008/01/09 19:22:21  zobenz
 * Added mechanism for implementing concurrent cognitive models (ConcurrentCognitiveModel interface), one implementation of which is a MultithreadedCognitiveModel
 *
 * Revision 1.1  2008/01/07 21:11:16  zobenz
 * Tested xml serialization of generated set of matrices
 *
 */
 
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.io.XStreamSerializationHandler;
import gov.sandia.cognition.learning.data.InputOutputPair;
import gov.sandia.cognition.statistics.distribution.DataCountTreeSetBinnedMapHistogram;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import junit.framework.TestCase;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMMatrixSetGeneratorTest extends TestCase {
    
    public SGMMatrixSetGeneratorTest(String testName) {
        super(testName);
    }            

    @Override
    protected void setUp() throws Exception {
        super.setUp();
    }

    @Override
    protected void tearDown() throws Exception {
        super.tearDown();
    }

    /**
     * Test of generateMatrices method, of class SGMMatrixSetGenerator.
     */
    public void testGenerateMatrices()
    {
        System.out.println("generateMatrices");
        
        long seed = 42;
        int maxLayersPerMatrix = 1;
        int maxStructureFeaturesPerLayer = 2;
        int numAnswerChoices = 8;
        int sgmCellImagePixelSize = 100;
        
        SGMScore bin = new SGMScore(Double.MIN_VALUE);

        DataCountTreeSetBinnedMapHistogram<SGMScore> bins =
            new DataCountTreeSetBinnedMapHistogram<SGMScore>(
            bin, new SGMScore(Double.MAX_VALUE));

        Map<SGMScore, Integer> binSizeLimits =
            new HashMap<SGMScore, Integer>(1);
        binSizeLimits.put(bin, 100);

        SGMScoreDistribution scoreDistribution =
            new SGMScoreDistribution(bins, binSizeLimits);
        
        SGMMatrixSize sgmMatrixSize = new SGMMatrixSize(3, 3);
        
        SGMMatrixDifficultyClassifier difficultyClassifier = null;
        try
        {
            difficultyClassifier = 
                (SGMMatrixDifficultyClassifier)XStreamSerializationHandler.
                readFromFile("SerializedMatrixSGMDifficultyClassifier.xml");
        }
        catch (Exception e)
        {
            fail(e.toString());            
        }
                
        SGMMatrixSetGenerator matrixGenerator = new SGMMatrixSetGenerator(
            scoreDistribution, sgmMatrixSize, maxLayersPerMatrix,
            maxStructureFeaturesPerLayer, numAnswerChoices, 
            difficultyClassifier, seed);
                        
        ArrayList<InputOutputPair<SGMMatrix, SGMScore>> matrices =
            matrixGenerator.generateMatrices(new RasterSettings(
            1000, 1000, sgmCellImagePixelSize, 2));

        // Test serialization
        try
        {
            FileWriter fileWriter = 
                new FileWriter("SGMMatrixSetGeneratorTest.xml", false);
            XStreamSerializationHandler.write(fileWriter, matrices);
            ArrayList deserializedMatrices = 
                (ArrayList)XStreamSerializationHandler.
                readFromFile("SGMMatrixSetGeneratorTest.xml");
            assertEquals(matrices.size(), deserializedMatrices.size());
        }
        catch (Exception e)
        {
            fail(e.toString());            
        }
        
        // Print out scores for generated matrices
        for (InputOutputPair<SGMMatrix, SGMScore> pair : matrices)
        {
            System.out.println(pair.getOutput().getScore());
        }
    }

}
