/*
 * File:                AbstractLogicOperationSGMStructureFeature.java
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
 * $Log: AbstractLogicOperationSGMStructureFeature.java,v $
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
 * Revision 1.1  2007/12/13 18:19:40  zobenz
 * Implemented infrastructure for logic operation structure features and implemented Logical OR
 *
 */
 
package gov.sandia.cognition.generator.matrix.structure.base;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public abstract class AbstractLogicOperationSGMStructureFeature
    extends AbstractBaseSGMStructureFeature
{
    private List<SGMSurfaceFeature> baseSurfaceFeatures;
    private Map<Integer, List<SGMSurfaceFeature>>
        baseSurfaceFeatureBaseLocationAssignments;
    
    public AbstractLogicOperationSGMStructureFeature(
        final SGMLocationTransform locationTransform,
        final List<SGMSurfaceFeature> baseSurfaceFeatures,
        final Random random)
    {
        super(locationTransform);
        this.setBaseSurfaceFeatures(baseSurfaceFeatures);
        
        // Randomly assign base surface features to base locations such that
        // all base surface features are used at least once
        int numBaseFeatures = this.getBaseSurfaceFeatures().size();
        int numBaseLocations = locationTransform.getBaseLocations().size();        
        Map<Integer, Boolean> assignedSurfaceFeatures = 
            new HashMap<Integer, Boolean>(numBaseFeatures);
        Map<Integer, Boolean> populatedBaseLocationIndices =
            new HashMap<Integer, Boolean>(numBaseLocations);
        this.setBaseSurfaceFeatureBaseLocationAssignments(
            new HashMap<Integer, List<SGMSurfaceFeature>>(numBaseLocations));
        boolean done = false;
        while (!done)
        {
            // Add base surface features to each base location index
            for (int baseLocationIndex = 0; 
                baseLocationIndex < numBaseLocations; baseLocationIndex++)
            {
                // Stochastically determine how many features to add to this
                // base location index (note, allowed to add zero)
                int numFeatures = random.nextInt(numBaseFeatures + 1);
                for (int i = 0; i < numFeatures; i++)
                {
                    // Stochastically pick a surface feature to add
                    int featureIndex = random.nextInt(numBaseFeatures);
                    
                    // Add the feature to the current base location index
                    if (this.getBaseSurfaceFeatureBaseLocationAssignments().
                        containsKey(baseLocationIndex))
                    {
                        if (!this.getBaseSurfaceFeatureBaseLocationAssignments().
                        get(baseLocationIndex).contains(featureIndex))
                        {
                            this.getBaseSurfaceFeatureBaseLocationAssignments().
                                get(baseLocationIndex).add(this.
                                getBaseSurfaceFeatures().get(featureIndex));

                            // Update populated location index tracking
                            if (!populatedBaseLocationIndices.
                                containsKey(baseLocationIndex))
                            {
                                populatedBaseLocationIndices.
                                    put(baseLocationIndex, true);
                            }
                            
                            // Update assigned surface feature tracking
                            if (!assignedSurfaceFeatures.
                                containsKey(featureIndex))
                            {
                                assignedSurfaceFeatures.put(featureIndex, true);
                            }
                        }
                    }
                    else
                    {
                        List<SGMSurfaceFeature> featureIndices =
                            new ArrayList<SGMSurfaceFeature>(1);
                        featureIndices.add(this.
                            getBaseSurfaceFeatures().get(featureIndex));
                        this.getBaseSurfaceFeatureBaseLocationAssignments().
                            put(baseLocationIndex, featureIndices);
                        
                        // Update populated location index tracking
                        if (!populatedBaseLocationIndices.
                            containsKey(baseLocationIndex))
                        {
                            populatedBaseLocationIndices.
                                put(baseLocationIndex, true);
                        }
                        
                        // Update assigned surface feature tracking
                        if (!assignedSurfaceFeatures.
                            containsKey(featureIndex))
                        {
                            assignedSurfaceFeatures.put(featureIndex, true);
                        }
                    }
                }
            }
            
            // Check to see if done
            if ((assignedSurfaceFeatures.size() >= numBaseFeatures) &&
                (populatedBaseLocationIndices.size() >= numBaseLocations))
            {
                done = true;
            }
        }
    }
    
    @Override
    public List<SGMSurfaceFeature> provideBaseSurfaceFeatures(
        final int sgmBaseLocationIndex)
    {
        // Return surface features for the specified base location index        
        return this.getBaseSurfaceFeatureBaseLocationAssignments().
           get(sgmBaseLocationIndex);
    }

    @Override
    public List<SGMSurfaceFeature> transformSurfaceFeatures(
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocation)
    {
        throw new UnsupportedOperationException("Logic operation " +
            "structure features are a special case that perform their" +
            "transform based on two previous locations, so this function" +
            "is never used");
    }
    
    public abstract List<SGMSurfaceFeature> transformSurfaceFeatures(
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocationOne,
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocationTwo);
    
    public abstract String getDescription();

    @Override
    public boolean checkCompatibility(
        final SGMFeature feature)
    {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    private List<SGMSurfaceFeature> getBaseSurfaceFeatures()
    {
        return baseSurfaceFeatures;
    }

    private void setBaseSurfaceFeatures(
        final List<SGMSurfaceFeature> baseSurfaceFeatures)
    {
        this.baseSurfaceFeatures = baseSurfaceFeatures;
    }

    private Map<Integer, List<SGMSurfaceFeature>> getBaseSurfaceFeatureBaseLocationAssignments()
    {
        return baseSurfaceFeatureBaseLocationAssignments;
    }

    private void setBaseSurfaceFeatureBaseLocationAssignments(
        final Map<Integer, List<SGMSurfaceFeature>> baseSurfaceFeatureBaseLocationAssignments)
    {
        this.baseSurfaceFeatureBaseLocationAssignments = baseSurfaceFeatureBaseLocationAssignments;
    }
}
