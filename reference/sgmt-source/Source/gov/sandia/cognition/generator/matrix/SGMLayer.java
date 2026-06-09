/*
 * File:                SGMLayer.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 7, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMLayer.java,v $
 * Revision 1.3  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:06  zobenz
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
 * Revision 1.22  2008/01/25 21:16:15  zobenz
 * Added infrastructure and method for evaluating SGMScore of a matrix given a SGMMatrixDifficulty Classifier
 *
 * Revision 1.21  2007/12/14 21:40:09  zobenz
 * Implemented TopLeftCornerOutSGMLocationTransform and associated infrastructure improvements
 *
 * Revision 1.20  2007/12/14 17:21:55  zobenz
 * Added an initialNumerosity parameter
 *
 * Revision 1.19  2007/12/14 16:25:49  zobenz
 * Added sanity checking on structureFeatures argument to constructor
 *
 * Revision 1.18  2007/12/13 18:19:40  zobenz
 * Implemented infrastructure for logic operation structure features and implemented Logical OR
 *
 * Revision 1.17  2007/12/13 15:54:54  zobenz
 * Divided up base and supplemental structure features into their own packages
 *
 * Revision 1.16  2007/12/13 15:50:17  zobenz
 * Made the distinction between base structure features and supplemental structure features explicit in preparation for implementing logical operation base structure features
 *
 * Revision 1.15  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.14  2007/12/10 18:28:38  zobenz
 * Added "explain" feature to textually describe how a matrix was constructed
 *
 * Revision 1.13  2007/12/07 00:00:52  zobenz
 * Removed some debug statements; disabled rotate structure feature again for the time being
 *
 * Revision 1.12  2007/12/06 23:28:33  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.11  2007/12/05 23:55:28  zobenz
 * Fixed Rotate structure feature (but still disabled in matrix generation for now); implemented Scale structure feature
 *
 * Revision 1.10  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 * Revision 1.9  2007/11/21 22:28:30  zobenz
 * Implemented SGMMatrix, which is composed of layers; starting work on stochastic generation of SGMs to fit a specified score distribution
 *
 * Revision 1.8  2007/11/21 18:01:07  zobenz
 * SGMLayer implementation completed
 *
 * Revision 1.7  2007/11/20 23:47:34  zobenz
 * Working on SGMLayer - specifically on creation of a layer from provided surface features, structure features, and baseLocation transform; it's not done yet.  Should have it finished tomorrow.
 *
 * Revision 1.6  2007/11/19 23:41:55  zobenz
 * Working implementation of SetIterationSGMFeature
 *
 * Revision 1.5  2007/11/19 22:59:30  zobenz
 * Promoted SGMCellImage up out of .ui sub package, as it is more general and not specific to UI.
 *
 * Revision 1.4  2007/11/19 22:56:42  zobenz
 * Added ability to get rasterized version of SGM cell image
 *
 * Revision 1.3  2007/11/13 22:58:55  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.2  2007/11/13 20:28:12  zobenz
 * Fixed painting colors; fixed line surface feature; updated proof of concept code
 *
 * Revision 1.1  2007/11/12 23:20:39  zobenz
 * Working on being able to render matrices to screen and to bitmap
 *
 */
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.locationtransform.SGMLocationTransform;
import gov.sandia.cognition.generator.matrix.structure.base.BaseSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.SGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.base.AbstractLogicOperationSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.structure.supplemental.SupplementalSGMStructureFeature;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import gov.sandia.cognition.util.CloneableSerializable;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMLayer extends AbstractSGMMatrix
{

    private List<SGMStructureFeature> structureFeatures;
    
    private Set<SGMSurfaceFeature> baseSurfaceFeatures;

    public SGMLayer(
        final SGMMatrixSize sgmMatrixSize,
        final List<SGMStructureFeature> structureFeatures)
    {
        // Store settings
        this.setSGMMatrixSize(sgmMatrixSize);
        this.setStructureFeatures(structureFeatures);

        // Construct cell storage
        this.setSGMCells(
            new SGMCell[this.getSGMMatrixSize().getNumRows()][this.getSGMMatrixSize().getNumColumns()]);
        
        if (structureFeatures.size() == 0)            
        {
            throw new IllegalArgumentException("SGMLayer: must provide at " +
                "least one structure feature, which must be a " +
                "BaseSGMStructureFeature");
        }
        if (!(structureFeatures.get(0) instanceof BaseSGMStructureFeature))
        {
            throw new IllegalArgumentException("SGMLayer: first structure " +
                "feature must be a BaseSGMStructureFeature");
        }
        for (int i = 1; i < structureFeatures.size(); i++)
        {
            if (!(structureFeatures.get(i) instanceof 
                SupplementalSGMStructureFeature))
            {
                throw new IllegalArgumentException("SGMLayer: structure " +
                    "features subsequent to the first one must be " +
                    "SupplementalSGMStructureFeatures");
            }
        }                        
        
        // Construct base surface features storage
        this.setBaseSurfaceFeatures(new HashSet<SGMSurfaceFeature>());

        // Now apply each of the structure features in turn
        for (SGMStructureFeature structureFeature : structureFeatures)
        {         
            SGMLocationTransform locationTransform =
                structureFeature.getLocationTransform();
            
            if (structureFeature instanceof 
                AbstractLogicOperationSGMStructureFeature)
            {
                // Handle logic operation structure features specially
                // Set up base locations
                int baseLocationIndex = 0;
                for (SGMLocation baseLocation :
                    locationTransform.getBaseLocations())
                {
                    SGMBaseCell baseCell = new SGMBaseCell(baseLocation,
                            ((BaseSGMStructureFeature)structureFeature).
                            provideBaseSurfaceFeatures(baseLocationIndex));
                        
                    this.getSGMCells()[baseLocation.getRow()][baseLocation.
                        getColumn()] = baseCell;
                    
                    // Keep track of unique base surface features in the
                    // layer
                    for (SGMSurfaceFeature feature :
                        baseCell.getSurfaceFeatures())
                    {
                        this.getBaseSurfaceFeatures().add(feature);
                    }
                    
                    // Increment base location index
                    baseLocationIndex++;
                }
                    
                // Generate derived cells by starting in third row and moving
                // diagonally up and to the right                                                                
                for (int row = 0; row < sgmMatrixSize.getNumRows(); row++)
                {
                    for (int column = 0; 
                        column < sgmMatrixSize.getNumColumns(); column++)
                    {
                        if (this.getSGMCells()[row][column] == null)
                        {
                            SGMCell previousCellOne = null;
                            SGMCell previousCellTwo = null;
                            // Figure out what the two previous cells are
                            if (row > 1)
                            {
                                // Previous two cells are immediately to the
                                // left of us
                                previousCellOne = 
                                    this.getSGMCells()[row - 2][column];
                                previousCellTwo = 
                                    this.getSGMCells()[row - 1][column];
                            }
                            else
                            {
                                // Previous two cells are immediately above us
                                previousCellOne = 
                                    this.getSGMCells()[row][column - 2];
                                previousCellTwo = 
                                    this.getSGMCells()[row][column - 1];
                            }
                            this.getSGMCells()[row][column] =
                                new SGMBaseCell(
                                new SGMLocation(row, column),
                                ((AbstractLogicOperationSGMStructureFeature)
                                structureFeature).transformSurfaceFeatures(
                                previousCellOne.getSurfaceFeatures(),
                                previousCellTwo.getSurfaceFeatures()));                            
                        }
                    }
                }
            }
            else
            {

                int baseLocationIndex = 0;
                for (SGMLocation baseLocation :
                    locationTransform.getBaseLocations())
                {                        
                    // Populate base cell at the current baseLocation
                    List<SGMSurfaceFeature> existingSurfaceFeaturesAtLocation =
                        null;
                    SGMCell currentCell =
                        this.getSGMCells()[baseLocation.getRow()][baseLocation.
                        getColumn()];
                    if (currentCell != null)
                    {
                        existingSurfaceFeaturesAtLocation =
                            currentCell.getSurfaceFeatures();
                    }
                    SGMBaseCell baseCell = null;
                    if (structureFeature instanceof BaseSGMStructureFeature)
                    {
                        // Base structure feature                    
                        baseCell = new SGMBaseCell(baseLocation,
                            ((BaseSGMStructureFeature)structureFeature).
                            provideBaseSurfaceFeatures(baseLocationIndex));  
         
                        // Keep track of unique base surface features in the
                        // layer
                        for (SGMSurfaceFeature feature :
                            baseCell.getSurfaceFeatures())
                        {
                            this.getBaseSurfaceFeatures().add(feature);
                        }
                    }
                    else
                    {
                        // Supplemental structure feature
                        baseCell = new SGMBaseCell(baseLocation,
                            ((SupplementalSGMStructureFeature)structureFeature).
                            provideBaseSurfaceFeatures(baseLocationIndex,
                            existingSurfaceFeaturesAtLocation));
                        
                        // Surface features here are _not_ base surface
                        // features - those can only be created by a
                        // base structure feature
                    }
                    this.getSGMCells()[baseLocation.getRow()][baseLocation.
                        getColumn()] =
                        baseCell;

                    // Generate derived cells
                    SGMCell parentCell = null;
                    SGMLocation currentLocation = locationTransform.
                        createNextLocation(baseLocation);
                    while (!currentLocation.equals(baseLocation))
                    {
                        // Get existing surface features at this location
                        existingSurfaceFeaturesAtLocation = null;
                        currentCell =
                            this.getSGMCells()[currentLocation.getRow()]
                            [currentLocation.getColumn()];
                        if (currentCell != null)
                        {
                            existingSurfaceFeaturesAtLocation =
                                currentCell.getSurfaceFeatures();
                        }
                        
                        // Determine parent cell for this location (NOTE: it
                        // is _NOT_ necessarily the previous location we were
                        // at)
                        SGMLocation parentCellLocation = locationTransform.
                            getParentLocationForStructureFeatureUse(
                            currentLocation);
                        parentCell = this.getSGMCells()
                            [parentCellLocation.getRow()]
                            [parentCellLocation.getColumn()];
                        
                        // Create the derived cell and place it in the layer
                        SGMDerivedCell derivedCell = null;
                        if (structureFeature instanceof BaseSGMStructureFeature)
                        {
                            // Base structure feature
                            derivedCell = new SGMDerivedCell(currentLocation,
                                baseCell, parentCell,
                                ((BaseSGMStructureFeature)structureFeature).
                                transformSurfaceFeatures(
                                parentCell.getSurfaceFeatures()));
                        }
                        else
                        {
                            // Supplemental structure feature
                            derivedCell = new SGMDerivedCell(currentLocation,
                                baseCell, parentCell,
                                ((SupplementalSGMStructureFeature)structureFeature).
                                transformSurfaceFeatures(
                                parentCell.getSurfaceFeatures(),
                                existingSurfaceFeaturesAtLocation));
                        }

                        this.getSGMCells()[currentLocation.getRow()]
                            [currentLocation.getColumn()] = derivedCell;

                        // Move to next location using transform
                        currentLocation = locationTransform.
                            createNextLocation(currentLocation);
                    }

                    // Update base surface feature baseLocation index
                    // for next iteration of loop
                    baseLocationIndex++;
                }
            }
        }
    }

    public List<SGMStructureFeature> getStructureFeatures()
    {
        return structureFeatures;
    }

    protected void setStructureFeatures(
        final List<SGMStructureFeature> structureFeatures)
    {
        this.structureFeatures = structureFeatures;
    }

    public CloneableSerializable clone()
    {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    public Set<SGMSurfaceFeature> getBaseSurfaceFeatures()
    {
        return baseSurfaceFeatures;
    }

    private void setBaseSurfaceFeatures(
        final Set<SGMSurfaceFeature> baseSurfaceFeatures)
    {
        this.baseSurfaceFeatures = baseSurfaceFeatures;
    }
}
