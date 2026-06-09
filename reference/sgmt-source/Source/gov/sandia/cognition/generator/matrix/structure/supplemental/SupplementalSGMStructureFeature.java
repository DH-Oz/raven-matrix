/*
 * File:                SupplementalSGMStructureFeature.java
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
 * $Log: SupplementalSGMStructureFeature.java,v $
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
 * Revision 1.1  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.1  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
 *
 */
 
package gov.sandia.cognition.generator.matrix.structure.supplemental;

import gov.sandia.cognition.generator.matrix.structure.SGMStructureFeature;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public interface SupplementalSGMStructureFeature
    extends SGMStructureFeature
{        
    public List<SGMSurfaceFeature> provideBaseSurfaceFeatures(
        final int sgmBaseLocationIndex,
        final List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation);

    public List<SGMSurfaceFeature> transformSurfaceFeatures(
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocation,
        final List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation);
}
