/*
 * File:                AbstractSGMSurfaceFeature.java
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
 * $Log: AbstractSGMSurfaceFeature.java,v $
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
 * Revision 1.6  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.5  2007/12/10 20:11:07  zobenz
 * Fixed imports
 *
 * Revision 1.4  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.3  2007/12/10 19:56:04  zobenz
 * Filled in rest of answer choice generation by randomly manipulating parameters of surface features
 *
 * Revision 1.2  2007/12/10 18:55:41  zobenz
 * Fixed surface feature equals check to take into account fill pattern (except when comparing lines, as fill pattern is irrelevant for them)
 *
 * Revision 1.1  2007/12/06 23:28:32  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.6  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.5  2007/12/05 20:44:55  zobenz
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
 * Revision 1.1  2007/11/07 17:35:34  zobenz
 * Refactoring class names to be consistent across project.
 *
 * Revision 1.1  2007/11/07 16:47:46  zobenz
 * Interim checkin; working on implementing SGM generation code.
 *
 */
package gov.sandia.cognition.generator.matrix.surface;

import gov.sandia.cognition.generator.matrix.SGMPoint;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import java.awt.Shape;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public abstract class AbstractSGMSurfaceFeature implements SGMSurfaceFeature
{

    private double scale;
    private int rotation;
    private SGMFillPattern fillPattern;
    private Shape shape;

    public AbstractSGMSurfaceFeature(
        final double scale,
        final int rotation,
        final SGMFillPattern fillPattern,
        final Shape shape)
    {
        this.setScale(scale);
        this.setRotation(rotation);
        this.setFillPattern(fillPattern);
        this.setShape(shape);
    }
    
    public AbstractSGMSurfaceFeature(
        final SGMSurfaceFeature other)
    {
        this.setScale(other.getScale());
        this.setRotation(other.getRotation());
        this.setFillPattern(other.getFillPattern());
        this.setShape(other.getShape());
    }

    public double getScale()
    {
        return scale;
    }

    public void setScale(
        final double scale)
    {
        this.scale = scale;
    }

    public int getRotation()
    {
        return this.rotation;
    }

    public void setRotation(
        int rotation)
    {
        this.rotation = rotation % 360;
    }

    public abstract SGMPoint getPosition();

    public abstract void setPosition(
        final SGMPoint position);

    public SGMFillPattern getFillPattern()
    {
        return fillPattern;
    }

    public void setFillPattern(
        final SGMFillPattern fillPattern)
    {
        this.fillPattern = fillPattern;
    }

    public Shape getShape()
    {
        return shape;
    }

    protected void setShape(
        Shape shape)
    {
        this.shape = shape;
    }

    protected abstract boolean customEqualsCheck(
        final SGMSurfaceFeature other);
    
    public boolean equals(
        final SGMSurfaceFeature other)
    {
        // Perform equals check on things that are common across all surface
        // features ANDed with equals check on things particular to the
        // surface feature type
        return (this.getScale() == other.getScale() &&
                this.getRotation() == other.getRotation() &&
                this.getPosition().x == other.getPosition().x &&
                this.getPosition().y == other.getPosition().y &&                
                this.getDescription().equals(other.getDescription()) &&
                this.customEqualsCheck(other));
        
        
//        // Fill pattern has no meaning for lines, so exclude it from
//        // equals checks if both features are a line
//        if ((this instanceof LineSGMSurfaceFeature) &&
//            (other instanceof LineSGMSurfaceFeature))
//        {
//            // getDescription used in lieu of getShape and getFillPattern to
//            // compare shape and fill pattern types, and not object
//            // reference equality
//            return (this.getScale() == other.getScale() &&
//                this.getRotation() == other.getRotation() &&
//                this.getPosition().x == other.getPosition().x &&
//                this.getPosition().y == other.getPosition().y &&                
//                this.getDescription().equals(other.getDescription()));
//        }
//        else
//        {
//            // getDescription used in lieu of getShape and getFillPattern to
//            // compare shape and fill pattern types, and not object
//            // reference equality
//            return (this.getScale() == other.getScale() &&
//                this.getRotation() == other.getRotation() &&
//                this.getPosition().x == other.getPosition().x &&
//                this.getPosition().y == other.getPosition().y &&
//                this.getDescription().equals(other.getDescription()) &&
//                this.getFillPattern().getDescription().
//                    equals(other.getFillPattern().getDescription()));
//        }
    }

    @Override
    public abstract AbstractSGMSurfaceFeature clone();
}
