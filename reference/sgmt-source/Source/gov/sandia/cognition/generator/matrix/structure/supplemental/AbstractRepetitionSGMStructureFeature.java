/*
 * File:                AbstractRepetitionSGMStructureFeature.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 6, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: AbstractRepetitionSGMStructureFeature.java,v $
 * Revision 1.1  2010/12/21 15:50:08  zobenz
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
 * Revision 1.3  2008/10/29 22:53:59  cewarr
 * Fixed bug 1293, allowing scaling and numerosity to be combined, by 1) combining scaling factor numerosity uses with existing scale factor and 2) allowing repetition (scaling/rotation) to apply one surface feature from previous cell to multiple surface features in current cell.
 *
 * Revision 1.2  2007/12/14 16:06:13  zobenz
 * Fixed bug with > 1 structure features per layer (by disallowing supplemental structure features when base structure feature is a logic operation)
 *
 * Revision 1.1  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.5  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
 *
 * Revision 1.4  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.3  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.2  2007/12/07 00:00:52  zobenz
 * Removed some debug statements; disabled rotate structure feature again for the time being
 *
 * Revision 1.1  2007/12/06 23:28:32  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 */
 
package gov.sandia.cognition.generator.matrix.structure.supplemental;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.ArrayList;
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public abstract class AbstractRepetitionSGMStructureFeature
    extends AbstractSupplementalSGMStructureFeature
{
    public AbstractRepetitionSGMStructureFeature(
        final SGMLocationTransform locationTransform)
    {
        super(locationTransform);
    }
    
    public List<SGMSurfaceFeature> provideBaseSurfaceFeatures(
        final int sgmBaseLocationIndex,
        final List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation)
    {            
        return existingSurfaceFeaturesAtLocation;
    }

    protected abstract SGMSurfaceFeature applyTransform(
        final SGMSurfaceFeature feature,
        final SGMSurfaceFeature previousLocationFeature);
    
    public List<SGMSurfaceFeature> transformSurfaceFeatures(
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocation,
        final List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation)
    {        
        if (existingSurfaceFeaturesAtLocation != null)            
        {
            // Can only repeat structure feature if there is a one-to-one
            // mapping of the number of existing surface features from
            // previous location surface features
            // cew 081029:  this restriction means that repetition (including
            // scaling and rotation) can't be applied after numerosity.
            // As a temporary fix, I'm going to assume that the parameter to
            // be repeated/transformed is in the previous cell's first feature
            // only, but this is clearly not an optimal solution.
//            if (surfaceFeaturesAtPreviousLocation.size() !=
//                existingSurfaceFeaturesAtLocation.size())
//            {
//                throw new IllegalArgumentException(
//                    "AbstractRepetitionSGMStructureFeature requires that " +
//                    "there be the same number of surface features at " +
//                    "previous location and current location (" +
//                    surfaceFeaturesAtPreviousLocation.size() + " != " +
//                    existingSurfaceFeaturesAtLocation.size() + ")");
//            }
            
            List<SGMSurfaceFeature> transformedFeatures =
                new ArrayList<SGMSurfaceFeature>(
                existingSurfaceFeaturesAtLocation.size());
                        
            for (int i = 0; i < existingSurfaceFeaturesAtLocation.size(); i++)
            {                                
                // Start with a copy of existing feature at location so we can
                // keep everything except parameter being repeated from
                // previous location                
                SGMSurfaceFeature transformedFeature =
                    existingSurfaceFeaturesAtLocation.get(i).clone();                    
                
                // Overwrite unchanged parameters with what is already
                // at this location, and store the transformed feature                
                transformedFeatures.add(this.applyTransform(transformedFeature,
                    surfaceFeaturesAtPreviousLocation.get(0)));
            }
            
            return transformedFeatures;
        }
        else
        {
            return surfaceFeaturesAtPreviousLocation;
        }        
    }

    public abstract String getDescription();

    public abstract boolean checkCompatibility(
        final SGMFeature feature);
}
