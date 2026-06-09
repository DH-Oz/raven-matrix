/*
 * File:                SGMMatrixDifficultyClassifier.java
 * Authors:             Kevin R. Dixon
 * Company:             Sandia National Laboratories
 * Project:             Cognitive Foundry
 * 
 * Copyright Dec 17, 2007, Sandia Corporation.  Under the terms of Contract
 * DE-AC04-94AL85000, there is a non-exclusive license for use of this work by
 * or on behalf of the U.S. Government. Export of this program may require a
 * license from the United States Government. See CopyrightHistory.txt for
 * complete details.
 * 
 * Revision History:
 * 
 * $Log: SGMMatrixDifficultyClassifier.java,v $
 * Revision 1.3  2010/12/22 21:48:58  zobenz
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
 * Revision 1.1  2010/12/20 17:52:22  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.9  2010/06/30 21:15:29  cewarr
 * more changes to match Foundry changes
 *
 * Revision 1.8  2009/03/03 14:33:26  cewarr
 * Corrected code to output SGM categories corresponding to those used in norming study.
 *
 * Revision 1.7  2009/02/26 21:47:50  cewarr
 * Added code to output SGM categories corresponding to those used in norming study.
 *
 * Revision 1.6  2009/02/06 20:38:28  krdixon
 * Changes to accommodate statistics package rewrite
 *
 * Revision 1.5  2008/02/04 23:18:39  zobenz
 * Fixed bug in creating vector to score
 *
 * Revision 1.4  2008/02/04 22:56:16  zobenz
 * Made featureVector variable to aid in debugging
 *
 * Revision 1.3  2008/01/25 21:16:15  zobenz
 * Added infrastructure and method for evaluating SGMScore of a matrix given a SGMMatrixDifficulty Classifier
 *
 * Revision 1.2  2008/01/09 23:42:44  krdixon
 * Fully implemented, with unit test
 *
 * Revision 1.1  2007/12/18 20:15:47  krdixon
 * Initial Revision
 *
 */

package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.SGMMatrix.WrongAnswerType;
import gov.sandia.cognition.generator.matrix.locationtransform.DiagonalBottomLeftTopRightSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.DiagonalTopLeftBottomRightSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.HorizontalSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.LogicSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.TopLeftCornerOutSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.VerticalSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.structure.SGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.BaseSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.LogicalANDSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.LogicalORSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.LogicalXORSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.ShapeRepetitionSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.supplemental.ApplyRotationSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.supplemental.ApplyScalingSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.supplemental.ChangeFillPatternSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.supplemental.FillPatternRepetitionSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.supplemental.TranslationalNumerositySGMStructureFeature;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import gov.sandia.cognition.evaluator.Evaluator;
import gov.sandia.cognition.learning.algorithm.BatchLearner;
import gov.sandia.cognition.learning.data.DefaultInputOutputPair;
import gov.sandia.cognition.learning.data.InputOutputPair;
import gov.sandia.cognition.learning.experiment.LeaveOneOutFoldCreator;
import gov.sandia.cognition.learning.experiment.SupervisedLearnerValidationExperiment;
import gov.sandia.cognition.learning.performance.MeanAbsoluteErrorEvaluator;
import gov.sandia.cognition.math.matrix.Vector;
import gov.sandia.cognition.math.matrix.VectorFactory;
import gov.sandia.cognition.statistics.method.ConfidenceInterval;
import gov.sandia.cognition.statistics.method.StudentTConfidence;
import java.io.Serializable;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 *
 * @author Kevin R. Dixon
 */
public class SGMMatrixDifficultyClassifier
    implements Evaluator<Vector, Double>, Serializable
{

    private Evaluator<? super Vector, Double> scoreEstimator;

    /** 
     * Creates a new instance of SGMMatrixDifficultyClassifier
     */
    public SGMMatrixDifficultyClassifier(
        Evaluator<? super Vector, Double> scoreEstimator )
    {
        this.setScoreEstimator( scoreEstimator );
    }

    /**
     * Copy Constructor
     * @param other SGMMatrixDifficultyClassifier to copy
     */
    public SGMMatrixDifficultyClassifier(
        SGMMatrixDifficultyClassifier other )
    {
        this( other.getScoreEstimator() );
    }

    /**
     * {@inheritDoc}
     * @return {@inheritDoc}
     */
    @Override
    public SGMMatrixDifficultyClassifier clone()
    {
        return new SGMMatrixDifficultyClassifier( this );
    }

    public Evaluator<? super Vector, Double> getScoreEstimator()
    {
        return scoreEstimator;
    }

    public void setScoreEstimator(
        Evaluator<? super Vector, Double> scoreEstimator )
    {
        this.scoreEstimator = scoreEstimator;
    }

    public static SGMMatrixDifficultyClassifier create(
        Collection<DefaultInputOutputPair<Vector, Double>> inputTargetPairs,
        BatchLearner<Collection<? extends InputOutputPair<? extends Vector, Double>>, ? extends Evaluator<? super Vector, Double>> learner )
    {
        Evaluator<? super Vector, Double> scoreEstimator =
            learner.learn( inputTargetPairs );

        return new SGMMatrixDifficultyClassifier( scoreEstimator );
    }

    public static ConfidenceInterval testPerformance(
        Collection<DefaultInputOutputPair<Vector, Double>> inputTargetPairs,
        BatchLearner<Collection<? extends InputOutputPair<? extends Vector, Double>>, ? extends Evaluator<? super Vector, Double>> learner )
    {

        MeanAbsoluteErrorEvaluator<Vector> oneNorm =
            new MeanAbsoluteErrorEvaluator<Vector>();
        LeaveOneOutFoldCreator<InputOutputPair<Vector, Double>> jackknife =
            new LeaveOneOutFoldCreator<InputOutputPair<Vector, Double>>();

        final double confidence = 0.95;
        StudentTConfidence.Summary ttest =
            new StudentTConfidence.Summary( confidence );

        SupervisedLearnerValidationExperiment<Vector, Double, Double, ConfidenceInterval> experiment =
            new SupervisedLearnerValidationExperiment<Vector, Double, Double, ConfidenceInterval>(
            jackknife, oneNorm, ttest );

        return experiment.evaluatePerformance( learner, inputTargetPairs );

    }

    public Double evaluate(
        Vector input )
    {
        return this.getScoreEstimator().evaluate( input );
    }
    
    public SGMScore evaluate(
        SGMMatrix matrix)
    {                                      
        // Process layers of matrix to get counts for feature vector to be
        // scored
        Map<Class, Integer> baseStructureFeatureCounts = 
            new HashMap<Class, Integer>();
        Map<Class, Integer> supplementalStructureFeatureCounts = 
            new HashMap<Class, Integer>();
        Map<Class, Integer> locationTransformCounts = 
            new HashMap<Class, Integer>();
        Map<Class, Integer> surfaceFeatureComplexityCounts = 
            new HashMap<Class, Integer>();        
        Set<SGMSurfaceFeature> uniqueSurfaceFeatures =
            new HashSet<SGMSurfaceFeature>();
        
        // build up a string representing the image category/complexity
        StringBuilder sb = new StringBuilder(20);
        
        for (SGMLayer layer : matrix.getSGMLayers())
        {
            // Structure features
            for (SGMStructureFeature structureFeature :
                layer.getStructureFeatures())
            {
                // Count up structure features by type
                Class structureFeatureClass = structureFeature.getClass();
                if (structureFeature instanceof BaseSGMStructureFeature)
                {
                    // Base structure features                    
                    int count = 0;
                    if (baseStructureFeatureCounts.containsKey(
                        structureFeatureClass))
                    {
                        count = baseStructureFeatureCounts.get(
                            structureFeatureClass);                                                
                    }
                    count++;
                    baseStructureFeatureCounts.put(structureFeatureClass,
                        count);
                    
                    if (structureFeature instanceof ShapeRepetitionSGMStructureFeature)
                    {
                        sb.append('A');
                    }
                    else if (structureFeature instanceof LogicalORSGMStructureFeature)
                    {
                        sb.append('X');
                    }
                    else if (structureFeature instanceof LogicalANDSGMStructureFeature)
                    {
                        sb.append('Y');
                    }
                    else if (structureFeature instanceof LogicalXORSGMStructureFeature)
                    {
                        sb.append('Z');
                    }
                    else
                    {
                        sb.append('U');
                    }
                }
                else
                {
                    // Supplemental structure features                    
                    int count = 0;
                    if (supplementalStructureFeatureCounts.containsKey(
                        structureFeatureClass))
                    {
                        count = supplementalStructureFeatureCounts.get(
                            structureFeatureClass);                           
                    }
                    count++;
                    supplementalStructureFeatureCounts.put(structureFeatureClass,
                        count);
                    
                    if (structureFeature instanceof FillPatternRepetitionSGMStructureFeature)
                    {
                        sb.append('B');
                    }
                    else if (structureFeature instanceof ApplyRotationSGMStructureFeature)
                    {
                        sb.append('C');
                    }
                    else if (structureFeature instanceof ApplyScalingSGMStructureFeature)
                    {
                        sb.append('D');
                    }
                    else if (structureFeature instanceof TranslationalNumerositySGMStructureFeature)
                    {
                        sb.append('E');
                    }
                    else if (structureFeature instanceof ChangeFillPatternSGMStructureFeature)
                    {
                        sb.append('B');
                    }
                    else
                    {
                        sb.append('V');
                    }
                }
                
                // Count up location transforms by type
                SGMLocationTransform locationTransform =
                    structureFeature.getLocationTransform();
                Class locationTransformClass = locationTransform.getClass();
                int count = 0;
                if (locationTransformCounts.containsKey(locationTransformClass))
                {
                    count = locationTransformCounts.get(locationTransformClass);                    
                }
                count++;
                locationTransformCounts.put(locationTransformClass, count);  
                
                // label codes for transforms in norming study usually indicate
                // the direction in which the structure feature remains the SAME
                // (except for top-left-out transform, handled differently below)
                if (locationTransform instanceof HorizontalSGMLocationTransform)
                {
                    if (structureFeature instanceof ShapeRepetitionSGMStructureFeature ||
                        structureFeature instanceof FillPatternRepetitionSGMStructureFeature)
                    {
                        sb.append('1');
                    }
                    else
                    {
                        sb.append('2');
                    }
                }
                else if (locationTransform instanceof VerticalSGMLocationTransform)
                {
                    if (structureFeature instanceof ShapeRepetitionSGMStructureFeature ||
                        structureFeature instanceof FillPatternRepetitionSGMStructureFeature)
                    {
                        sb.append('2');
                    }
                    else
                    {
                        sb.append('1');
                    }
                }
                else if (locationTransform instanceof DiagonalBottomLeftTopRightSGMLocationTransform)
                {
                    if (structureFeature instanceof ShapeRepetitionSGMStructureFeature ||
                        structureFeature instanceof FillPatternRepetitionSGMStructureFeature)
                    {
                        sb.append('3');
                    }
                    else
                    {
                        sb.append('4');
                    }
                }
                else if (locationTransform instanceof DiagonalTopLeftBottomRightSGMLocationTransform)
                {
                    if (structureFeature instanceof ShapeRepetitionSGMStructureFeature ||
                        structureFeature instanceof FillPatternRepetitionSGMStructureFeature)
                    {
                        sb.append('4');
                    }
                    else
                    {
                        sb.append('3');
                    }
                }
                else if (locationTransform instanceof TopLeftCornerOutSGMLocationTransform)
                {
                    // in norming study, this transform was never used with fill pattern repetition,
                    // and was not part of label if used with shape repetition
                    // '5' indicates that feature CHANGES from top left corner out
                    // use '6' to indicate 'opposite' of '5', and flag that this is
                    // an SGM that may not correspond to a norming SGM
                    if (structureFeature instanceof ShapeRepetitionSGMStructureFeature ||
                        structureFeature instanceof FillPatternRepetitionSGMStructureFeature)
                    {
                        sb.append('6');
                    }
                    else
                    {
                        sb.append('5');
                    }
                }
                else if (locationTransform instanceof LogicSGMLocationTransform)
                {
                    // '7' isn't used in norming labels, but this makes assumed
                    // transform explicit, and distinct from some unknown transform
                    sb.append('7');
                }
                else 
                {
                    sb.append('0');
                }
            }
                
            sb.append('_');     // separate layers
                
            uniqueSurfaceFeatures.addAll(layer.getBaseSurfaceFeatures());
        }                  
        sb.deleteCharAt(sb.length()-1);   // remove final _
        
        // Count up surface features by type
        // TODO - for now we only have one surface feature complexity
        // implemented - simple geometric shapes - so just count up
        // total number of unique surface features; later will need to count
        // up by type
        Class surfaceFeatureClass = SGMSurfaceFeature.class;
        surfaceFeatureComplexityCounts.put(surfaceFeatureClass, 
            uniqueSurfaceFeatures.size());
        
        // Count up wrong answer types
        Map<Class, Integer> wrongAnswerTypeCounts = 
            new HashMap<Class, Integer>();
        
        // Push counts obtained from our walk across the layers into the
        // appropriate places in the featureScores vector
        // Convert the matrix to a feature vector for scoring
        double[] featureScores = new double[37];

        // # Cells in Matrix
        featureScores[0] = (matrix.getSGMMatrixSize().getNumRows() *
            matrix.getSGMMatrixSize().getNumColumns());
        
        // # Answer Choices
        featureScores[1] = (matrix.getAnswerChoices().size());
        
        // Base Structure Features
        featureScores[2] = 0; // Pattern Completion (not implemented yet)
        
        featureScores[3] = 0; // Shape Repetition
        if (baseStructureFeatureCounts.containsKey(
            ShapeRepetitionSGMStructureFeature.class))
        {
            featureScores[3] = baseStructureFeatureCounts.get(
                ShapeRepetitionSGMStructureFeature.class);
        }
        
        featureScores[4] = 0; // Mirror (not implemented yet)
        
        featureScores[5] = 0; // Logical OR
        if (baseStructureFeatureCounts.containsKey(
            LogicalORSGMStructureFeature.class))
        {
            featureScores[5] = baseStructureFeatureCounts.get(
                LogicalORSGMStructureFeature.class);
        }
        
        featureScores[6] = 0; // Logical XOR
        if (baseStructureFeatureCounts.containsKey(
            LogicalXORSGMStructureFeature.class))
        {
            featureScores[6] = baseStructureFeatureCounts.get(
                LogicalXORSGMStructureFeature.class);
        }
        
        featureScores[7] = 0; // Logical AND
        if (baseStructureFeatureCounts.containsKey(
            LogicalANDSGMStructureFeature.class))
        {
            featureScores[7] = baseStructureFeatureCounts.get(
                LogicalANDSGMStructureFeature.class);
        }
        
        // Supplemental Structure Features
        featureScores[8] = 0; // Fill Pattern Repetition
        if (supplementalStructureFeatureCounts.containsKey(
            FillPatternRepetitionSGMStructureFeature.class))
        {
            featureScores[8] = supplementalStructureFeatureCounts.get(
                FillPatternRepetitionSGMStructureFeature.class);
        }
        
        featureScores[9] = 0; // Apply Translation (not implemented yet)
        
        featureScores[10] = 0; // Apply Rotation
        if (supplementalStructureFeatureCounts.containsKey(
            ApplyRotationSGMStructureFeature.class))
        {
            featureScores[10] = supplementalStructureFeatureCounts.get(
                ApplyRotationSGMStructureFeature.class);
        }
        
        featureScores[11] = 0; // Apply Scaling
        if (supplementalStructureFeatureCounts.containsKey(
            ApplyScalingSGMStructureFeature.class))
        {
            featureScores[11] = supplementalStructureFeatureCounts.get(
                ApplyScalingSGMStructureFeature.class);
        }
        
        featureScores[12] = 0; // Translational Numerosity
        if (supplementalStructureFeatureCounts.containsKey(
            TranslationalNumerositySGMStructureFeature.class))
        {
            featureScores[12] = supplementalStructureFeatureCounts.get(
                TranslationalNumerositySGMStructureFeature.class);
        }
        
        featureScores[13] = 0; // Rotational Numerosity (not implemented yet)
        
        featureScores[14] = 0; // Scaling Numerosity (not implemented yet)
        
        featureScores[15] = 0; // Deformation (not implemented yet)
        
        // Location Transforms
        featureScores[16] = 0; // Pattern Location Transform 
                               // (not implemented yet)
        
        featureScores[17] = 0; // Horizontal Location Transform
        if (locationTransformCounts.containsKey(
            HorizontalSGMLocationTransform.class))
        {
            featureScores[17] = locationTransformCounts.get(
                HorizontalSGMLocationTransform.class);
        }
        
        featureScores[18] = 0; // Vertical Location Transform
        if (locationTransformCounts.containsKey(
            VerticalSGMLocationTransform.class))
        {
            featureScores[18] = locationTransformCounts.get(
                VerticalSGMLocationTransform.class);
        }
        
        featureScores[19] = 0; // BL-TR Diagonal Location Transform
        if (locationTransformCounts.containsKey(
            DiagonalBottomLeftTopRightSGMLocationTransform.class))
        {
            featureScores[19] = locationTransformCounts.get(
                DiagonalBottomLeftTopRightSGMLocationTransform.class);
        }
        
        featureScores[20] = 0; // TL-BR Diagonal Location Transform
        if (locationTransformCounts.containsKey(
            DiagonalTopLeftBottomRightSGMLocationTransform.class))
        {
            featureScores[20] = locationTransformCounts.get(
                DiagonalTopLeftBottomRightSGMLocationTransform.class);
        }
        
        featureScores[21] = 0; // Logic Location Transform
        if (locationTransformCounts.containsKey(
            LogicSGMLocationTransform.class))
        {
            featureScores[21] = locationTransformCounts.get(
                LogicSGMLocationTransform.class);
        }
        
        featureScores[22] = 0; // Out From TL All Cells Location Transform
        if (locationTransformCounts.containsKey(
            TopLeftCornerOutSGMLocationTransform.class))
        {
            featureScores[22] = locationTransformCounts.get(
                TopLeftCornerOutSGMLocationTransform.class);
        }
        
        // Base Surface Feature Complexity
        featureScores[23] = 0; // Simple Repeating Background 
                               // (not implemented yet)
        
        featureScores[24] = 0; // Gradated Background (not implemented yet)
        
        featureScores[25] = 0; // Complex Line Pattern Background 
                               // (not implemented yet)
        
        featureScores[26] = 0; // Empty Space (not implemented yet)
        
        featureScores[27] = 0; // Simple Geometric Shape
        // TODO - as soon as add more surface feature types, will need to
        // change class key to more granular type
        if (surfaceFeatureComplexityCounts.containsKey(
            SGMSurfaceFeature.class))
        {
            featureScores[27] = surfaceFeatureComplexityCounts.get(
                SGMSurfaceFeature.class);
        }
        
        featureScores[28] = 0; // Compound Geometric Shape (not implemented yet)
        
        featureScores[29] = 0; // Complex Shape (not implemented yet)
        
        featureScores[30] = 0; // Shape Variances (not implemented yet)
        
        // Wrong Answer Type
        Map<WrongAnswerType, Integer> answerTypeCounts = 
            matrix.getWrongAnswerTypeCounts();
        featureScores[31] = 0; // Cell from Matrix Other Than Correct Answer
        if (answerTypeCounts.containsKey(
            WrongAnswerType.INCORRECT_CELL_FROM_MATRIX))
        {
            featureScores[31] = answerTypeCounts.get(
                WrongAnswerType.INCORRECT_CELL_FROM_MATRIX);
        }        
        
        featureScores[32] = 0; // Structure Feature Based Modification to 
                               // Matrix Cell Other Than Correct Answer                               
        if (answerTypeCounts.containsKey(
            WrongAnswerType.MODIFIED_INCORRECT_CELL_FROM_MATRIX))
        {
            featureScores[32] = answerTypeCounts.get(
                WrongAnswerType.MODIFIED_INCORRECT_CELL_FROM_MATRIX);
        }
        
        featureScores[33] = 0; // Structure Feature Based Modification to 
                               // Correct Answer
        if (answerTypeCounts.containsKey(
            WrongAnswerType.MODIFIED_CORRECT_ANSWER))
        {
            featureScores[33] = answerTypeCounts.get(
                WrongAnswerType.MODIFIED_CORRECT_ANSWER);
        }
        
        featureScores[34] = 0; // Structure Feature Based Modification to 
                               // a Wrong Answer
        if (answerTypeCounts.containsKey(
            WrongAnswerType.MODIFIED_WRONG_ANSWER))
        {
            featureScores[34] = answerTypeCounts.get(
                WrongAnswerType.MODIFIED_WRONG_ANSWER);
        }
        
        featureScores[35] = 0; // Combination of Subset of Surface Features 
                               // Across Matrix
        if (answerTypeCounts.containsKey(
            WrongAnswerType.MATRIX_SURFACE_FEATURE_COMBINATION))
        {
            featureScores[35] = answerTypeCounts.get(
                WrongAnswerType.MATRIX_SURFACE_FEATURE_COMBINATION);
        }
        
        featureScores[36] = 0; // Novel Surface Feature Not in Matrix    
        if (answerTypeCounts.containsKey(
            WrongAnswerType.NOVEL_SURFACE_FEATURE))
        {
            featureScores[35] = answerTypeCounts.get(
                WrongAnswerType.NOVEL_SURFACE_FEATURE);
        }
        
        // Evaluate the score of the feature vector
        VectorFactory vectorFactory = VectorFactory.getDefault();
        Vector featureVector = vectorFactory.copyArray(featureScores);
        
        System.out.println(sb.toString() + " " + featureVector);
                
        return new SGMScore(this.evaluate(featureVector));
    }
}
