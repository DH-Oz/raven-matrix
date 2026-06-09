/*
 * File:                SupplementalSGMStructureFeatureGenerator.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 30, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SupplementalSGMStructureFeatureGenerator.java,v $
 * Revision 1.2  2010/12/21 16:10:58  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:07  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:03  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:37  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:30  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.7  2008/11/05 18:24:26  cewarr
 * Tweaked the grey fill patterns, added two shapes, eliminated squares/circles and repeat use of same shape in a matrix, fixed some problems with wrong answers when numerosity is used.
 *
 * Revision 1.6  2008/11/03 18:50:43  cewarr
 * Added ability to rotate through fill patterns, and two more grey levels so there are 5 fill patterns total.  (bug 1273)
 *
 * Revision 1.5  2008/10/07 21:42:05  zobenz
 * Functioning SGM Builder GUI
 *
 * Revision 1.4  2007/12/14 17:21:55  zobenz
 * Added an initialNumerosity parameter
 *
 * Revision 1.3  2007/12/14 16:06:13  zobenz
 * Fixed bug with > 1 structure features per layer (by disallowing supplemental structure features when base structure feature is a logic operation)
 *
 * Revision 1.2  2007/12/13 16:03:24  zobenz
 * Implemented class for generating base structure features
 *
 * Revision 1.1  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.1  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
 *
 * Revision 1.5  2007/12/11 17:35:32  zobenz
 * Improved numerosity to use consistent scaling and positioning across cells along location transform
 *
 * Revision 1.4  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.3  2007/12/10 23:39:50  zobenz
 * Added numerosity structure feature
 *
 * Revision 1.2  2007/12/10 21:59:06  zobenz
 * Cleaned up surface feature generation to improve visual layout
 *
 * Revision 1.1  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.10  2007/12/10 18:55:41  zobenz
 * Fixed surface feature equals check to take into account fill pattern (except when comparing lines, as fill pattern is irrelevant for them)
 *
 * Revision 1.9  2007/12/10 18:28:38  zobenz
 * Added "explain" feature to textually describe how a matrix was constructed
 *
 * Revision 1.8  2007/12/07 00:24:40  zobenz
 * Added fill pattern repetition structure feature
 *
 * Revision 1.7  2007/12/06 23:28:32  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.6  2007/12/06 19:04:41  zobenz
 * Committing working implementation in preparation for overhauling way in which structure features are applied
 *
 * Revision 1.5  2007/12/05 23:55:28  zobenz
 * Fixed Rotate structure feature (but still disabled in matrix generation for now); implemented Scale structure feature
 *
 * Revision 1.4  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.3  2007/12/05 20:44:55  zobenz
 * Improved answer choice generation; Replaced SetIteration structure feature with Identity structure feature; added Rotate structure feature (which has a bug right now)
 *
 * Revision 1.2  2007/12/03 23:09:21  zobenz
 * Initial implementation of a complete top to bottom stochastic generation of SGMs
 *
 * Revision 1.1  2007/11/30 23:10:58  zobenz
 * Work in progress on stochastic SGM generation
 *
 */
package gov.sandia.cognition.generator.matrix.structure.supplemental;

import gov.sandia.cognition.generator.matrix.SGMMatrixSize;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransformGenerator;
import gov.sandia.cognition.generator.matrix.fillpattern.BlackSGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.Grey10SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.Grey75SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.Grey40SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.WhiteSGMFillPattern;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransformGenerator.LocationTransformType;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SupplementalSGMStructureFeatureGenerator
{
    public enum SupplementalStructureFeatureType
    {
        UNSPECIFIED,
        APPLY_ROTATION,
        APPLY_SCALING,
        FILL_PATTERN_REPETITION,
        CHANGE_FILL_PATTERN,
        TRANSLATIONAL_NUMEROSITY;
    }
    
    public static final int MAX_INITIAL_NUMEROSITY = 2;
    
    public static SupplementalSGMStructureFeature generateStructureFeature(
        final SGMMatrixSize sgmMatrixSize,
        final int sgmCellImagePixelSize,
        final Random random)
    {
        return generateStructureFeature(sgmMatrixSize,
            sgmCellImagePixelSize, random,
            SupplementalStructureFeatureType.UNSPECIFIED,
            LocationTransformType.UNSPECIFIED);
    }
    
    public static SupplementalSGMStructureFeature generateStructureFeature(
        final SGMMatrixSize sgmMatrixSize,
        final int sgmCellImagePixelSize,
        final Random random,
        final SupplementalStructureFeatureType supplementalStructureFeatureType,
        final LocationTransformType locationTransformType)
    {
        // TODO - through reflection dynamically determine the 
        // SGMStructureFeatures available... [20071130 ZOB] this turns out to
        // be extremely non-trivial to do, sadly (although ServiceLoader in Java
        // 6 may help).  One way to do it with reflection can be found here:
        // http://lists.apple.com/archives/Java-dev/2006/Jun/msg00109.html
        
        // Stochastically pick a location transform
        SGMLocationTransform locationTransform =
            SGMLocationTransformGenerator.generateLocationTransform(
            sgmMatrixSize, random, locationTransformType);
        
        // Generate structure feature
        SupplementalSGMStructureFeature structureFeature = null;
        int type = -1;
        if (supplementalStructureFeatureType == 
            SupplementalStructureFeatureType.UNSPECIFIED)
        {   
            // Generate stochastically
            type = random.nextInt(5);                        
        }
        else if (supplementalStructureFeatureType == 
            SupplementalStructureFeatureType.APPLY_SCALING)
        {
            // Apply Scaling
            type = 0;
        }
        else if (supplementalStructureFeatureType == 
            SupplementalStructureFeatureType.FILL_PATTERN_REPETITION)
        {
            // Fill Pattern Repetition
            type = 1;
        }
        else if (supplementalStructureFeatureType == 
            SupplementalStructureFeatureType.APPLY_ROTATION)
        {
            // Apply Rotation
            type = 2;
        }
        else if (supplementalStructureFeatureType ==
                SupplementalStructureFeatureType.TRANSLATIONAL_NUMEROSITY)
        {
            // Translational Numerosity
            type = 3;
        }
        else
        {
            // Change Fill Pattern
            type = 4;
        }
        switch (type)
        {
            case 0:                               
                // Scale factor of 0.66
                double scale = 0.66;

                // Create structure feature
                structureFeature = 
                    new ApplyScalingSGMStructureFeature(
                    locationTransform, scale);                
                break;
            case 1:
// TODO - stochastically pick fill patterns                
                List<SGMFillPattern> baseFillPatterns =
                    new ArrayList<SGMFillPattern>(3);
                baseFillPatterns.add(new WhiteSGMFillPattern());
                baseFillPatterns.add(new BlackSGMFillPattern());
                baseFillPatterns.add(new Grey75SGMFillPattern());
                
                // Create structure feature                
                structureFeature =
                    new FillPatternRepetitionSGMStructureFeature(
                    locationTransform, baseFillPatterns);
                break;                
            case 2:                
                // Only support 45 degree rotation right now
                int rotation = 45;

                // Create structure feature
                structureFeature = 
                    new ApplyRotationSGMStructureFeature(
                    locationTransform, rotation);                
                break;     
            case 3:
                int initialNumerosity = 
                    random.nextInt(MAX_INITIAL_NUMEROSITY) + 1;
                
                structureFeature =
                    new TranslationalNumerositySGMStructureFeature(
                    locationTransform, 
                    sgmCellImagePixelSize, sgmMatrixSize,
                    initialNumerosity);
                break;
            case 4:
                List<SGMFillPattern> fillPatterns =
                    new ArrayList<SGMFillPattern>(5);
                fillPatterns.add(new WhiteSGMFillPattern());
                fillPatterns.add(new Grey75SGMFillPattern());
                fillPatterns.add(new Grey40SGMFillPattern());
                fillPatterns.add(new Grey10SGMFillPattern());
                fillPatterns.add(new BlackSGMFillPattern());
                
                // Create structure feature                
                structureFeature =
                    new ChangeFillPatternSGMStructureFeature(
                    locationTransform, fillPatterns);
                break;                
                
        }

        return structureFeature;
    }
}
