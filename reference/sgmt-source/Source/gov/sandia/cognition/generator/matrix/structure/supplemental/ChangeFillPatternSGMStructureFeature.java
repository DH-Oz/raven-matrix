/*
 * File:                ChangeFillPatternSGMStructureFeature.java
 * Authors:             Christina Warrender
 * Company:             Sandia National Laboratories
 * Project:             Cognitive Foundry
 * 
 * Copyright October 29, 2008, Sandia Corporation.
 * Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive 
 * license for use of this work by or on behalf of the U.S. Government. Export 
 * of this program may require a license from the United States Government. 
 * See CopyrightHistory.txt for complete details.
 * 
 * Revision History:
 * 
 * $Log: ChangeFillPatternSGMStructureFeature.java,v $
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
 * Revision 1.1  2008/11/03 18:50:43  cewarr
 * Added ability to rotate through fill patterns, and two more grey levels so there are 5 fill patterns total.  (bug 1273)
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
 * @TODO    Document this.
 * 
 * @author  Christina Warrender
 * @since   2.1
 */
public class ChangeFillPatternSGMStructureFeature
    extends AbstractRepetitionSGMStructureFeature
{
    private List<SGMFillPattern> baseFillPatterns;
    public static final String DESCRIPTION = "Change Fill Pattern";

    public ChangeFillPatternSGMStructureFeature(
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
                
                // Overwrite fill pattern with the appropriate one -
                // in this case, all base locations get same fill pattern.
                transformedFeature.setFillPattern(this.getBaseFillPatterns().
                    get(0));
                
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
        int fillIndex = (this.getBaseFillPatterns().
                indexOf(previousLocationFeature.getFillPattern()) + 1) %
                this.getBaseFillPatterns().size();
        feature.setFillPattern(this.getBaseFillPatterns().get(fillIndex));
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
