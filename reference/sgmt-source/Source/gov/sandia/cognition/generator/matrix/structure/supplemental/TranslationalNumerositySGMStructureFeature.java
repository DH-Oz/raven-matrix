/*
 * File:                TranslationalNumerositySGMStructureFeature.java
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
 * $Log: TranslationalNumerositySGMStructureFeature.java,v $
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
 * Revision 1.5  2008/10/29 22:53:59  cewarr
 * Fixed bug 1293, allowing scaling and numerosity to be combined, by 1) combining scaling factor numerosity uses with existing scale factor and 2) allowing repetition (scaling/rotation) to apply one surface feature from previous cell to multiple surface features in current cell.
 *
 * Revision 1.4  2008/10/15 17:49:03  zobenz
 * Made surface feature sizes more visually distinct.
 *
 * Revision 1.3  2007/12/17 15:23:31  zobenz
 * Fixed translational numerosity calculation of number of positions when the location transform is top left out.
 *
 * Revision 1.2  2007/12/14 17:21:55  zobenz
 * Added an initialNumerosity parameter
 *
 * Revision 1.1  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.1  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
 *
 * Revision 1.3  2007/12/11 17:35:32  zobenz
 * Improved numerosity to use consistent scaling and positioning across cells along location transform
 *
 * Revision 1.2  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.1  2007/12/10 23:39:50  zobenz
 * Added numerosity structure feature
 *
 */
 
package gov.sandia.cognition.generator.matrix.structure.supplemental;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.SGMMatrixSize;
import gov.sandia.cognition.generator.matrix.SGMPoint;
import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.locationtransform.TopLeftCornerOutSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.ArrayList;
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class TranslationalNumerositySGMStructureFeature
    extends AbstractSupplementalSGMStructureFeature
{
    public static final String DESCRIPTION = "Numerosity";
    private int sgmCellImagePixelSize;
    private int numPositions;
    private double positionStepSize;
    private double scaling;
    private int initialNumerosity;    
        
    public TranslationalNumerositySGMStructureFeature(
        final SGMLocationTransform locationTransform,
        final int sgmCellImagePixelSize,
        final SGMMatrixSize sgmMatrixSize,
        final int initialNumerosity)
    {
        super(locationTransform);
        
        this.setSGMCellImagePixelSize(sgmCellImagePixelSize);
        this.setInitialNumerosity(initialNumerosity);
        
        int maxDimension = sgmMatrixSize.getNumRows();
        if (sgmMatrixSize.getNumColumns() > sgmMatrixSize.getNumRows())
        {
            maxDimension = sgmMatrixSize.getNumColumns();
        }
        if (locationTransform instanceof TopLeftCornerOutSGMLocationTransform)
        {
            this.setNumPositions((int)Math.ceil(Math.sqrt(
                sgmMatrixSize.getNumRows() +
                sgmMatrixSize.getNumColumns() - 1)));
        }
        else
        {
            // Take into account initial numerosity when calculating num
            // positions
            this.setNumPositions((int)Math.ceil(Math.sqrt(maxDimension +
                (this.getInitialNumerosity() - 1))));
        }
        
        this.setPositionStepSize(
                ((double)this.getSGMCellImagePixelSize()) /
                ((double)(this.getNumPositions() + 1)));
        
        this.setScaling(0.75 / this.getNumPositions());                
    }
    
    @Override
    public List<SGMSurfaceFeature> provideBaseSurfaceFeatures(
        final int sgmBaseLocationIndex,
        final List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation)
    {
        if (existingSurfaceFeaturesAtLocation != null)
        {                                   
            List<SGMSurfaceFeature> transformedFeatures =
            new ArrayList<SGMSurfaceFeature>(this.getInitialNumerosity());

// TODO don't restrict to just first surface feature - instead preprocess
// surface features to combine into one surface feature that can then be
// repeated        
        
            // Create initialNumerosity multiples of the first surface feature
            // in existing surface features
            for (int i = 0; i < this.getInitialNumerosity(); i++)
            {
                transformedFeatures.add(existingSurfaceFeaturesAtLocation.
                    get(0).clone());
            }

            // Now layout the surface feature positions to be non-overlapping
            int columnPosition = 0;
            int rowPosition = 0;                            
            for (SGMSurfaceFeature feature : transformedFeatures)
            {
                feature.setScale(this.getScaling());
                feature.setPosition(new SGMPoint(
                    (columnPosition + 1) * this.getPositionStepSize(),
                    (rowPosition + 1) * this.getPositionStepSize()));

                columnPosition++;
                if (columnPosition >= getNumPositions())
                {
                    columnPosition = 0;
                    rowPosition++;
                }
            }                              

            return transformedFeatures;             
        }
        else
        {
            return null;
        }       
    }

    @Override
    public List<SGMSurfaceFeature> transformSurfaceFeatures(
        final List<SGMSurfaceFeature> surfaceFeaturesAtPreviousLocation,
        final List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation)
    {                
        List<SGMSurfaceFeature> transformedFeatures =
            new ArrayList<SGMSurfaceFeature>(
            surfaceFeaturesAtPreviousLocation.size() + 1);                                    

// TODO don't restrict to just first surface feature - instead preprocess
// surface features to combine into one surface feature that can then be
// repeated        
        
        // Create n + 1 multiples of the first surface feature in
        // existing surface features, where n is the number of surface
        // features at previous location
        for (int i = 0; i <= surfaceFeaturesAtPreviousLocation.size(); i++)
        {
            transformedFeatures.add(existingSurfaceFeaturesAtLocation.
                get(0).clone());
        }

        // Now layout the surface feature positions to be non-overlapping
        int columnPosition = 0;
        int rowPosition = 0;                            
        for (SGMSurfaceFeature feature : transformedFeatures)
        {
            feature.setScale(this.getScaling()*feature.getScale());
            feature.setPosition(new SGMPoint(
                (columnPosition + 1) * this.getPositionStepSize(),
                (rowPosition + 1) * this.getPositionStepSize()));

            columnPosition++;
            if (columnPosition >= getNumPositions())
            {
                columnPosition = 0;
                rowPosition++;
            }
        }                              

        return transformedFeatures; 
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

    private int getSGMCellImagePixelSize()
    {
        return sgmCellImagePixelSize;
    }

    private void setSGMCellImagePixelSize(int sgmCellImagePixelSize)
    {
        this.sgmCellImagePixelSize = sgmCellImagePixelSize;
    }

    private double getPositionStepSize()
    {
        return positionStepSize;
    }

    private void setPositionStepSize(double positionStepSize)
    {
        this.positionStepSize = positionStepSize;
    }

    private double getScaling()
    {
        return scaling;
    }

    private void setScaling(double scaling)
    {
        this.scaling = scaling;
    }

    private int getNumPositions()
    {
        return numPositions;
    }

    private void setNumPositions(int numPositions)
    {
        this.numPositions = numPositions;
    }

    private int getInitialNumerosity()
    {
        return initialNumerosity;
    }

    private void setInitialNumerosity(int initialNumerosity)
    {
        this.initialNumerosity = initialNumerosity;
    }

}
