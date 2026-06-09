/*
 * File:                AbstractBaseSGMStructureFeature.java
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
 * $Log: AbstractBaseSGMStructureFeature.java,v $
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
 * Revision 1.1  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.1  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
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
 
package gov.sandia.cognition.generator.matrix.structure.base;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public abstract class AbstractBaseSGMStructureFeature
    implements BaseSGMStructureFeature
{
    private SGMLocationTransform locationTransform;
    
    public AbstractBaseSGMStructureFeature(
        final SGMLocationTransform locationTransform)
    {
        this.setLocationTransform(locationTransform);
    }
    
    public SGMLocationTransform getLocationTransform()
    {
        return this.locationTransform;
    }

    public abstract List<SGMSurfaceFeature> provideBaseSurfaceFeatures(
        final int sgmBaseLocationIndex);

    public abstract List<SGMSurfaceFeature> transformSurfaceFeatures(
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocation);

    public abstract String getDescription();

    public abstract boolean checkCompatibility(
        final SGMFeature feature);

    private void setLocationTransform(
        final SGMLocationTransform locationTransform)
    {
        this.locationTransform = locationTransform;
    }

}
