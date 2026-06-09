/*
 * File:                SGMCell.java
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
 * $Log: SGMCell.java,v $
 * Revision 1.3  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:05  zobenz
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
 * Revision 1.8  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.7  2007/11/21 22:28:30  zobenz
 * Implemented SGMMatrix, which is composed of layers; starting work on stochastic generation of SGMs to fit a specified score distribution
 *
 * Revision 1.6  2007/11/21 18:01:08  zobenz
 * SGMLayer implementation completed
 *
 * Revision 1.5  2007/11/13 22:58:55  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.4  2007/11/13 20:28:12  zobenz
 * Fixed painting colors; fixed line surface feature; updated proof of concept code
 *
 * Revision 1.3  2007/11/07 17:35:35  zobenz
 * Refactoring class names to be consistent across project.
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
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public interface SGMCell
{
    public SGMLocation getLocation();
    
    public List<SGMSurfaceFeature> getSurfaceFeatures();
    
    public SGMCompositeCell combineWith(SGMCell other)
        throws SGMLocationMismatchException;
}
