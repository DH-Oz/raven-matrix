/*
 * File:                ApplyScalingSGMStructureFeature.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 5, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: ApplyScalingSGMStructureFeature.java,v $
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
 * Revision 1.1  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.1  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
 *
 * Revision 1.2  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.1  2007/12/06 23:28:32  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.1  2007/12/05 23:55:28  zobenz
 * Fixed Rotate structure feature (but still disabled in matrix generation for now); implemented Scale structure feature
 *
 */
package gov.sandia.cognition.generator.matrix.structure.supplemental;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class ApplyScalingSGMStructureFeature
    extends AbstractRepetitionSGMStructureFeature
{
    public static final String DESCRIPTION = "Scaling Repetition";
    private double scaleAmount;

    public ApplyScalingSGMStructureFeature(
        final SGMLocationTransform locationTransform,
        final double scaleAmount)
    {
        super(locationTransform);
        this.setScaleAmount(scaleAmount);
    }

    public String getDescription()
    {
        return DESCRIPTION;
    }
        
    protected SGMSurfaceFeature applyTransform(
        final SGMSurfaceFeature feature,
        final SGMSurfaceFeature previousLocationFeature)
    { 
        // Apply scaling to the feature
        feature.setScale(scaleAmount * previousLocationFeature.getScale());
        return feature;
    }

    public boolean checkCompatibility(
        final SGMFeature feature)
    {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    private double getScaleAmount()
    {
        return scaleAmount;
    }

    private void setScaleAmount(
        final double scaleAmount)
    {
        this.scaleAmount = scaleAmount;
    }
}
