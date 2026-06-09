/*
 * File:                LogicalANDSGMStructureFeature.java
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
 * $Log: LogicalANDSGMStructureFeature.java,v $
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
 * Revision 1.1  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 */
 
package gov.sandia.cognition.generator.matrix.structure.base;

import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class LogicalANDSGMStructureFeature
    extends AbstractLogicOperationSGMStructureFeature
{
    public static final String DESCRIPTION = "Logical AND";    
    
    public LogicalANDSGMStructureFeature(
        final SGMLocationTransform locationTransform,
        final List<SGMSurfaceFeature> baseSurfaceFeatures,
        final Random random)
    {
        super(locationTransform, baseSurfaceFeatures, random);
    }
    
    @Override
    public List<SGMSurfaceFeature> transformSurfaceFeatures(
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocationOne,
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocationTwo)
    {
        // Perform AND by collecting a list of features that exist at
        // both locations
        List<SGMSurfaceFeature> surfaceFeatures =
            new ArrayList<SGMSurfaceFeature>();
        
        for (SGMSurfaceFeature feature : surfaceFeaturesAtPreviousLocationOne)
        {   
            if (surfaceFeaturesAtPreviousLocationTwo.contains(feature))
            {
                surfaceFeatures.add(feature);            
            }
        }
        
        return surfaceFeatures;
    }

    @Override
    public String getDescription()
    {
        return DESCRIPTION;
    }    
}

