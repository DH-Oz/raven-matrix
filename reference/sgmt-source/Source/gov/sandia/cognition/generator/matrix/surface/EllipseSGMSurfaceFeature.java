/*
 * File:                EllipseSGMSurfaceFeature.java
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
 * $Log: EllipseSGMSurfaceFeature.java,v $
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
 * Revision 1.8  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.7  2007/12/10 23:39:50  zobenz
 * Added numerosity structure feature
 *
 * Revision 1.6  2007/12/10 21:59:05  zobenz
 * Cleaned up surface feature generation to improve visual layout
 *
 * Revision 1.5  2007/12/10 20:11:07  zobenz
 * Fixed imports
 *
 * Revision 1.4  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.3  2007/12/06 23:28:31  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.2  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.1  2007/12/05 20:44:54  zobenz
 * Improved answer choice generation; Replaced SetIteration structure feature with Identity structure feature; added Rotate structure feature (which has a bug right now)
 *
 * Revision 1.4  2007/12/04 00:03:40  zobenz
 * Implemented fill pattern attribute of surface features.
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
 * Revision 1.1  2007/11/07 16:47:46  zobenz
 * Interim checkin; working on implementing SGM generation code.
 *
 */
 
package gov.sandia.cognition.generator.matrix.surface;

import gov.sandia.cognition.generator.matrix.SGMFeature;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.generator.matrix.SGMPoint;
import java.awt.geom.Ellipse2D;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class EllipseSGMSurfaceFeature extends AbstractSGMSurfaceFeature
{     
    public static final String DESCRIPTION = "Ellipse";
    private double width;
    private double height;
    
    public EllipseSGMSurfaceFeature(
            final double width,
            final double height,
            final int rotation,            
            final SGMPoint position,
            final SGMFillPattern fillPattern)
    {
        super(1.0, rotation, fillPattern,
               new Ellipse2D.Double(position.x - (width / 2.0),
               position.y - (height / 2.0), width, height));
        this.setWidth(width);
        this.setHeight(height);
    }
    
    public EllipseSGMSurfaceFeature(
        final EllipseSGMSurfaceFeature other)
    {
        super(other);
    }

    @Override
    public Ellipse2D.Double getShape()
    {
        return (Ellipse2D.Double)super.getShape();
    }       

    @Override
    public SGMPoint getPosition()
    {                
        return new SGMPoint(this.getShape().getCenterX(),
            this.getShape().getCenterY());
    }      
    
    @Override
    public void setPosition(
        final SGMPoint position)
    {        
        double halfWidth = this.getShape().width / 2.0;
        double halfHeight = this.getShape().height / 2.0;        
        this.setShape(new Ellipse2D.Double(position.x - halfWidth,
            position.y - halfHeight, this.getShape().width, 
            this.getShape().height));
    }
    
    @Override
    public AbstractSGMSurfaceFeature clone()
    {
        return new EllipseSGMSurfaceFeature(this);
    }

    public String getDescription()
    {
        return DESCRIPTION;
    }

    public boolean checkCompatibility(
        final SGMFeature feature)
    {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    public double getWidth()
    {
        return width;
    }

    private void setWidth(
        final double width)
    {
        this.width = width;
    }

    public double getHeight()
    {
        return height;
    }

    private void setHeight(
        final double height)
    {
        this.height = height;
    }

    @Override
    protected boolean customEqualsCheck(SGMSurfaceFeature other)
    {
        if (!(other instanceof EllipseSGMSurfaceFeature))
        {
            return false;
        }
        else
        {
            EllipseSGMSurfaceFeature otherCasted =
                (EllipseSGMSurfaceFeature)other;
            return (this.getFillPattern().getDescription().
                equals(other.getFillPattern().getDescription())) &&
                ((this.getWidth() * this.getScale()) ==
                (otherCasted.getWidth() * otherCasted.getScale())) &&
                ((this.getHeight() * this.getScale()) ==
                (otherCasted.getHeight() * otherCasted.getScale()));
        }
    }
}
