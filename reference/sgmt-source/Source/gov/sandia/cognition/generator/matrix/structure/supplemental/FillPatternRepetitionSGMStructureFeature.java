/*
 * File:                FillPatternSGMStructureFeature.java
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
 * $Log: FillPatternRepetitionSGMStructureFeature.java,v $
 * Revision 1.2  2010/12/21 16:10:58  zobenz
 * Normalized documentation to match tool name.
 *
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
 * Revision 1.5  2007/12/11 15:06:45  zobenz
 * Fixed bug in generation of base surface features that was causing side effect of manipulating fill pattern of prior base surface features.
 *
 * Revision 1.4  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.3  2007/12/10 18:55:41  zobenz
 * Fixed surface feature equals check to take into account fill pattern (except when comparing lines, as fill pattern is irrelevant for them)
 *
 * Revision 1.2  2007/12/07 00:24:40  zobenz
 * Added fill pattern repetition structure feature
 *
 * Revision 1.1  2007/12/06 23:28:32  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.1  2007/12/06 19:04:41  zobenz
 * Committing working implementation in preparation for overhauling way in which structure features are applied
 *
 */
package gov.sandia.cognition.generator.matrix.structure.supplemental;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
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
public class FillPatternRepetitionSGMStructureFeature
    extends AbstractRepetitionSGMStructureFeature
{
    private List<SGMFillPattern> baseFillPatterns;
    public static final String DESCRIPTION = "Fill Pattern Repetition";

    public FillPatternRepetitionSGMStructureFeature(
        final SGMLocationTransform locationTransform,
        final List<SGMFillPattern> baseFillPatterns)
    {
        super(locationTransform);
        this.setBaseFillPatterns(baseFillPatterns);
    }

    @Override
    public List<SGMSurfaceFeature> provideBaseSurfaceFeatures(
        final int sgmBaseLocationIndex,
        final List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation)
    {       
        if (existingSurfaceFeaturesAtLocation != null)
        {
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
                
                // Overwrite fill pattern with the appropriate one for this
                // base location
                transformedFeature.setFillPattern(this.getBaseFillPatterns().
                    get(sgmBaseLocationIndex % this.getBaseFillPatterns().
                    size()));
                
                transformedFeatures.add(transformedFeature);
            }
            
            return transformedFeatures;
        }
        else
        {
            return null;
        } 
    }
    
    @Override
    protected SGMSurfaceFeature applyTransform(SGMSurfaceFeature feature,
        SGMSurfaceFeature previousLocationFeature)
    {
        // Apply fill pattern to the feature
        feature.setFillPattern(previousLocationFeature.getFillPattern());
        return feature;
    }

    @Override
    public String getDescription()
    {
        return DESCRIPTION;
    }

    @Override
    public boolean checkCompatibility(SGMFeature feature)
    {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    private List<SGMFillPattern> getBaseFillPatterns()
    {
        return baseFillPatterns;
    }

    private void setBaseFillPatterns(List<SGMFillPattern> baseFillPatterns)
    {
        this.baseFillPatterns = baseFillPatterns;
    }
}
