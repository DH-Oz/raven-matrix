/*
 * File:                BaseSGMStructureFeatureGenerator.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 13, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: BaseSGMStructureFeatureGenerator.java,v $
 * Revision 1.2  2010/12/21 16:10:58  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:07  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:05  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:32  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:29  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.12  2008/11/05 18:24:26  cewarr
 * Tweaked the grey fill patterns, added two shapes, eliminated squares/circles and repeat use of same shape in a matrix, fixed some problems with wrong answers when numerosity is used.
 *
 * Revision 1.11  2008/10/07 21:42:05  zobenz
 * Functioning SGM Builder GUI
 *
 * Revision 1.10  2008/10/06 21:07:20  zobenz
 * Rough in of SGM Builder
 *
 * Revision 1.9  2008/01/07 21:11:17  zobenz
 * Tested xml serialization of generated set of matrices
 *
 * Revision 1.8  2007/12/17 16:04:17  zobenz
 * Enabled XOR logical transform (it had been disabled by accident)
 *
 * Revision 1.7  2007/12/14 21:40:09  zobenz
 * Implemented TopLeftCornerOutSGMLocationTransform and associated infrastructure improvements
 *
 * Revision 1.6  2007/12/14 16:06:13  zobenz
 * Fixed bug with > 1 structure features per layer (by disallowing supplemental structure features when base structure feature is a logic operation)
 *
 * Revision 1.5  2007/12/13 20:57:09  zobenz
 * Finished filling in some documentation that was marked TODO; as an aside, the code currently has a bug if you set max structure features per layer> 1
 *
 * Revision 1.4  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.3  2007/12/13 18:19:40  zobenz
 * Implemented infrastructure for logic operation structure features and implemented Logical OR
 *
 * Revision 1.2  2007/12/13 16:03:24  zobenz
 * Implemented class for generating base structure features
 *
 * Revision 1.1  2007/12/13 15:54:53  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 */
 
package gov.sandia.cognition.generator.matrix.structure.base;

import gov.sandia.cognition.generator.matrix.SGMMatrixSize;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.WhiteSGMFillPattern;
import gov.sandia.cognition.generator.matrix.locationtransform.LogicSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransformGenerator;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransformGenerator.LocationTransformType;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeatureGenerator;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class BaseSGMStructureFeatureGenerator
{
    public enum BaseStructureFeatureType
    {
        UNSPECIFIED,
        SHAPE_REPETITION,
        LOGICAL_OR,
        LOGICAL_AND,
        LOGICAL_XOR;
    }
    
    public static final int MIN_SURFACE_FEATURES_FOR_LOGIC_OPERATION = 3;
    public static final int MAX_SURFACE_FEATURES_FOR_LOGIC_OPERATION = 5;
    
    public static BaseSGMStructureFeature generateStructureFeature(
        final SGMMatrixSize sgmMatrixSize,
        final int sgmCellImagePixelSize,
        final Random random)
    {
        return generateStructureFeature(sgmMatrixSize,
            sgmCellImagePixelSize, random,
            BaseStructureFeatureType.UNSPECIFIED,
            LocationTransformType.UNSPECIFIED);
    }
    
    public static BaseSGMStructureFeature generateStructureFeature(
        final SGMMatrixSize sgmMatrixSize,
        final int sgmCellImagePixelSize,
        final Random random,
        BaseStructureFeatureType baseStructureFeatureType,
        LocationTransformType locationTransformType)
    {
        // TODO - through reflection dynamically determine the 
        // SGMStructureFeatures available... [20071130 ZOB] this turns out to
        // be extremely non-trivial to do, sadly (although ServiceLoader in Java
        // 6 may help).  One way to do it with reflection can be found here:
        // http://lists.apple.com/archives/Java-dev/2006/Jun/msg00109.html                
        
        // Generate structure feature
        BaseSGMStructureFeature structureFeature = null;
        int type = -1;
        int logicalType = -1;
        if (baseStructureFeatureType == BaseStructureFeatureType.UNSPECIFIED)
        {
            // Generate type stochastically
            if ((sgmMatrixSize.getNumRows() > 2) &&
                (sgmMatrixSize.getNumColumns() > 2))
            {
                // Can only do logic operation structure features for matrices
                // at least 3x3 in size
                type = random.nextInt(2);
            }
            else
            {
                // Matrix too small, exclude logic operation structure features
                type = random.nextInt(1);
            }
        }
        else if (baseStructureFeatureType == 
            BaseStructureFeatureType.SHAPE_REPETITION)
        {
            // Shape repetition
            type = 0;
        }
        else
        {
            // Logical operation
            type = 1;
            if (baseStructureFeatureType == 
                BaseStructureFeatureType.LOGICAL_OR)
            {
                // OR
                logicalType = 0;
            }
            else if (baseStructureFeatureType == 
                BaseStructureFeatureType.LOGICAL_AND)
            {
                // AND
                logicalType = 1;
            }
            else
            {
                // XOR
                logicalType = 2;
            }
        }
        
        switch (type)
        {
            case 0:      
                // Shape repetition

                // Stochastically pick a location transform as part of
                // creating the shape repetition structure feature                
                SGMLocationTransform locationTransform =
                    SGMLocationTransformGenerator.generateLocationTransform(
                    sgmMatrixSize, random, locationTransformType);
                
                structureFeature = new ShapeRepetitionSGMStructureFeature(
                    locationTransform, createBasicBaseSurfaceFeatures(
                    locationTransform.getBaseLocations().size(),
                    sgmCellImagePixelSize, random));
                break;
            case 1:
                // Logic operation
                List<SGMFillPattern> allowedFillPatterns =
                    new ArrayList<SGMFillPattern>(1);
                allowedFillPatterns.add(new WhiteSGMFillPattern());
                
                int numSurfaceFeatures = 
                    random.nextInt(MAX_SURFACE_FEATURES_FOR_LOGIC_OPERATION - 
                    MIN_SURFACE_FEATURES_FOR_LOGIC_OPERATION + 1) +
                    MIN_SURFACE_FEATURES_FOR_LOGIC_OPERATION;
                List<SGMSurfaceFeature> baseSurfaceFeatures =
                    new ArrayList<SGMSurfaceFeature>(numSurfaceFeatures);
                while (baseSurfaceFeatures.size() < numSurfaceFeatures)                
                {                   
                    SGMSurfaceFeature feature = SGMSurfaceFeatureGenerator.
                        generateSurfaceFeature(sgmCellImagePixelSize,
                        allowedFillPatterns, random);
                    
                    // Check for duplicates
                    if (!containsCheck(baseSurfaceFeatures, feature))
                    {                        
                        baseSurfaceFeatures.add(feature);
                    }
                }
                
                if (logicalType < 0)
                {
                    // Generate stochastically
                    logicalType = random.nextInt(3);
                }
                switch (logicalType)
                {
                    case 0:
                        // OR logic operation                                               
                        structureFeature = new LogicalORSGMStructureFeature(
                            new LogicSGMLocationTransform(sgmMatrixSize),
                            baseSurfaceFeatures, random);                        
                        break;
                    case 1:
                        // AND logic operation                                               
                        structureFeature = new LogicalANDSGMStructureFeature(
                            new LogicSGMLocationTransform(sgmMatrixSize),
                            baseSurfaceFeatures, random);                        
                        break;
                    case 2:
                        // XOR logic operation                                               
                        structureFeature = new LogicalXORSGMStructureFeature(
                            new LogicSGMLocationTransform(sgmMatrixSize),
                            baseSurfaceFeatures, random);                        
                        break;
                }
                break;
        }

        return structureFeature;
    }
    
    private static List<List<SGMSurfaceFeature>>
        createBasicBaseSurfaceFeatures(
        final int maxDimension,
        final int sgmCellImagePixelSize,
        final Random random)
    {
        return createBasicBaseSurfaceFeatures(
                maxDimension, sgmCellImagePixelSize, true, random);
    }

    
    private static List<List<SGMSurfaceFeature>>
        createBasicBaseSurfaceFeatures(
        final int maxDimension,
        final int sgmCellImagePixelSize,
        boolean uniqueShapes,
        final Random random)
    {
        
        // Create storage for the base surface features
        ArrayList<List<SGMSurfaceFeature>> baseSurfaceFeatures =
            new ArrayList<List<SGMSurfaceFeature>>(3);

        List<Class> shapesUsed = new ArrayList<Class>();
        
        // Create base surface features stochastically
        for (int i = 0; i < maxDimension; i++)
        {
            List<SGMSurfaceFeature> surfaceFeatures =
                new ArrayList<SGMSurfaceFeature>(1);
            SGMSurfaceFeature feature = SGMSurfaceFeatureGenerator.
                generateSurfaceFeature(sgmCellImagePixelSize,
                random);
            if (uniqueShapes)
            {
                while (shapesUsed.contains(feature.getClass()))
                {
                    feature = SGMSurfaceFeatureGenerator.
                            generateSurfaceFeature(sgmCellImagePixelSize,
                            random);
                }
            }
            
            surfaceFeatures.add(feature);
            shapesUsed.add(feature.getClass());
            baseSurfaceFeatures.add(surfaceFeatures);
        }

        return baseSurfaceFeatures;
    } 
    
    private static boolean containsCheck(
        final List<SGMSurfaceFeature> surfaceFeatures,
        final SGMSurfaceFeature surfaceFeature)
    {               
        // Built-in List contains check is wrong thing to do here (which is 
        // why we don't do it) - don't want that it contains the same object
        // reference, but rather that there is some surface feature that
        // fundamentally _equals_ this surface feature in terms of its 
        // properties
        for (SGMSurfaceFeature feature : surfaceFeatures)
        {
            if (feature.equals(surfaceFeature))
            {
                return true;
            }
        }        
        return false;
    }
}
