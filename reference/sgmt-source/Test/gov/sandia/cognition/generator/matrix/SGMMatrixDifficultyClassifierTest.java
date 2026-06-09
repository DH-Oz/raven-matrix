/*
 * File:                SGMMatrixDifficultyClassifierTest.java
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
 * $Log: SGMMatrixDifficultyClassifierTest.java,v $
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
 * Revision 1.8  2010/06/30 21:15:29  cewarr
 * more changes to match Foundry changes
 *
 * Revision 1.7  2009/08/10 22:33:51  krdixon
 * Rewrite of NN and k-NN classes, moved to the "nearest" package, made more
 * OO.
 *
 * Revision 1.6  2009/02/06 20:38:28  krdixon
 * Changes to accommodate statistics package rewrite
 *
 * Revision 1.5  2008/01/09 23:42:53  krdixon
 * Fully implemented, with unit test
 *
 * Revision 1.4  2007/12/18 22:53:10  krdixon
 * Now using LocallyWeightedLearning
 *
 * Revision 1.3  2007/12/18 22:34:31  krdixon
 * Update with k-Nearest Neighbor
 *
 * Revision 1.2  2007/12/18 22:18:21  jdbasil
 * Cleaned up experiments.
 *
 * Revision 1.1  2007/12/18 20:15:56  krdixon
 * Initial Revision
 *
 */

package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.SGMMatrixDifficultyClassifier;
import gov.sandia.cognition.evaluator.Evaluator;
import gov.sandia.cognition.learning.algorithm.nearest.KNearestNeighborKDTree;
import gov.sandia.cognition.learning.algorithm.regression.LinearRegression;
import gov.sandia.cognition.learning.algorithm.regression.LocallyWeightedFunction;
import gov.sandia.cognition.learning.algorithm.tree.RegressionTreeLearner;
import gov.sandia.cognition.learning.algorithm.tree.VectorThresholdVarianceLearner;
import gov.sandia.cognition.learning.data.DefaultInputOutputPair;
import gov.sandia.cognition.learning.data.InputOutputPair;
import gov.sandia.cognition.learning.function.distance.EuclideanDistanceMetric;
import gov.sandia.cognition.learning.function.kernel.RadialBasisKernel;
import gov.sandia.cognition.learning.function.vector.VectorizableVectorConverter;
import gov.sandia.cognition.math.NumberAverager;
import gov.sandia.cognition.math.matrix.Vector;
import gov.sandia.cognition.math.matrix.VectorReader;
import gov.sandia.cognition.statistics.method.ConfidenceInterval;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;
import junit.framework.TestCase;

/**
 * JUnit tests for class SGMMatrixDifficultyClassifierTest
 * @author Kevin R. Dixon
 */
public class SGMMatrixDifficultyClassifierTest
    extends TestCase
{

    /**
     * Entry point for JUnit tests for class SGMMatrixDifficultyClassifierTest
     * @param testName name of this test
     */
    public SGMMatrixDifficultyClassifierTest(
        String testName )
    {
        super( testName );
    }

    /**
     * Test of clone method, of class SGMMatrixDifficultyClassifier.
     */
    public void testClone()
    {
        System.out.println( "clone" );
        SGMMatrixDifficultyClassifier instance =
            new SGMMatrixDifficultyClassifier( (Evaluator<? super Vector, Double>) null);
        SGMMatrixDifficultyClassifier result = instance.clone();
        assertNotSame( result, instance );

    }

    public void testCreate() throws Exception
    {

        System.out.println( "create" );
        VectorReader inputFile = new VectorReader( new FileReader( "SGM_dataset.input.txt" ) );
        List<Vector> inputs = inputFile.readCollection( true );
        System.out.println( "Read: " + inputs.size() );

        VectorReader targetFile = new VectorReader( new FileReader( "SGM_dataset.target.txt" ) );
        List<Vector> targetVectors = targetFile.readCollection( true );
        
        assertEquals( inputs.size(), targetVectors.size() );
        
        int num = inputs.size();
        ArrayList<Double> targets = new ArrayList<Double>( num );
        for( Vector t : targetVectors )
        {
            targets.add( t.getElement(0) );
        }
        
        ArrayList<DefaultInputOutputPair<Vector,Double>> inputTargetPairs =
            DefaultInputOutputPair.mergeCollections(inputs, targets);
        
        ConfidenceInterval result;
        
        LinearRegression<Vector> regression = 
            new LinearRegression<Vector>( new VectorizableVectorConverter());
        result = SGMMatrixDifficultyClassifier.testPerformance(inputTargetPairs, regression);
        
        System.out.println( "Linear Regression 1-norm: " + result );        
        
        VectorThresholdVarianceLearner decisionLearner =
            new VectorThresholdVarianceLearner();
        RegressionTreeLearner<Vector> treeLearner = new RegressionTreeLearner<Vector>(
            decisionLearner, null );
        result = SGMMatrixDifficultyClassifier.testPerformance(inputTargetPairs, treeLearner);
        System.out.println( "Regression Tree 1-norm: " + result );
        
        KNearestNeighborKDTree.Learner<Vector,Double> knear =
            new KNearestNeighborKDTree.Learner<Vector, Double>( 3, new EuclideanDistanceMetric(), new NumberAverager() );
        result = SGMMatrixDifficultyClassifier.testPerformance(inputTargetPairs, knear);
        System.out.println( "k-Nearest Neighbor 1-norm: " + result );
        
        LocallyWeightedFunction.Learner<Vector,Double> lwl = 
            new LocallyWeightedFunction.Learner<Vector,Double>( new RadialBasisKernel(10.0), regression );
        result = SGMMatrixDifficultyClassifier.testPerformance(inputTargetPairs, lwl);
        System.out.println( "LWL: " + result );
    }

}
