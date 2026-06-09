/*
 * File:                SGMMatrixSetGenerator.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 21, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMMatrixSetGenerator.java,v $
 * Revision 1.3  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:05  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:04  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:33  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:23  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.16  2010/06/30 14:18:31  cewarr
 * Changed to use new DefaultInputOutputPair to match Foundry API change
 *
 * Revision 1.15  2008/03/25 16:04:30  zobenz
 * Cleaned up model settings - All model settings now stored in AnalogyModelSettings.java; added a RasterSettings.java to store just the image rasterization settings for SGM generation and rasterization
 *
 * Revision 1.14  2008/03/03 22:03:09  zobenz
 * Made matrix generation settings serializable as part of SGMMatrixSetGenerator
 *
 * Revision 1.13  2008/01/25 22:30:20  zobenz
 * SGMScore now determined during generation of set of SGM matrices using a provided difficulty classifer
 *
 * Revision 1.12  2008/01/07 21:11:17  zobenz
 * Tested xml serialization of generated set of matrices
 *
 * Revision 1.11  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.10  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.9  2007/12/10 20:01:52  zobenz
 * Moved SGMLayer generation to its own class
 *
 * Revision 1.8  2007/12/10 19:56:04  zobenz
 * Filled in rest of answer choice generation by randomly manipulating parameters of surface features
 *
 * Revision 1.7  2007/12/07 00:00:52  zobenz
 * Removed some debug statements; disabled rotate structure feature again for the time being
 *
 * Revision 1.6  2007/12/06 23:28:33  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.5  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 * Revision 1.4  2007/12/03 23:09:21  zobenz
 * Initial implementation of a complete top to bottom stochastic generation of SGMs
 *
 * Revision 1.3  2007/11/30 23:10:57  zobenz
 * Work in progress on stochastic SGM generation
 *
 * Revision 1.2  2007/11/30 16:27:52  zobenz
 * Implemented missing hashCode functions; Implemented SGMScore and SGMScoreDistribution
 *
 * Revision 1.1  2007/11/21 22:28:30  zobenz
 * Implemented SGMMatrix, which is composed of layers; starting work on stochastic generation of SGMs to fit a specified score distribution
 *
 */
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.RasterSettings;
import gov.sandia.cognition.learning.data.DefaultInputOutputPair;
import gov.sandia.cognition.learning.data.InputOutputPair;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMMatrixSetGenerator
    implements Serializable
{
    private SGMScoreDistribution sgmScoreDistribution;
    private SGMMatrixSize sgmMatrixSize;
    private int maxLayersPerMatrix;
    private int maxStructureFeaturesPerLayer;    
    private int numAnswerChoices;
    private SGMMatrixDifficultyClassifier difficultyClassifier;
    private long seed;
    
    public SGMMatrixSetGenerator(
        final SGMScoreDistribution sgmScoreDistribution,
        final SGMMatrixSize sgmMatrixSize,
        final int maxLayersPerMatrix,
        final int maxStructureFeaturesPerLayer,        
        final int numAnswerChoices,
        final SGMMatrixDifficultyClassifier difficultyClassifier,
        final long seed)
    {            
        this.setSGMScoreDistribution(sgmScoreDistribution);
        this.setSGMMatrixSize(sgmMatrixSize);
        this.setMaxLayersPerMatrix(maxLayersPerMatrix);
        this.setMaxStructureFeaturesPerLayer(maxStructureFeaturesPerLayer);
        this.setNumAnswerChoices(numAnswerChoices);
        this.setDifficultyClassifier(difficultyClassifier);        
        this.setSeed(seed);        
    }
    
    public ArrayList<InputOutputPair<SGMMatrix, SGMScore>>
        generateMatrices(
        final RasterSettings rasterSettings)
    {
        ArrayList<InputOutputPair<SGMMatrix, SGMScore>> matrices =
            new ArrayList<InputOutputPair<SGMMatrix, SGMScore>>();
        Random random = new Random(getSeed());

        boolean done = false;
        while (!done)
        {                       
            // Stochastically determine number of layers
            int numLayers = random.nextInt(getMaxLayersPerMatrix()) + 1;
            ArrayList<SGMLayer> sgmLayers =
                new ArrayList<SGMLayer>(numLayers);

            // Stochastically decide the position for the correct answer
            // in the collection of answer choices
            int correctAnswerPosition = random.nextInt(getNumAnswerChoices());

            // Create each layer 
            for (int currentLayer = 0; currentLayer < numLayers; currentLayer++)
            {                
                // Create and store the layer
                sgmLayers.add(SGMLayerGenerator.generateLayer(
                    getSGMMatrixSize(),
                    this.getMaxStructureFeaturesPerLayer(),
                    rasterSettings.getSGMCellRasterImagePixelSize(),
                    random));
            }

            // Collect the layers into a matrix
            SGMMatrix matrix =
                new SGMMatrix(getSGMMatrixSize(),
                this.getNumAnswerChoices(),  correctAnswerPosition,
                
                sgmLayers, random);
            
            // Make sure enough answer choices were generated
            if (matrix.getNumAnswerChoicesGenerated() < getNumAnswerChoices())
            {
                continue;
            }

            // See if the generated matrix fulfills a need in our requested
            // sgmScoreDistribution
            SGMScore score = getDifficultyClassifier().evaluate(matrix);
            if (getSGMScoreDistribution().addSGMScore(score))
            {
                // Matrix fulfills a need in distribution, so keep it
                matrices.add(new DefaultInputOutputPair<SGMMatrix,
                    SGMScore>(matrix, score));

                // Check to see if we've completely satisfied the
                // requested score distribution
                done = getSGMScoreDistribution().distributionAchieved();
            }
        }
        return matrices;
    }

    public SGMScoreDistribution getSGMScoreDistribution()
    {
        return sgmScoreDistribution;
    }

    private void setSGMScoreDistribution(
        final SGMScoreDistribution sgmScoreDistribution)
    {
        this.sgmScoreDistribution = sgmScoreDistribution;
    }

    public SGMMatrixSize getSGMMatrixSize()
    {
        return sgmMatrixSize;
    }

    private void setSGMMatrixSize(
        final SGMMatrixSize sgmMatrixSize)
    {
        this.sgmMatrixSize = sgmMatrixSize;
    }

    public int getMaxLayersPerMatrix()
    {
        return maxLayersPerMatrix;
    }

    private void setMaxLayersPerMatrix(
        final int maxLayersPerMatrix)
    {
        this.maxLayersPerMatrix = maxLayersPerMatrix;
    }

    public int getMaxStructureFeaturesPerLayer()
    {
        return maxStructureFeaturesPerLayer;
    }

    private void setMaxStructureFeaturesPerLayer(
        final int maxStructureFeaturesPerLayer)
    {
        this.maxStructureFeaturesPerLayer = maxStructureFeaturesPerLayer;
    }

    public int getNumAnswerChoices()
    {
        return numAnswerChoices;
    }

    private void setNumAnswerChoices(
        final int numAnswerChoices)
    {
        this.numAnswerChoices = numAnswerChoices;
    }

    public SGMMatrixDifficultyClassifier getDifficultyClassifier()
    {
        return difficultyClassifier;
    }

    private void setDifficultyClassifier(
        final SGMMatrixDifficultyClassifier difficultyClassifier)
    {
        this.difficultyClassifier = difficultyClassifier;
    }

    public long getSeed()
    {
        return seed;
    }

    private void setSeed(long seed)
    {
        this.seed = seed;
    }
}
