/*
 * File:                SGMMatrix.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 1, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMMatrix.java,v $
 * Revision 1.1  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:06  zobenz
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
 * Revision 1.25  2008/11/05 18:24:26  cewarr
 * Tweaked the grey fill patterns, added two shapes, eliminated squares/circles and repeat use of same shape in a matrix, fixed some problems with wrong answers when numerosity is used.
 *
 * Revision 1.24  2008/01/25 21:16:15  zobenz
 * Added infrastructure and method for evaluating SGMScore of a matrix given a SGMMatrixDifficulty Classifier
 *
 * Revision 1.23  2007/12/13 20:57:09  zobenz
 * Finished filling in some documentation that was marked TODO; as an aside, the code currently has a bug if you set max structure features per layer> 1
 *
 * Revision 1.22  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.21  2007/12/11 17:35:32  zobenz
 * Improved numerosity to use consistent scaling and positioning across cells along location transform
 *
 * Revision 1.20  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.19  2007/12/10 21:59:05  zobenz
 * Cleaned up surface feature generation to improve visual layout
 *
 * Revision 1.18  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.17  2007/12/10 19:56:04  zobenz
 * Filled in rest of answer choice generation by randomly manipulating parameters of surface features
 *
 * Revision 1.16  2007/12/10 18:28:38  zobenz
 * Added "explain" feature to textually describe how a matrix was constructed
 *
 * Revision 1.15  2007/12/10 15:43:29  zobenz
 * Fixed padding out of wrong answers with blanks to make sure correct answer is in contiguous block with non blank wrong answers
 *
 * Revision 1.14  2007/12/07 00:30:47  zobenz
 * Padding answer choices with blanks if needed until finish working on answer choice generation
 *
 * Revision 1.13  2007/12/06 23:28:33  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.12  2007/12/06 19:04:41  zobenz
 * Committing working implementation in preparation for overhauling way in which structure features are applied
 *
 * Revision 1.11  2007/12/05 20:44:55  zobenz
 * Improved answer choice generation; Replaced SetIteration structure feature with Identity structure feature; added Rotate structure feature (which has a bug right now)
 *
 * Revision 1.10  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 * Revision 1.9  2007/11/30 23:10:58  zobenz
 * Work in progress on stochastic SGM generation
 *
 * Revision 1.8  2007/11/21 22:52:45  zobenz
 * Implemented SGMMatrix, which is composed of layers; starting work on stochastic generation of SGMs to fit a specified score distribution
 *
 * Revision 1.7  2007/11/21 22:28:30  zobenz
 * Implemented SGMMatrix, which is composed of layers; starting work on stochastic generation of SGMs to fit a specified score distribution
 *
 * Revision 1.6  2007/11/20 23:47:34  zobenz
 * Working on SGMLayer - specifically on creation of a layer from provided surface features, structure features, and location transform; it's not done yet.  Should have it finished tomorrow.
 *
 * Revision 1.5  2007/11/19 23:41:55  zobenz
 * Working implementation of SetIterationSGMFeature
 *
 * Revision 1.4  2007/11/13 22:58:55  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.3  2007/11/12 23:20:39  zobenz
 * Working on being able to render matrices to screen and to bitmap
 *
 * Revision 1.2  2007/11/07 16:47:46  zobenz
 * Interim checkin; working on implementing SGM generation code.
 *
 * Revision 1.1  2007/11/01 22:57:55  zobenz
 * Initial stubs
 *
 */
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPatternGenerator;
import gov.sandia.cognition.generator.matrix.structure.SGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.supplemental.TranslationalNumerositySGMStructureFeature;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import gov.sandia.cognition.util.CloneableSerializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMMatrix extends AbstractSGMMatrix
{
    private List<SGMCell> answerChoices;
    private int correctAnswerPosition;
    private int numAnswerChoicesGenerated;
    private List<SGMLayer> sgmLayers;
    private Map<WrongAnswerType, Integer> wrongAnswerTypeCounts;
    public static final int MAX_DUPLICATES_IN_A_ROW = 500;  
    
    public enum WrongAnswerType
    {
        INCORRECT_CELL_FROM_MATRIX,
        MODIFIED_INCORRECT_CELL_FROM_MATRIX,
        MODIFIED_CORRECT_ANSWER,
        MODIFIED_WRONG_ANSWER,
        MATRIX_SURFACE_FEATURE_COMBINATION,
        NOVEL_SURFACE_FEATURE;        
    }

    public SGMMatrix(
        final SGMMatrixSize sgmMatrixSize,
        final int numAnswerChoices,
        final int correctAnswerPosition,
        final List<SGMLayer> sgmLayers,
        final Random random)
    {
        // Sanity check on correct answer position
        if (correctAnswerPosition >= numAnswerChoices)
        {
            throw new IllegalArgumentException("correctAnswerPosition" +
                " (" + correctAnswerPosition + ") must be strictly less than " +
                "numAnswerChoices (" + numAnswerChoices + ")");
        }

        // Sanity check on the sgmMatrixSize, numAnswerChoices, and
        // correctAnswerPosition of each layer
        for (SGMLayer layer : sgmLayers)
        {
            if (!layer.getSGMMatrixSize().equals(layer.getSGMMatrixSize()))
            {
                throw new SGMMatrixSizeMismatchException(
                    "Layers must have the same dimensions as the matrix: " +
                    "(" + this.getSGMMatrixSize().getNumRows() +
                    "x" + this.getSGMMatrixSize().getNumColumns() + ") !=" +
                    "(" + layer.getSGMMatrixSize().getNumRows() +
                    "x" + layer.getSGMMatrixSize().getNumColumns() + ")");
            }
        }

        // Store settings
        this.setSGMMatrixSize(sgmMatrixSize);
        this.setAnswerChoices(new ArrayList<SGMCell>(numAnswerChoices));
        this.setCorrectAnswerPosition(correctAnswerPosition);
        this.setSGMLayers(sgmLayers);

        // Construct cell storage
        this.setSGMCells(
            new SGMCell[this.getSGMMatrixSize().getNumRows()][this.getSGMMatrixSize().getNumColumns()]);

        // Construct storage for wrong answer type counts
        this.setWrongAnswerTypeCounts(new HashMap<WrongAnswerType, Integer>());
        
        // Composite the layers to create the cells for the overall matrix                
        for (int row = 0; row < this.getSGMMatrixSize().getNumRows(); row++)
        {
            for (int col = 0; col < this.getSGMMatrixSize().getNumColumns();
                col++)
            {
                List<SGMSurfaceFeature> surfaceFeatures =
                    new ArrayList<SGMSurfaceFeature>();

                SGMCompositeCell currentCell = null;
                int i = 0;
                for (SGMLayer layer : this.getSGMLayers())
                {
                    // First layer, so grab its cell so we can composite 
                    // onto it
                    if (i == 0)
                    {
                        currentCell = new SGMCompositeCell(
                            layer.getSGMCells()[row][col]);
                    }
                    else
                    {
                        currentCell = currentCell.combineWith(
                            layer.getSGMCells()[row][col]);
                    }

                    i++;
                }

                this.getSGMCells()[row][col] = currentCell;
            }
        }
        
        // Pad out wrong answer choice storage with nulls to get us started
        for (int i = 0; i < numAnswerChoices; i++)
        {
            this.getAnswerChoices().add(null);
        }
        int positionInAnswerChoices = 0;
        if (positionInAnswerChoices == correctAnswerPosition)
        {
            positionInAnswerChoices++;
        }
        
        // Put correct answer into its position
        int correctAnswerRow = this.getSGMMatrixSize().getNumRows() - 1;
        int correctAnswerColumn = this.getSGMMatrixSize().getNumColumns() - 1;
        SGMCell correctAnswer =
            this.getSGMCells()[correctAnswerRow][correctAnswerColumn];
        this.getAnswerChoices().set(correctAnswerPosition,
            this.getSGMCells()[correctAnswerRow][correctAnswerColumn]);
        this.setNumAnswerChoicesGenerated(1); // Correct answer counts for 1

        // Generate wrong answers using first strategy - variations on
        // things seen in the matrix
        int numDuplicatesInARow = 0;
        while ((positionInAnswerChoices < numAnswerChoices)
            && (numDuplicatesInARow < MAX_DUPLICATES_IN_A_ROW))
        {                   
            SGMCompositeCell answerChoice = null;
            WrongAnswerType answerType = null;
            int type;
            // Exclude case 0 if there aren't enough layers to use it
            if (this.getSGMLayers().size() > 1)
            {
                type = random.nextInt(4);
            }
            else
            {
                type = random.nextInt(3) + 1;
            }            
            switch (type)
            {
                case 0:
                    // Generate a wrong answer as a subset of layers
                    // from the correct answer
                    List<Integer> layersSubSet = this.generateRandomLayerSubSet(
                        this.getSGMLayers().size(), random);
                    for (int index = 0; index < layersSubSet.size(); index++)
                    {
                        int currentLayer = layersSubSet.get(index);
                        if (index == 0)
                        {
                            // First layer, so grab its cell so we can composite
                            // onto it
                            answerChoice = new SGMCompositeCell(
                                this.getSGMLayers().get(currentLayer).
                                getSGMCells()[correctAnswerRow]
                                [correctAnswerColumn]);
                        }
                        else
                        {
                            answerChoice = answerChoice.combineWith(
                                this.getSGMLayers().get(currentLayer).
                                getSGMCells()[correctAnswerRow]
                                [correctAnswerColumn]);
                        }
                    }
                    answerType = 
                        WrongAnswerType.MATRIX_SURFACE_FEATURE_COMBINATION;

                    break;
                case 1:
                    // Generate a wrong answer as one of the cells in
                    // in the matrix other than the correct answer
                    int row = correctAnswerRow;
                    int column = correctAnswerColumn;
                    while ((row == correctAnswerRow) && 
                        (column == correctAnswerColumn))
                    {
                        row = random.nextInt(this.getSGMMatrixSize().
                            getNumRows());
                        column = random.nextInt(this.getSGMMatrixSize().
                            getNumColumns());
                    }
                    answerChoice = new SGMCompositeCell(
                        this.getSGMCells()[row][column]);
                    answerType = WrongAnswerType.INCORRECT_CELL_FROM_MATRIX;
                    
                    break;                
                case 2:
                    // Apply a random parameter change to a random cell
                    // from the matrix
                    
                    // First, choose a random layer, and test whether that
                    // layer uses numerosity.  If so, change all surface features
                    // in that layer the same way.
                    
                    int layerID = random.nextInt(this.getSGMLayers().size());
                    SGMLayer layer = this.getSGMLayers().get(layerID);
                    boolean numerosityLayer = false;
                    List<SGMStructureFeature> structures =
                        layer.getStructureFeatures();
                    for (int i = 0; i<structures.size(); i++)
                    {
                        if (structures.get(i).getDescription().equals( 
                                TranslationalNumerositySGMStructureFeature.
                                DESCRIPTION))
                            numerosityLayer = true;
                    }
                    
                    // Stochastically pick cell to modify (break if
                    // no surface features at chosen cell)
                    row = random.nextInt(this.getSGMMatrixSize().
                            getNumRows());
                    column = random.nextInt(this.getSGMMatrixSize().
                            getNumColumns());
                    if (layer.getSGMCells()[row][column].
                        getSurfaceFeatures().size() > 0)
                    {                                            
                        answerChoice = new SGMCompositeCell(
                            layer.getSGMCells()[row][column]);
                        
                        List<SGMSurfaceFeature> features =
                            answerChoice.getSurfaceFeatures();
 
                        // Stochastically pick which parameter of the feature
                        // to modify
                        int parameterToChange = random.nextInt(2);

                        if (numerosityLayer)
                        {
                            // change all features the same way
                            switch (parameterToChange)
                            {
                                case 0:
                                    // Modify the fill pattern
                                    SGMFillPattern fill = SGMFillPatternGenerator.
                                            generateFillPattern(random);
                                    for (int i=0; i<features.size(); i++)
                                    {
                                        SGMSurfaceFeature feature =
                                            features.get(i).clone();
                                        features.set(i, feature);
                                        feature.setFillPattern(fill);
                                    }
                                    break;
                                case 1:
                                    // Modify the scale (0.66)
                                    double newScale = 0.66;
                                    for (int i=0; i<features.size(); i++)
                                    {
                                        SGMSurfaceFeature feature =
                                            features.get(i).clone();
                                        features.set(i, feature);
                                        feature.setScale(newScale);
                                    }
                                    break;
                            }
                        }
                        else    // no numerosity
                        {
                            // Stochastically pick surface feature in cell to modify
                            int featureIndex = random.nextInt(
                                features.size());
                            SGMSurfaceFeature feature =
                                features.get(featureIndex).clone();

                            // After cloning surface feature so that we can
                            // manipulate its parameters without affecting other
                            // uses of the surface feature in matrix, need to put
                            // clone in our answerChoice's list of surface features
                            features.set(featureIndex, feature);

                            switch (parameterToChange)
                            {
                                case 0:
                                    // Modify the fill pattern
                                    feature.setFillPattern(SGMFillPatternGenerator.
                                        generateFillPattern(random));
                                    break;
                                case 1:
                                    // Modify the scale (0.66)
                                    double newScale = 0.66;
                                    feature.setScale(newScale);
                                    break;
                            }
                        }
                    }
                    answerType = 
                        WrongAnswerType.MODIFIED_INCORRECT_CELL_FROM_MATRIX;
                    
                    break;                                                                                                                                                                                                                                                
                case 3:
                    // Generate a wrong answer as a combination of random
                    // layers from across the matrix                    
                    // Stochastically choose numLayers to be between 1 and 
                    // number of layers in matrix (inclusive)
                    int matrixNumLayers = this.getSGMLayers().size();
                    int numLayers = 1;
                    if (matrixNumLayers > numLayers)
                    {
                        numLayers = random.nextInt(matrixNumLayers) + 1;
                    }

                    // Stochastically determine which layers to use
                    List<Integer> layers = 
                        new ArrayList<Integer>(numLayers);
                    while (layers.size() < numLayers)
                    {
                        int potentialLayer = 
                            random.nextInt(matrixNumLayers);
                        if (!layers.contains(potentialLayer))
                        {
                            layers.add(potentialLayer);
                        }
                    }

                    // Grab random surface features layer by layer from
                    // a random cell in the matrix
                    List<SGMSurfaceFeature> surfaceFeatures =
                        new ArrayList<SGMSurfaceFeature>();
                    for (Integer currentLayer : layers)
                    {
                        row = random.nextInt(this.getSGMMatrixSize().
                            getNumRows());
                        column = random.nextInt(this.getSGMMatrixSize().
                            getNumColumns());

                        for (SGMSurfaceFeature currentFeature :
                            this.getSGMLayers().get(currentLayer).
                            getSGMCells()[row][column].
                            getSurfaceFeatures())
                        {
                            // Randomly decide if we want to use the
                            // current surface feature
                            if (random.nextBoolean())
                            {
// TODO - probably want to check to see if already have added the surface
// feature                                
                                surfaceFeatures.add(currentFeature);
                            }
                        }                            
                    }    

                    // Create cell from surface features (setting
                    // SGMLocation to null because location
                    // doesn't matter for answer choices)
                    answerChoice = new SGMCompositeCell(null,
                        surfaceFeatures);                             
                    answerType = 
                        WrongAnswerType.MATRIX_SURFACE_FEATURE_COMBINATION;
                    break;
            }
            
            // Check to see if we generated an answer choice or not
            if ((answerChoice == null) || 
                (answerChoice.getSurfaceFeatures().size() == 0))
            {
                continue;
            }

            // Store the wrong answer that was generated if we don't already
            // have it in our answer choices        
            if ((!answerChoice.equals(correctAnswer)) && 
                (!this.containsCheck(this.getAnswerChoices(), answerChoice)))
            {
                this.getAnswerChoices().set(positionInAnswerChoices,
                    answerChoice);
                this.setNumAnswerChoicesGenerated(
                    this.getNumAnswerChoicesGenerated() + 1);
                positionInAnswerChoices++;
                if (positionInAnswerChoices == correctAnswerPosition)
                {
                    positionInAnswerChoices++;
                }
                numDuplicatesInARow = 0;
                
                // Update wrong answer type counts
                int count = 0;
                if (this.getWrongAnswerTypeCounts().containsKey(answerType))
                {
                    count = this.getWrongAnswerTypeCounts().get(answerType);
                }
                count++;
                this.getWrongAnswerTypeCounts().put(answerType, count);
            }    
            else
            {
                numDuplicatesInARow++;
            }
        }
        
        // TODO - another strategy (especially applicable to single layer
        // matrices) is to misapply the structure feature(s) of the layer
        // - i.e. scale, rotate, repeat, etc. by incorrect amount.  Could
        // add functionality to structure features to have them generate
        // a randomly incorrect output  
        //
        // Also - multiple structure features in a layer - only apply
        // subset of the structure features to get wrong answer                    
        
        // Before padding out with blank answers, make sure correct
        // answer is somewhere within the non-blank wrong answers
        if (this.getCorrectAnswerPosition() > positionInAnswerChoices)
        {
            // Correct answer is not in a contiguous block with wrong
            // answers, so choose a new position
            int newPosition = 0;
            if (positionInAnswerChoices > 0)
            {
                newPosition = random.nextInt(positionInAnswerChoices);
            }
            
            // Move item currently at newPosition to end of contiguous block
            this.getAnswerChoices().set(positionInAnswerChoices, 
                this.getAnswerChoices().get(newPosition));
            
            // Now put correct answer at newPosition
            this.getAnswerChoices().set(newPosition,
                this.getSGMCells()[correctAnswerRow][correctAnswerColumn]);
            this.setCorrectAnswerPosition(newPosition);
            
            // Move on to next position
            positionInAnswerChoices++;
        }
        
        // Make sure we don't overwrite correct answer if it is located
        // at positionInAnswerChoices
        if (positionInAnswerChoices == this.getCorrectAnswerPosition())
        {
            positionInAnswerChoices++;
        }
        
        // Pad out to get enough answers by adding in blank answers
        while (positionInAnswerChoices < numAnswerChoices)            
        {
            SGMCell currentCell = new SGMBaseCell(null,
                new ArrayList<SGMSurfaceFeature>(0));
                        
            // Store the wrong answer that was generated if we don't already
            // have it in our answer choices
            this.getAnswerChoices().set(positionInAnswerChoices,
                currentCell);
            positionInAnswerChoices++;
        }
    }
    
    private boolean containsCheck(List<SGMCell> answerChoices,
        SGMCell answerChoice)
    {                        
        // Built-in List contains check is wrong thing to do here (which is 
        // why we don't do it) - don't want that it contains the same object
        // reference, but rather that there is some cell that
        // fundamentally _equals_ this cell in terms of its 
        // properties
        
        for (SGMCell answer : answerChoices)
        {
            if (answer == null)
            {
                continue;
            }
            if (answer.equals(answerChoice))
            {
                return true;
            }
        }
        return false;
    }

    private List<Integer> generateRandomLayerSubSet(
        final int numLayers,
        Random random)
    {
        List<Integer> layersNotYetUsed =
            new ArrayList<Integer>(this.getSGMLayers().size());
        for (int layer = 0; layer < this.getSGMLayers().size(); layer++)
        {
            layersNotYetUsed.add(layer);
        }

        int numLayersToCombine = numLayers;
        if (numLayers > 1)
        {
            numLayersToCombine = random.nextInt(numLayers - 1) + 1;
        }
        List<Integer> layersSubSet = new ArrayList<Integer>(numLayersToCombine);
        for (int layer = 0; layer < numLayersToCombine; layer++)
        {
            // Randomly pick one of the layers from among those not
            // yet used
            int indexToUse = random.nextInt(layersNotYetUsed.size());
            layersSubSet.add(layersNotYetUsed.get(indexToUse));

            // Mark layer used by removing it from layersNotYetUsed
            layersNotYetUsed.remove(indexToUse);
        }

        return layersSubSet;
    }

    public List<SGMCell> getAnswerChoices()
    {
        return this.answerChoices;
    }

    protected void setAnswerChoices(
        final List<SGMCell> answerChoices)
    {
        this.answerChoices = answerChoices;
    }

    public int getCorrectAnswerPosition()
    {
        return this.correctAnswerPosition;
    }

    protected void setCorrectAnswerPosition(
        final int correctAnswerPosition)
    {
        this.correctAnswerPosition = correctAnswerPosition;
    }

    public List<SGMLayer> getSGMLayers()
    {
        return sgmLayers;
    }

    private void setSGMLayers(List<SGMLayer> sgmLayers)
    {
        this.sgmLayers = sgmLayers;
    }

    public CloneableSerializable clone()
    {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    public int getNumAnswerChoicesGenerated()
    {
        return numAnswerChoicesGenerated;
    }

    private void setNumAnswerChoicesGenerated(
        final int numAnswerChoicesGenerated)
    {
        this.numAnswerChoicesGenerated = numAnswerChoicesGenerated;
    }
    
    public Map<WrongAnswerType, Integer> getWrongAnswerTypeCounts()
    {
        return wrongAnswerTypeCounts;
    }

    private void setWrongAnswerTypeCounts(
        final Map<WrongAnswerType, Integer> wrongAnswerTypeCounts)
    {
        this.wrongAnswerTypeCounts = wrongAnswerTypeCounts;
    }
}
