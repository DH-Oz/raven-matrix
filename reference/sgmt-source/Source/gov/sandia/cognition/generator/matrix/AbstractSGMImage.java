/*
 * File:                AbstractSGMImage.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 26, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: AbstractSGMImage.java,v $
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
 * Revision 1.6  2009/02/16 22:04:55  cewarr
 * Modifications to read image inputs with different formats (RGBA, RGB...)
 *
 * Revision 1.5  2008/02/07 17:13:47  krdixon
 * Made a static version of createImageRaster()
 *
 * Revision 1.4  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 * Revision 1.3  2007/12/03 23:09:21  zobenz
 * Initial implementation of a complete top to bottom stochastic generation of SGMs
 *
 * Revision 1.2  2007/11/28 19:30:18  krdixon
 * Changed from (x,y) to (row,column)
 *
 * Revision 1.1  2007/11/26 23:15:18  zobenz
 * Filled in implementation of SGMMatrixImage
 *
 */

package gov.sandia.cognition.generator.matrix;

import java.awt.Image;
import java.awt.image.BufferedImage;
import java.awt.image.ColorModel;
import java.awt.image.PixelGrabber;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public abstract class AbstractSGMImage
    extends BufferedImage
{
    public AbstractSGMImage(
        int width,
        int height)
    {
        // BufferedImage uses (width,height) instead of (height,width)
        super(width, height, BufferedImage.TYPE_INT_ARGB);
    }
    
    public AbstractSGMImage(
        int width,
        int height,
        int imageType)
    {
        super(width, height, imageType);
    }

    public float[][] createImageRaster(
        int numRows,
        int numColumns )
        throws InterruptedException
    {
        return AbstractSGMImage.createImageRaster(this, numRows, numColumns);
    }
     
    public static float[][] createImageRaster(
        BufferedImage bufferedImage,
        int numRows,
        int numColumns )
        throws InterruptedException
    {
        float imageRaster[][] = new float[numRows][numColumns];

        // PixelGrabber uses (width,height), not (height,width)
        PixelGrabber pg = new PixelGrabber(
            bufferedImage.getScaledInstance( numColumns, numRows, Image.SCALE_SMOOTH ),
            0, 0, numColumns, numRows, false );
        pg.grabPixels();
        ColorModel cm = pg.getColorModel();
        int ip[] = (int[]) pg.getPixels();
        int x, y, i = 0;
        final float normalizer = 3.0f * 255;
        for (y = 0; y < numRows; y++)
        {
            for (x = 0; x < numColumns; x++)
            {
                imageRaster[y][x] = (cm.getRed( ip[i] ) + cm.getGreen( ip[i] ) +
                    cm.getBlue( ip[i] )) / normalizer;
                i++;
            }
        }

        return imageRaster;
    }
}
