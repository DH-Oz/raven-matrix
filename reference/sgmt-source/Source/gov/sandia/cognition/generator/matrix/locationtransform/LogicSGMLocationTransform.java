/*
 * File:                LogicSGMLocationTransform.java
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
 * $Log: LogicSGMLocationTransform.java,v $
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
 * Revision 1.2  2007/12/14 21:40:09  zobenz
 * Implemented TopLeftCornerOutSGMLocationTransform and associated infrastructure improvements
 *
 * Revision 1.1  2007/12/13 18:19:40  zobenz
 * Implemented infrastructure for logic operation structure features and implemented Logical OR
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
public class LogicSGMLocationTransform
    extends AbstractSGMLocationTransform
{
    public static final String DESCRIPTION = "Logic";
    
    public LogicSGMLocationTransform(
        SGMMatrixSize sgmMatrixSize)
    {
        // Matrix must be at least 3x3 for logic operation structure features
        super(sgmMatrixSize);
        
        if (this.getSGMMatrixSize().getNumRows() < 3 ||
            this.getSGMMatrixSize().getNumColumns() < 3)
        {
            throw new IllegalArgumentException("SGMMatrixSize must" +
                "be at least 3x3 for LogicSGMLocationTransform");
        }
    }
    
    @Override
    protected void populateBaseLocations()
    {
        // The top left four cells define the starting point for a
        // logic operation structure feature     
        this.setBaseLocations(new ArrayList<SGMLocation>());
        this.getBaseLocations().add(new SGMLocation(0, 0));
        this.getBaseLocations().add(new SGMLocation(0, 1));
        this.getBaseLocations().add(new SGMLocation(1, 0));
        this.getBaseLocations().add(new SGMLocation(1, 1));
    }

    @Override
    public SGMLocation createNextLocation(SGMLocation location)
    {
        throw new UnsupportedOperationException("Logic operation structure " +
            "features are a special case that don't use the location " +
            "transform to determine the next location");
    }

    @Override
    public SGMLocation getParentLocationForStructureFeatureUse(
        final SGMLocation location)
    {
        throw new UnsupportedOperationException("Logic operation structure " +
            "features are a special case that don't use the location " +
            "transform to determine the prior location");
    }
    
    

    @Override
    public String getDescription()
    {
        return DESCRIPTION;
    }

}
