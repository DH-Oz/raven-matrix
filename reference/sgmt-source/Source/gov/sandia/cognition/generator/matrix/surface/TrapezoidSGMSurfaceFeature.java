/*
 * File:                TrapezoidSGMSurfaceFeature.java
 * Authors:             Christina Warrender
 * Company:             Sandia National Laboratories
 * Project:             Cognitive Foundry
 * 
 * Copyright November 04, 2008, Sandia Corporation.
 * Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive 
 * license for use of this work by or on behalf of the U.S. Government. Export 
 * of this program may require a license from the United States Government. 
 * See CopyrightHistory.txt for complete details.
 * 
 * Revision History:
 * 
 * $Log: TrapezoidSGMSurfaceFeature.java,v $
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
 * Revision 1.1  2008/11/05 18:24:26  cewarr
 * Tweaked the grey fill patterns, added two shapes, eliminated squares/circles and repeat use of same shape in a matrix, fixed some problems with wrong answers when numerosity is used.
 *
 */

package gov.sandia.cognition.generator.matrix.surface;

import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.generator.matrix.SGMPoint;
import java.awt.geom.Path2D;

/**
 * @TODO    Document this.
 * 
 * @author  Christina Warrender
 * @since   2.1
 */
public class TrapezoidSGMSurfaceFeature
    extends AbstractPathBasedSGMSurfaceFeature
{     
    public static final String DESCRIPTION = "Trapezoid";
    
    @Override
    public Path2D.Double makePath(
        final double width,        
        final double height,
        final SGMPoint position)
    {
        Path2D.Double path = new Path2D.Double(); 
        
        double halfWidth = width / 2.0;
        double quarterWidth = halfWidth / 2.0;
        double halfHeight = height / 2.0;
        
        path.moveTo(position.x - halfWidth, position.y + halfHeight);
        path.lineTo(position.x + halfWidth, position.y + halfHeight);
        path.lineTo(position.x + quarterWidth, position.y - halfHeight);
        path.lineTo(position.x - quarterWidth, position.y - halfHeight);
        path.lineTo(position.x - halfWidth, position.y + halfHeight);
        
        return path;
    }
    
    public TrapezoidSGMSurfaceFeature(
            final double width,
            final double height,
            final int rotation,            
            final SGMPoint position,
            final SGMFillPattern fillPattern)
    {        
        super(width, height, rotation, position, fillPattern);
    }
    
    public TrapezoidSGMSurfaceFeature(
        final TrapezoidSGMSurfaceFeature other)
    {
        super(other);
    }    
                  
    @Override
    public AbstractSGMSurfaceFeature clone()
    {
        return new TrapezoidSGMSurfaceFeature(this);
    }

    public String getDescription()
    {
        return DESCRIPTION;
    }    
}
