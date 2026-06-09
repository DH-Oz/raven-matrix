/*
 * File:                LineSGMSurfaceFeature.java
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
 * $Log: LineSGMSurfaceFeature.java,v $
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:06  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:00  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:30  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:26  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.7  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.6  2007/12/10 23:39:50  zobenz
 * Added numerosity structure feature
 *
 * Revision 1.5  2007/12/10 20:11:07  zobenz
 * Fixed imports
 *
 * Revision 1.4  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.3  2007/12/06 23:28:32  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.2  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.1  2007/12/05 20:44:54  zobenz
 * Improved answer choice generation; Replaced SetIteration structure feature with Identity structure feature; added Rotate structure feature (which has a bug right now)
 *
 * Revision 1.6  2007/12/04 00:03:40  zobenz
 * Implemented fill pattern attribute of surface features.
 *
 * Revision 1.5  2007/11/13 22:58:54  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.4  2007/11/13 20:28:12  zobenz
 * Fixed painting colors; fixed line surface feature; updated proof of concept code
 *
 * Revision 1.3  2007/11/12 23:20:39  zobenz
 * Working on being able to render matrices to screen and to bitmap
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
import java.awt.Shape;
import java.awt.geom.Line2D;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class LineSGMSurfaceFeature extends AbstractSGMSurfaceFeature
{

    public static final String DESCRIPTION = "Line";
    private double length;

    public LineSGMSurfaceFeature(
        final double length,
        final int rotation,
        final SGMPoint position,
        final SGMFillPattern fillPattern)
    {
        super(1.0, rotation, fillPattern, createLine(length, position));

        // Store length for future use when changing position of line
        this.setLength(length);
    }
    
    public LineSGMSurfaceFeature(
        final LineSGMSurfaceFeature other)
    {
        super(other);
        this.setLength(other.getLength());
    }

    private static Shape createLine(
        final double length,
        final SGMPoint position)
    {
        // Rotation will be handled by transform in super, so we
        // can just create a horizontal line with the specified
        // position as the center of the line        
        double halfLength = length / 2.0;
        double x1 = position.x - halfLength;
        double x2 = position.x + halfLength;
        return new Line2D.Double(x1, position.y, x2, position.y);
    }

    @Override
    public Line2D.Double getShape()
    {
        return (Line2D.Double) super.getShape();
    }

    @Override
    public SGMPoint getPosition()
    {
        double x = (this.getShape().x1 + this.getShape().x2) / 2.0;
        double y = (this.getShape().y1 + this.getShape().y2) / 2.0;
        return new SGMPoint(x, y);
    }

    @Override
    public void setPosition(
        final SGMPoint position)
    {
        this.setShape(createLine(this.getLength(), position));
    }

    @Override
    public AbstractSGMSurfaceFeature clone()
    {
        return new LineSGMSurfaceFeature(this);
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

    public double getLength()
    {
        return length;
    }

    protected void setLength(
        final double length)
    {
        this.length = length;
    }
    
    @Override
    protected boolean customEqualsCheck(SGMSurfaceFeature other)
    {
        if (!(other instanceof LineSGMSurfaceFeature))
        {
            return false;
        }
        else
        {
            LineSGMSurfaceFeature otherCasted =
                (LineSGMSurfaceFeature)other;
            return (this.getFillPattern().getDescription().
                equals(other.getFillPattern().getDescription())) &&
                ((this.getLength() * this.getScale()) ==
                (otherCasted.getLength() * otherCasted.getScale()));
        }
    }
}
