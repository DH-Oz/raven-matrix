/*
 * File:                SGMDerivedCell.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 1, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMDerivedCell.java,v $
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
 * Revision 1.5  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.4  2007/11/21 18:01:08  zobenz
 * SGMLayer implementation completed
 *
 * Revision 1.3  2007/11/13 22:58:55  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.2  2007/11/07 16:47:46  zobenz
 * Interim checkin; working on implementing SGM generation code.
 *
 * Revision 1.1  2007/11/01 22:57:55  zobenz
 * Initial stubs
 *
 */
 
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.Arrays;
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMDerivedCell extends SGMBaseCell
{   
    private SGMBaseCell baseCell;
    private SGMCell parentCell;
    
    public SGMDerivedCell(
            SGMLocation location,
            SGMBaseCell baseCell,
            SGMCell parentCell,
            List<SGMSurfaceFeature> surfaceFeatures)
    {
        super(location, surfaceFeatures);
        this.setBaseCell(baseCell);
        this.setParentCell(parentCell);                
        
    }
    
    public SGMDerivedCell(
            SGMLocation location,
            SGMBaseCell baseCell,
            SGMCell parentCell,
            SGMSurfaceFeature... surfaceFeatures)
    {
        this(location, baseCell, parentCell,
                Arrays.asList(surfaceFeatures));
        
    }    

    public SGMBaseCell getBaseCell()
    {
        return baseCell;
    }

    protected void setBaseCell(SGMBaseCell baseCell)
    {
        this.baseCell = baseCell;
    }


    public SGMCell getParentCell()
    {
        return parentCell;
    }

    protected void setParentCell(SGMCell parentCell)
    {
        this.parentCell = parentCell;
    }
}
