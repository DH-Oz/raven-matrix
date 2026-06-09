/*
 * File:                DiagonalBottomLeftTopRightSGMLocationTransform.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 20, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: DiagonalBottomLeftTopRightSGMLocationTransform.java,v $
 * Revision 1.2  2010/12/21 16:10:58  zobenz
 * Normalized documentation to match tool name.
 *
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
 * Revision 1.7  2007/12/14 21:40:09  zobenz
 * Implemented TopLeftCornerOutSGMLocationTransform and associated infrastructure improvements
 *
 * Revision 1.6  2007/12/11 17:35:32  zobenz
 * Improved numerosity to use consistent scaling and positioning across cells along location transform
 *
 * Revision 1.5  2007/12/10 18:28:38  zobenz
 * Added "explain" feature to textually describe how a matrix was constructed
 *
 * Revision 1.4  2007/12/06 23:28:32  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.3  2007/12/03 20:03:14  zobenz
 * Fixed base location generation
 *
 * Revision 1.2  2007/11/21 18:01:07  zobenz
 * SGMLayer implementation completed
 *
 * Revision 1.1  2007/11/20 23:47:35  zobenz
 * Working on SGMLayer - specifically on creation of a layer from provided surface features, structure features, and location transform; it's not done yet.  Should have it finished tomorrow.
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
public class DiagonalBottomLeftTopRightSGMLocationTransform extends AbstractSGMLocationTransform
{
    public static final String DESCRIPTION = "Diagonal Bottom Left to Top Right";
    
    public DiagonalBottomLeftTopRightSGMLocationTransform(
        SGMMatrixSize sgmMatrixSize)
    {
        super(sgmMatrixSize);
                
        // Make sure sgmMatrixSize is square and has odd size
        if ((sgmMatrixSize.getNumRows() % 2 == 0) ||
            (sgmMatrixSize.getNumRows() != sgmMatrixSize.getNumColumns()))
        {
            throw new IllegalArgumentException("Diagonal Bottom Left to" +
                "Top Right Location Transform requires that the matrix be" +
                "a square with an odd number of rows and columns");
        }
    }
    
    @Override
    protected void populateBaseLocations()
    {
        this.setBaseLocations(new ArrayList<SGMLocation>());

        int row = 0;
        for (int column = 0; column <
            this.getSGMMatrixSize().getNumColumns(); column++)
        {
            this.getBaseLocations().add(new SGMLocation(row, column));
            row++;
        }        
    }

    @Override
    public SGMLocation createNextLocation(SGMLocation location)
    {
        int row = location.getRow() - 1;        
        if (row < 0)
        {
            row = this.getSGMMatrixSize().getNumRows() - 1;
        }

        int column = location.getColumn() + 1;        
        if (column >= this.getSGMMatrixSize().getNumColumns())
        {
            column = 0;
        }

        return new SGMLocation(row, column);
    }   
    
    @Override
    public SGMLocation getParentLocationForStructureFeatureUse(
        final SGMLocation location)
    {
        int row = location.getRow() + 1;
        if (row >= this.getSGMMatrixSize().getNumRows())
        {
            row = 0;
        }
        
        int column = location.getColumn() - 1;
        if (column < 0)
        {
            column = this.getSGMMatrixSize().getNumColumns() - 1;
        }
                
        return new SGMLocation(row, column);
    }
    
    public String getDescription()
    {
        return DESCRIPTION;
    }
}
