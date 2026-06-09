/*
 * File:                AbstractSGMMatrix.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 4, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: AbstractSGMMatrix.java,v $
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:05  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:04  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:33  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:23  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.4  2008/03/03 21:07:05  zobenz
 * Updated AnalogyModel to store settings for how to draw a SGM, and added evaluate method to allow you to easily pass in an SGM and have it be fed to the model.
 *
 * Revision 1.3  2008/01/25 22:30:20  zobenz
 * SGMScore now determined during generation of set of SGM matrices using a provided difficulty classifer
 *
 * Revision 1.2  2007/12/06 23:28:33  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.1  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 */
 
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.util.CloneableSerializable;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public abstract class AbstractSGMMatrix
{
    private SGMMatrixSize sgmMatrixSize;
    private SGMCell[][] sgmCells;
            
    public SGMMatrixSize getSGMMatrixSize()
    {
        return this.sgmMatrixSize;
    }

    protected void setSGMMatrixSize(
        final SGMMatrixSize sgmMatrixSize)
    {
        this.sgmMatrixSize = sgmMatrixSize;
    }
    
    public SGMCell[][] getSGMCells()
    {
        return this.sgmCells;
    }
    
    protected void setSGMCells(
        final SGMCell[][] sgmCells)
    {
        this.sgmCells = sgmCells;
    }

    @Override
    public abstract CloneableSerializable clone();
}
