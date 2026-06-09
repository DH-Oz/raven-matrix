/*
 * File:                Dimension.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 6, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMLocation.java,v $
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:05  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:03  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:33  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:23  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.4  2007/11/30 16:27:52  zobenz
 * Implemented missing hashCode functions; Implemented SGMScore and SGMScoreDistribution
 *
 * Revision 1.3  2007/11/20 23:47:34  zobenz
 * Working on SGMLayer - specifically on creation of a layer from provided surface features, structure features, and location transform; it's not done yet.  Should have it finished tomorrow.
 *
 * Revision 1.2  2007/11/13 20:28:12  zobenz
 * Fixed painting colors; fixed line surface feature; updated proof of concept code
 *
 * Revision 1.1  2007/11/07 17:35:34  zobenz
 * Refactoring class names to be consistent across project.
 *
 * Revision 1.1  2007/11/07 16:47:46  zobenz
 * Interim checkin; working on implementing SGM generation code.
 *
 */
 
package gov.sandia.cognition.generator.matrix;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMLocation
{
    private int row;
    private int column;
    
    public SGMLocation(int row, int column)
    {
        this.setRow(row);
        this.setColumn(column);
    }

    public int getRow()
    {
        return row;
    }

    protected void setRow(int row)
    {
        this.row = row;
    }

    public int getColumn()
    {
        return column;
    }

    protected void setColumn(int column)
    {
        this.column = column;
    }

    @Override
    public boolean equals(Object other)
    {
        if ((other == null) || !(other instanceof SGMLocation))
        {
            return false;
        }
        else
        {
            return equals((SGMLocation)other);
        }        
    }

    @Override
    public int hashCode()
    {
        int hash = 3;
        hash = 11 * hash + this.row;
        hash = 11 * hash + this.column;
        return hash;
    }
    
    public boolean equals(SGMLocation other)
    {
        if ((other.getRow() == this.getRow()) &&
            (other.getColumn() == this.getColumn()))
        {
            return true;
        }
        else
        {
            return false;
        }
    }       
}
