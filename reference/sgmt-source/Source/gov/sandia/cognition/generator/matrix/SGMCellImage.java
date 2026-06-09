/*
 * File:                SGMCellImage.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 13, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMCellImage.java,v $
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
 * Revision 1.18  2009/02/16 22:04:55  cewarr
 * Modifications to read image inputs with different formats (RGBA, RGB...)
 *
 * Revision 1.17  2009/02/06 22:35:34  cewarr
 * Added ability to create input images from file; isolated methods to create or read images to avoid duplication of code.
 *
 * Revision 1.16  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.15  2007/12/10 23:39:50  zobenz
 * Added numerosity structure feature
 *
 * Revision 1.14  2007/12/10 21:59:05  zobenz
 * Cleaned up surface feature generation to improve visual layout
 *
 * Revision 1.13  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.12  2007/12/06 23:28:33  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.11  2007/12/06 19:04:41  zobenz
 * Committing working implementation in preparation for overhauling way in which structure features are applied
 *
 * Revision 1.10  2007/12/05 23:55:28  zobenz
 * Fixed Rotate structure feature (but still disabled in matrix generation for now); implemented Scale structure feature
 *
 * Revision 1.9  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.8  2007/12/04 15:31:26  zobenz
 * Made surface feature stroke width thicker (2.0f) when rendered in cell image
 *
 * Revision 1.7  2007/12/04 00:03:40  zobenz
 * Implemented fill pattern attribute of surface features.
 *
 * Revision 1.6  2007/12/03 23:09:21  zobenz
 * Initial implementation of a complete top to bottom stochastic generation of SGMs
 *
 * Revision 1.5  2007/11/28 19:30:23  krdixon
 * Changed from (x,y) to (row,column)
 *
 * Revision 1.4  2007/11/26 23:15:18  zobenz
 * Filled in implementation of SGMMatrixImage
 *
 * Revision 1.3  2007/11/26 22:14:29  zobenz
 * Fixed bug in test code for creating a couple of layers; added SGMMatrixImage to support rastering the entire matrix as a whole.
 *
 * Revision 1.2  2007/11/21 18:01:07  zobenz
 * SGMLayer implementation completed
 *
 * Revision 1.1  2007/11/19 22:59:30  zobenz
 * Promoted SGMCellImage up out of .ui sub package, as it is more general and not specific to UI.
 *
 * Revision 1.4  2007/11/19 22:56:41  zobenz
 * Added ability to get rasterized version of SGM cell image
 *
 * Revision 1.3  2007/11/13 22:58:55  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.2  2007/11/13 20:28:12  zobenz
 * Fixed painting colors; fixed line surface feature; updated proof of concept code
 *
 * Revision 1.1  2007/11/13 18:11:55  zobenz
 * Proof of concept rendering SGMCell to window, bottom to top
 *
 */
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.surface.LineSGMSurfaceFeature;
import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Paint;
import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.Stroke;
import java.awt.geom.AffineTransform;
import java.awt.image.BufferedImage;
import java.awt.image.Raster;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMCellImage
    extends AbstractSGMImage
{

    private SGMCell sgmCell;

    public SGMCellImage(
        final int width,
        final int height,
        final SGMCell sgmCell)
    {
        super(width, height);

        this.setSGMCell(sgmCell);
    }
    
    public SGMCellImage(
        final int width, 
        final int height,
        final BufferedImage image)
    {
        // TODO:  we're assuming here that any input image file that doesn't
        // specify the image format properly - like images produced by our
        // SGM Builder - are ARGB format.  Not necessarily a good assumption
        // for other inputs, but as of 2/16/09, all the other input images we
        // use do specify format correctly.
        super(width, height, 
            image.getType()==0? BufferedImage.TYPE_INT_ARGB : image.getType() );
        this.sgmCell = null;
        this.setData(image.getData()); 
    }

    public SGMCell getSGMCell()
    {
        return this.sgmCell;
    }

    protected void setSGMCell(
        final SGMCell sgmCell)
    {
        this.sgmCell = sgmCell;
        Graphics2D g2 = this.createGraphics();

        // Need to make image background white - easiest way to do this
        // is to just draw a rectangle filling the image
        g2.setColor(Color.WHITE);
        g2.setBackground(Color.WHITE);
        Shape whiteBackground =
            new Rectangle(0, 0, this.getWidth(), this.getHeight());
        g2.fill(whiteBackground);
        g2.draw(whiteBackground);

        // Now draw in the shapes for the SGM cell
        g2.setColor(Color.BLACK);
        for (SGMSurfaceFeature feature : sgmCell.getSurfaceFeatures())
        {
            Shape shape = feature.getShape();

            // Convert rotation to radians from degrees
            double rotationRadians = ((double)feature.getRotation()) 
                / 180.0 * Math.PI;


            // Get width and height of shape to be used during
            // translate of shape to origin for transform application - note
            // that line surface feature doesn't need this, as it already
            // treats it's position as being the center of the line
            double halfWidth = 0.0;
            double halfHeight = 0.0;
            if (!(feature instanceof LineSGMSurfaceFeature))
            {
                halfWidth = feature.getShape().getBounds().getWidth() / 2.0;
                halfHeight = feature.getShape().getBounds().getHeight() / 2.0;
            }
            
            // Set up transform - remember, pieces of transform
            // specified below are executed in reverse order - i.e.
            // last one first in terms of the effect on the Shape
            AffineTransform transform = new AffineTransform();
            transform.translate(feature.getPosition().x,
                feature.getPosition().y);
            transform.rotate(rotationRadians);                   
            transform.scale(feature.getScale(), feature.getScale());            
            transform.translate(-feature.getPosition().x,
                -feature.getPosition().y);

            shape = transform.createTransformedShape(shape);

            Paint originalPaint = g2.getPaint();
            g2.setPaint(feature.getFillPattern().getPaint());
            g2.fill(shape);
            g2.setPaint(originalPaint);
            Stroke originalStroke = g2.getStroke();
            g2.setStroke(new BasicStroke(2.0f));
            g2.draw(shape);
            g2.setStroke(originalStroke);
        }
    }
}
