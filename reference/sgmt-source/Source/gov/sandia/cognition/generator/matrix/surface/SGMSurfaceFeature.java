/*
 * File:                SGMSurfaceFeature.java
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
 * $Log: SGMSurfaceFeature.java,v $
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:06  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:00  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:31  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:26  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.2  2007/12/10 20:11:07  zobenz
 * Fixed imports
 *
 * Revision 1.1  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.7  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.6  2007/12/05 20:44:55  zobenz
 * Improved answer choice generation; Replaced SetIteration structure feature with Identity structure feature; added Rotate structure feature (which has a bug right now)
 *
 * Revision 1.5  2007/12/04 00:03:40  zobenz
 * Implemented fill pattern attribute of surface features.
 *
 * Revision 1.4  2007/12/03 23:09:21  zobenz
 * Initial implementation of a complete top to bottom stochastic generation of SGMs
 *
 * Revision 1.3  2007/11/13 22:58:55  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.2  2007/11/07 17:36:22  zobenz
 * Refactoring class names to be consistent across project.
 *
 * Revision 1.1  2007/11/07 17:35:35  zobenz
 * Refactoring class names to be consistent across project.
 *
 * Revision 1.2  2007/11/07 16:47:46  zobenz
 * Interim checkin; working on implementing SGM generation code.
 *
 * Revision 1.1  2007/11/01 22:57:54  zobenz
 * Initial stubs
 *
 */
 
package gov.sandia.cognition.generator.matrix.surface;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.SGMPoint;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.util.CloneableSerializable;
import java.awt.Shape;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public interface SGMSurfaceFeature
        extends SGMFeature, CloneableSerializable
{    
    public double getScale();
    
    public void setScale(
        final double scale);
    
    public int getRotation();
    
    public void setRotation(
        final int rotation);
    
    public SGMPoint getPosition();
    
    public void setPosition(
        final SGMPoint position);
    
    public SGMFillPattern getFillPattern();
    
    public void setFillPattern(
        final SGMFillPattern fillPattern);
    
    public boolean equals(
        final SGMSurfaceFeature other);
    
    public Shape getShape();
    
    public SGMSurfaceFeature clone();
}
