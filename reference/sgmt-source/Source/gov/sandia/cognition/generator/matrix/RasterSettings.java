/*
 * File:                RasterSettings.java
 * Authors:             Zachary Benz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright March 25, 2008, Sandia Corporation.
 * Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive 
 * license for use of this work by or on behalf of the U.S. Government. Export 
 * of this program may require a license from the United States Government. 
 * See CopyrightHistory.txt for complete details.
 * 
 * Revision History:
 * 
 * $Log: RasterSettings.java,v $
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:06  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.2  2010/12/20 17:52:32  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.1  2008/03/25 16:04:30  zobenz
 * Cleaned up model settings - All model settings now stored in AnalogyModelSettings.java; added a RasterSettings.java to store just the image rasterization settings for SGM generation and rasterization
 *
 */

package gov.sandia.cognition.generator.matrix;

import java.io.Serializable;

/**
 * @TODO    Document this.
 * 
 * @author  Zachary Benz
 * @since   1.0
 */
public class RasterSettings
    implements Serializable
{
    private int rasterImageWidth;
    private int rasterImageHeight;
    private int sgmCellRasterImagePixelSize;
    private int pixelsBetweenSGMCells;
    
    public RasterSettings(
        final int rasterImageWidth,
        final int rasterImageHeight,
        final int sgmCellRasterImagePixelSize,
        final int pixelsBetweenSGMCells)
    {
        this.setRasterImageWidth(rasterImageWidth);
        this.setRasterImageHeight(rasterImageHeight);
        this.setSGMCellRasterImagePixelSize(sgmCellRasterImagePixelSize);
        this.setPixelsBetweenSGMCells(pixelsBetweenSGMCells);
    }
    
    public int getRasterImageWidth()
    {
        return rasterImageWidth;
    }

    private void setRasterImageWidth(
        final int rasterImageWidth)
    {
        this.rasterImageWidth = rasterImageWidth;
    }

    public int getRasterImageHeight()
    {
        return rasterImageHeight;
    }

    private void setRasterImageHeight(
        final int rasterImageHeight)
    {
        this.rasterImageHeight = rasterImageHeight;
    }

    public int getSGMCellRasterImagePixelSize()
    {
        return sgmCellRasterImagePixelSize;
    }

    private void setSGMCellRasterImagePixelSize(
        final int sgmCellRasterImagePixelSize)
    {
        this.sgmCellRasterImagePixelSize = sgmCellRasterImagePixelSize;
    }

    public int getPixelsBetweenSGMCells()
    {
        return pixelsBetweenSGMCells;
    }

    private void setPixelsBetweenSGMCells(
        final int pixelsBetweenSGMCells)
    {
        this.pixelsBetweenSGMCells = pixelsBetweenSGMCells;
    }
}
