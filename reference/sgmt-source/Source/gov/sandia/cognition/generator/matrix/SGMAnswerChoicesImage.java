/*
 * File:                SGMAnswerChoicesImage.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 4, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMAnswerChoicesImage.java,v $
 * Revision 1.2  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
 * Revision 1.1  2010/12/21 15:50:06  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:03  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:33  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:23  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.4  2009/02/16 22:04:55  cewarr
 * Modifications to read image inputs with different formats (RGBA, RGB...)
 *
 * Revision 1.3  2009/02/06 22:35:34  cewarr
 * Added ability to create input images from file; isolated methods to create or read images to avoid duplication of code.
 *
 * Revision 1.2  2007/12/12 23:02:55  jdbasil
 * Pair made into interface. Code moved to DefaultPair.
 *
 * Revision 1.1  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 */
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.util.DefaultPair;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.image.BufferedImage;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMAnswerChoicesImage
    extends AbstractSGMImage
{
    private int pixelsBetweenCells;
    private int numAnswerMatrixColumns;
    private int numAnswerMatrixRows;
    private SGMMatrix sgmMatrix;
    private SGMCellImage[][] sgmCellImages;

    private static DefaultPair<Integer, Integer> calcNumRowsColumns(
        final int numAnswerChoices,
        final int numAnswerMatrixColumns)
    {        
        int numAnswerMatrixRows = numAnswerChoices /
            numAnswerMatrixColumns;       
        if (numAnswerChoices % numAnswerMatrixColumns > 0)
        {
            numAnswerMatrixRows++;
        }
        int localNumAnswerMatrixColumns = numAnswerMatrixColumns;
        if (numAnswerMatrixColumns > numAnswerChoices)
        {
            localNumAnswerMatrixColumns = numAnswerChoices;
        }

        return new DefaultPair<Integer,Integer>
            (numAnswerMatrixRows, localNumAnswerMatrixColumns);
    }

    private static int calcWidth(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final int numAnswerMatrixColumns,
        final int numAnswerChoices)
    {
        int width = ((sgmCellImagePixelSize + pixelsBetweenCells) *
            calcNumRowsColumns(numAnswerChoices,
            numAnswerMatrixColumns).getSecond()) + pixelsBetweenCells;

        return width;
    }

    private static int calcWidth(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final int numAnswerMatrixColumns,
        final SGMMatrix sgmMatrix)
    {
        int width = ((sgmCellImagePixelSize + pixelsBetweenCells) *
            calcNumRowsColumns(sgmMatrix.getAnswerChoices().size(),
            numAnswerMatrixColumns).getSecond()) + pixelsBetweenCells;

        return width;
    }

    private static int calcHeight(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final int numAnswerMatrixColumns,
        final int numAnswerChoices)
    {
        int height = ((sgmCellImagePixelSize + pixelsBetweenCells) *
            calcNumRowsColumns(numAnswerChoices,numAnswerMatrixColumns).getFirst())
            + pixelsBetweenCells;
        
        return height;
    }
    
    private static int calcHeight(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final int numAnswerMatrixColumns,
        final SGMMatrix sgmMatrix)
    {
        int height = ((sgmCellImagePixelSize + pixelsBetweenCells) *
            calcNumRowsColumns(sgmMatrix.getAnswerChoices().size(),
            numAnswerMatrixColumns).getFirst()) + pixelsBetweenCells;

        return height;
    }

    public SGMAnswerChoicesImage(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final int numAnswerMatrixColumns,
        final SGMMatrix sgmMatrix)
    {
        super(calcWidth(sgmCellImagePixelSize, pixelsBetweenCells,
            numAnswerMatrixColumns, sgmMatrix),
            calcHeight(sgmCellImagePixelSize, pixelsBetweenCells,
            numAnswerMatrixColumns, sgmMatrix));

        this.setPixelsBetweenCells(pixelsBetweenCells);
        DefaultPair<Integer, Integer> numRowsColumns = calcNumRowsColumns(
            sgmMatrix.getAnswerChoices().size(), numAnswerMatrixColumns);
        this.setNumAnswerMatrixRows(numRowsColumns.getFirst());
        this.setNumAnswerMatrixColumns(numRowsColumns.getSecond());
        this.setSGMMatrix(sgmMatrix);
    }
    
    public SGMAnswerChoicesImage(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final int numAnswerChoices,
        final int numAnswerMatrixColumns,
        final BufferedImage image)
    {
        // TODO:  we're assuming here that any input image file that doesn't
        // specify the image format properly - like images produced by our
        // SGM Builder - are ARGB format.  Not necessarily a good assumption
        // for other inputs, but as of 2/16/09, all the other input images we
        // use do specify format correctly.
        super(calcWidth(sgmCellImagePixelSize, pixelsBetweenCells,
            numAnswerMatrixColumns, numAnswerChoices),
            calcHeight(sgmCellImagePixelSize, pixelsBetweenCells,
            numAnswerMatrixColumns, numAnswerChoices), 
            image.getType()==0? BufferedImage.TYPE_INT_ARGB : image.getType() );
            
        
        this.setPixelsBetweenCells(pixelsBetweenCells);
        DefaultPair<Integer, Integer> numRowsColumns = calcNumRowsColumns(
            numAnswerChoices, numAnswerMatrixColumns);
        this.setNumAnswerMatrixRows(numRowsColumns.getFirst());
        this.setNumAnswerMatrixColumns(numRowsColumns.getSecond());   
        
        // creating the object this way means we won't be able to reconstruct
        // the original SGMMatrix object
        this.sgmMatrix = null;
        this.setData(image.getData());
        
        // create the individual SGM CellImages by subdividing
        // original image
        this.divideImage(image);
    }

    private void divideImage(BufferedImage image) 
    {
        // Determine how big a SGM cell should be drawn
        int numCellsAcross = this.getNumAnswerMatrixColumns();
        int cellWidth = (this.getWidth() - (this.getPixelsBetweenCells() *
            (numCellsAcross + 1))) / numCellsAcross;
        int numCellsDown = this.getNumAnswerMatrixRows();
        int cellHeight = (this.getHeight() - (this.getPixelsBetweenCells() *
            (numCellsDown + 1))) / numCellsDown;

        // Set up storage for SGM cell images
        this.setSGMCellImages(
            new SGMCellImage[numCellsDown][numCellsAcross]);

        // Now draw in the SGM cells
        int x = this.getPixelsBetweenCells();
        int y = this.getPixelsBetweenCells();
        for (int row = 0; row < numCellsDown; row++)
        {
            for (int col = 0; col < numCellsAcross; col++)
            {
                // Create image for current cell
                BufferedImage subimage = image.getSubimage(x, y, cellWidth, cellHeight);
                SGMCellImage sgmCellImage = new SGMCellImage(cellWidth,
                    cellHeight, subimage);

                // Store image for possible later retrieval
                this.getSGMCellImages()[row][col] = sgmCellImage;

                // Update draw position for next iteration
                x += (cellWidth + this.getPixelsBetweenCells());
            }

            // Update draw position for next iteration
            x = this.getPixelsBetweenCells();
            y += (cellHeight + this.getPixelsBetweenCells());
        }
    }

    private int getPixelsBetweenCells()
    {
        return pixelsBetweenCells;
    }

    private void setPixelsBetweenCells(
        final int pixelsBetweenCells)
    {
        this.pixelsBetweenCells = pixelsBetweenCells;
    }

    private SGMMatrix getSGMMatrix()
    {
        return sgmMatrix;
    }

    private void setSGMMatrix(
        final SGMMatrix sgmMatrix)
    {
        this.sgmMatrix = sgmMatrix;
        Graphics2D g2 = this.createGraphics();

        // Need to make image background black - easiest way to do this
        // is to just draw a rectangle filling the image
        g2.setColor(Color.BLACK);
        g2.setBackground(Color.BLACK);
        Shape blackBackground =
            new Rectangle(0, 0, this.getWidth(), this.getHeight());
        g2.fill(blackBackground);
        g2.draw(blackBackground);

        // Determine how big a SGM cell should be drawn
        int numCellsAcross = this.getNumAnswerMatrixColumns();
        int cellWidth = (this.getWidth() - (this.getPixelsBetweenCells() *
            (numCellsAcross + 1))) / numCellsAcross;
        int numCellsDown = this.getNumAnswerMatrixRows();
        int cellHeight = (this.getHeight() - (this.getPixelsBetweenCells() *
            (numCellsDown + 1))) / numCellsDown;

        // Set up storage for SGM cell images
        this.setSGMCellImages(
            new SGMCellImage[numCellsDown][numCellsAcross]);

        // Now draw in the SGM cells
        int x = this.getPixelsBetweenCells();
        int y = this.getPixelsBetweenCells();
        g2.setColor(Color.BLACK);
        int i = 0;
        for (int row = 0; row < numCellsDown; row++)
        {
            for (int col = 0; col < numCellsAcross; col++)
            {
                // Create image for current cell
                SGMCellImage sgmCellImage = new SGMCellImage(cellWidth,
                    cellHeight,
                    this.getSGMMatrix().getAnswerChoices().get(i));

                // Store image for possible later retrieval
                this.getSGMCellImages()[row][col] = sgmCellImage;

                // Draw the cell into the matrix image  
                g2.drawImage(sgmCellImage, null, x, y);

                // Update draw position for next iteration
                x += (cellWidth + this.getPixelsBetweenCells());

                // Update which answer choice we're on, and quit
                // if we've past the last one
                i++;
                if (i >= this.getSGMMatrix().getAnswerChoices().size())
                {
                    break;
                }
            }

            // Quit if we've processed all the answer choices
            if (i >= this.getSGMMatrix().getAnswerChoices().size())
            {
                break;
            }

            // Update draw position for next iteration
            x = this.getPixelsBetweenCells();
            y += (cellHeight + this.getPixelsBetweenCells());
        }
    }

    public SGMCellImage getAnswerImage(int index)
    {
        int row = index / this.getNumAnswerMatrixColumns();
        int col = index % this.getNumAnswerMatrixColumns();
        return sgmCellImages[row][col];
    }
    
    private SGMCellImage[][] getSGMCellImages()
    {
        return sgmCellImages;
    }

    private void setSGMCellImages(
        final SGMCellImage[][] sgmCellImages)
    {
        this.sgmCellImages = sgmCellImages;
    }

    public int getNumAnswerMatrixColumns()
    {
        return numAnswerMatrixColumns;
    }

    public void setNumAnswerMatrixColumns(int numAnswerMatrixColumns)
    {
        this.numAnswerMatrixColumns = numAnswerMatrixColumns;
    }

    public int getNumAnswerMatrixRows()
    {
        return numAnswerMatrixRows;
    }

    public void setNumAnswerMatrixRows(int numAnswerMatrixRows)
    {
        this.numAnswerMatrixRows = numAnswerMatrixRows;
    }
}
