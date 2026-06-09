/*
 * File:                TopLeftCornerOutSGMLocationTransform.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 14, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: TopLeftCornerOutSGMLocationTransform.java,v $
 * Revision 1.1  2010/12/21 15:50:07  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:20:55  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:38  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:27  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.1  2007/12/14 21:40:09  zobenz
 * Implemented TopLeftCornerOutSGMLocationTransform and associated infrastructure improvements
 *
 */
 
package gov.sandia.cognition.generator.matrix.locationtransform;

import gov.sandia.cognition.generator.matrix.SGMLocation;
import gov.sandia.cognition.generator.matrix.SGMMatrixSize;
import java.util.ArrayList;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class TopLeftCornerOutSGMLocationTransform
    extends AbstractSGMLocationTransform
{
    public static final String DESCRIPTION = "Top Left Corner Out";
    
    public TopLeftCornerOutSGMLocationTransform(
        final SGMMatrixSize sgmMatrixSize)
    {
        super(sgmMatrixSize);
    }
    
    @Override
    protected void populateBaseLocations()
    {
        // Only one base location - the top left corner
        this.setBaseLocations(new ArrayList<SGMLocation>());
        this.getBaseLocations().add(new SGMLocation(0, 0));
    }

    @Override
    public SGMLocation createNextLocation(SGMLocation location)
    {
        // To move outward from the top left corner we wrap around diagnonally
        // moving up and to the right
        int row;
        int column;
        if ((location.getRow() == this.getSGMMatrixSize().getNumRows() - 1) &&
            (location.getColumn() == 
            this.getSGMMatrixSize().getNumColumns() - 1))
        {
            // In bottom right corner
            row = 0;
            column = 0;
        }
        else if (this.getSGMMatrixSize().getNumRows() >
            this.getSGMMatrixSize().getNumColumns())
        {            
            // More rows than columns
            if (location.getRow() == 0)
            {
                // Anywhere in first row
                row = location.getColumn() + 1;
                column = 0;
            }
            else
            {
                if (location.getColumn() < 
                    (this.getSGMMatrixSize().getNumColumns() - 1))
                {
                    // Not in first row or last column
                    row = location.getRow() - 1;
                    column = location.getColumn() + 1;
                }
                else
                {
                    // Anywhere in last column except first row
                    row = location.getRow() +
                        this.getSGMMatrixSize().getNumColumns();
                    if (row >= this.getSGMMatrixSize().getNumRows())
                    {
                        row = this.getSGMMatrixSize().getNumRows() - 1;
                        column = location.getColumn() - 
                            (this.getSGMMatrixSize().getNumRows() -
                            location.getRow() - 2);
                    }
                    else
                    {
                        column = 0;
                    }
                }
            }
        }
        else
        {
            // More columns than rows, or square matrix
            if ((location.getRow() > 0) && (location.getColumn() < 
                this.getSGMMatrixSize().getNumColumns() - 1))
            {
                // Not in first row or last column                
                row = location.getRow() - 1;
                column = location.getColumn() + 1;
            }
            else
            {
                if (location.getColumn() == 
                    this.getSGMMatrixSize().getNumColumns() - 1)
                {
                    // Anywhere in last column
                    row = this.getSGMMatrixSize().getNumRows() - 1;
                    column = location.getColumn() - 
                        (this.getSGMMatrixSize().getNumRows() -
                        location.getRow() - 2);
                }
                else 
                {
                    // Anywhere in first row except for last column
                    row = location.getColumn() + 1;
                    if (row >= this.getSGMMatrixSize().getNumRows())
                    {
                        row = this.getSGMMatrixSize().getNumRows() - 1;
                        column = location.getColumn() - 
                            (this.getSGMMatrixSize().getNumRows() - 2);
                    }
                    else
                    {
                        column = 0;
                    }
                }
            }
        }               
        
        return new SGMLocation(row, column);
    }
    
    @Override
    public SGMLocation getParentLocationForStructureFeatureUse(
        final SGMLocation location)
    {
        // If the location is the base location (top left corner), there
        // is no parent
        if ((location.getRow() == 0) && (location.getColumn() == 0))
        {
            throw new IllegalArgumentException(
                "TopLeftCornerOutSGMLocationTransform: can't get a parent" +
                "location for the base location (i.e. for the top left corner");
        }
        
        // Parent location is one above current location, unless there
        // are none above, in which case it is the one to the left of the
        // current location        
        if (location.getRow() > 0)
        {
            int row = location.getRow() - 1;
            return new SGMLocation(row, location.getColumn());
        }
        else
        {
            int column = location.getColumn() - 1;
            return new SGMLocation(location.getRow(), column);
        }
    }

    @Override
    public String getDescription()
    {
       return DESCRIPTION;
    }

}
