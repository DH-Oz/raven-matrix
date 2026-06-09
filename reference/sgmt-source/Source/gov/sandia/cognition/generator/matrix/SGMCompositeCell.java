/*
 * File:                SGMCompositeCell.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 21, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMCompositeCell.java,v $
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
 * Revision 1.1  2010/12/20 18:58:33  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:23  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.3  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.2  2007/12/10 19:56:04  zobenz
 * Filled in rest of answer choice generation by randomly manipulating parameters of surface features
 *
 * Revision 1.1  2007/11/21 22:28:30  zobenz
 * Implemented SGMMatrix, which is composed of layers; starting work on stochastic generation of SGMs to fit a specified score distribution
 *
 */
 
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMCompositeCell extends SGMBaseCell
{
    public SGMCompositeCell(SGMCell cell)
    {
        super(cell.getLocation(), 
            new ArrayList<SGMSurfaceFeature>(cell.getSurfaceFeatures()));
    }
    
    public SGMCompositeCell(
            SGMLocation location,
            List<SGMSurfaceFeature> surfaceFeatures)
    {
        super(location, surfaceFeatures);
    }
    
    public SGMCompositeCell(
            SGMLocation location,
            SGMSurfaceFeature... surfaceFeatures)
    {
        this(location, Arrays.asList(surfaceFeatures));
    }
}
