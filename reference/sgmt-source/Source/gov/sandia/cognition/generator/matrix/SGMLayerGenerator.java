/*
 * File:                SGMLayerGenerator.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 10, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMLayerGenerator.java,v $
 * Revision 1.1  2010/12/21 15:50:05  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:04  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:34  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:23  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.9  2007/12/14 16:06:13  zobenz
 * Fixed bug with > 1 structure features per layer (by disallowing supplemental structure features when base structure feature is a logic operation)
 *
 * Revision 1.8  2007/12/13 16:03:24  zobenz
 * Implemented class for generating base structure features
 *
 * Revision 1.7  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.6  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
 *
 * Revision 1.5  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.4  2007/12/10 23:39:50  zobenz
 * Added numerosity structure feature
 *
 * Revision 1.3  2007/12/10 21:59:05  zobenz
 * Cleaned up surface feature generation to improve visual layout
 *
 * Revision 1.2  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.1  2007/12/10 20:01:51  zobenz
 * Moved SGMLayer generation to its own class
 *
 */
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.structure.SGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.AbstractLogicOperationSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.BaseSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.BaseSGMStructureFeatureGenerator;
import gov.sandia.cognition.generator.matrix.structure.supplemental.SupplementalSGMStructureFeatureGenerator;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMLayerGenerator
{
    public static SGMLayer generateLayer(
        final SGMMatrixSize sgmMatrixSize,
        final int maxStructureFeaturesPerLayer,
        final int sgmCellImagePixelSize,
        final Random random)
    {
        // Stochastically determine number of structure features
        int numStructureFeatures =
            random.nextInt(maxStructureFeaturesPerLayer) + 1;      
        List<SGMStructureFeature> structureFeatures =
            new ArrayList<SGMStructureFeature>(numStructureFeatures);

        // Create the base structure feature, which defines the
        // base surface features   
        BaseSGMStructureFeature baseStructureFeature =
            BaseSGMStructureFeatureGenerator.
            generateStructureFeature(sgmMatrixSize, sgmCellImagePixelSize,
            random);
        structureFeatures.add(baseStructureFeature);

// TODO - only certain combinations of supplemental features are valid... so
// we need to check for this 
        if (!(baseStructureFeature instanceof 
            AbstractLogicOperationSGMStructureFeature))
        {
            // Create supplemental structure features
            for (int i = 1; i < numStructureFeatures; i++)
            {
                structureFeatures.add(
                    SupplementalSGMStructureFeatureGenerator.
                    generateStructureFeature(sgmMatrixSize,
                    sgmCellImagePixelSize, random));
            }
        }

        // Create and store the layer
        return new SGMLayer(sgmMatrixSize, structureFeatures);
    }   
}
