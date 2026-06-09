/*
 * File:                SGMMatrixImage.java
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
 * $Log: SGMMatrixImage.java,v $
 * Revision 1.3  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
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
 * Revision 1.12  2009/03/10 17:28:33  cewarr
 * Fixed code to merge an answer choice with an incomplete matrix when both are read from file; cell was being updated, but not underlying BufferedImage of the whole matrix.
 *
 * Revision 1.11  2009/02/16 22:04:55  cewarr
 * Modifications to read image inputs with different formats (RGBA, RGB...)
 *
 * Revision 1.10  2009/02/06 22:35:34  cewarr
 * Added ability to create input images from file; isolated methods to create or read images to avoid duplication of code.
 *
 * Revision 1.9  2008/03/03 21:07:05  zobenz
 * Updated AnalogyModel to store settings for how to draw a SGM, and added evaluate method to allow you to easily pass in an SGM and have it be fed to the model.
 *
 * Revision 1.8  2008/01/17 21:09:44  zobenz
 * Changed background color to white to avoid having black lines between cells of the matrix
 *
 * Revision 1.7  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 * Revision 1.6  2007/12/04 00:03:40  zobenz
 * Implemented fill pattern attribute of surface features.
 *
 * Revision 1.5  2007/12/03 23:09:21  zobenz
 * Initial implementation of a complete top to bottom stochastic generation of SGMs
 *
 * Revision 1.4  2007/12/03 20:32:41  zobenz
 * Working stochastic generation of multi-layer matrices; note for the moment structure and surface feature selection is hard-coded.
 *
 * Revision 1.3  2007/11/28 19:30:23  krdixon
 * Changed from (x,y) to (row,column)
 *
 * Revision 1.2  2007/11/26 23:15:18  zobenz
 * Filled in implementation of SGMMatrixImage
 *
 * Revision 1.1  2007/11/26 22:14:29  zobenz
 * Fixed bug in test code for creating a couple of layers; added SGMMatrixImage to support rastering the entire matrix as a whole.
 *
 */
package gov.sandia.cognition.generator.matrix;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.image.BufferedImage;

/**
 * SGMMatrixImage allows conversion between SGMMatrix objects
 * we create and SGMInputImages fed to the model.  As an AbstractSGMImage,
 * it supports rastering of the entire image, but it also allows access to the 
 * individual cells within the image.
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMMatrixImage
    extends AbstractSGMImage
{

    private int pixelsBetweenCells;
    private int sgmCellImagePixelSize;
    private SGMMatrix sgmMatrix;
    private SGMCellImage[][] sgmCellImages;
    
    private int answerRow;
    private int answerColumn;

    private static int calcWidth(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,        
        final SGMMatrix sgmMatrix)
    {

        int width = ((sgmCellImagePixelSize + pixelsBetweenCells) *
            sgmMatrix.getSGMMatrixSize().getNumColumns()) + pixelsBetweenCells;

        return width;
    }

    private static int calcHeight(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final SGMMatrix sgmMatrix)
    {
        int height = ((sgmCellImagePixelSize + pixelsBetweenCells) *
            sgmMatrix.getSGMMatrixSize().getNumRows()) + pixelsBetweenCells;

        return height;
    }

    public SGMMatrixImage(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final SGMMatrix sgmMatrix,
        final int answerChoice)
    {
        super(calcWidth(sgmCellImagePixelSize, pixelsBetweenCells, sgmMatrix),
            calcHeight(sgmCellImagePixelSize, pixelsBetweenCells, sgmMatrix));

        this.setSGMCellImagePixelSize(sgmCellImagePixelSize);
        this.setPixelsBetweenCells(pixelsBetweenCells);
        this.setSGMMatrix(sgmMatrix, answerChoice);
    }
    
    public SGMMatrixImage(
        final int sgmCellImagePixelSize,
        final int pixelsBetweenCells,
        final BufferedImage image,
        final int numMatrixRows,
        final int numMatrixColumns)
    {
        // TODO:  we're assuming here that any input image file that doesn't
        // specify the image format properly - like images produced by our
        // SGM Builder - are ARGB format.  Not necessarily a good assumption
        // for other inputs, but as of 2/16/09, all the other input images we
        // use do specify format correctly.
        super(image.getWidth(), image.getHeight(), 
            image.getType()==0? BufferedImage.TYPE_INT_ARGB : image.getType() );
                
        this.setSGMCellImagePixelSize(sgmCellImagePixelSize);
        this.setPixelsBetweenCells(pixelsBetweenCells);
        this.sgmMatrix = null;
        this.setData(image.getData());
        // create the individual SGMCellImages by subdividing
        // original image
        this.divideImage(image, numMatrixRows, numMatrixColumns);
    }

    private void divideImage(
        final BufferedImage image, 
        final int numMatrixRows, 
        final int numMatrixColumns) 
    {
        // Determine how big a SGM cell should be drawn
        int numCellsAcross = numMatrixColumns;
        int cellWidth = (this.getWidth() - (this.getPixelsBetweenCells() *
            (numCellsAcross + 1))) / numCellsAcross;
        int numCellsDown = numMatrixRows;
        int cellHeight = (this.getHeight() - (this.getPixelsBetweenCells() *
            (numCellsDown + 1))) / numCellsDown;
        
        this.answerRow = numCellsDown - 1;
        this.answerColumn = numCellsAcross - 1;

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
//                Rectangle rect = new Rectangle(x, y, cellWidth, cellHeight);
//                Raster subraster = image.getData(rect);
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
    
    protected int getSGMCellImagePixelSize()
    {
        return sgmCellImagePixelSize;
    }
    
    protected void setSGMCellImagePixelSize(int sgmCellImagePixelSize)
    {
        this.sgmCellImagePixelSize = sgmCellImagePixelSize;
    }

    protected int getPixelsBetweenCells()
    {
        return pixelsBetweenCells;
    }

    protected void setPixelsBetweenCells(int spaceBetweenCells)
    {
        this.pixelsBetweenCells = spaceBetweenCells;
    }

    public SGMMatrix getSGMMatrix()
    {
        return this.sgmMatrix;
    }

    protected void setSGMMatrix(
        final SGMMatrix sgmMatrix,
        final int answerChoice)
    {
        this.sgmMatrix = sgmMatrix;
        Graphics2D g2 = this.createGraphics();

        // Need to make image background black - easiest way to do this
        // is to just draw a rectangle filling the image
        Color currentColor = g2.getColor();
        Color currentBackground = g2.getBackground();
        g2.setColor(Color.WHITE);
        g2.setBackground(Color.WHITE);
        Shape background =
            new Rectangle(0, 0, this.getWidth(), this.getHeight());
        g2.fill(background);
        g2.draw(background);
        g2.setColor(currentColor);
        g2.setBackground(currentBackground);

        // Determine how big a SGM cell should be drawn
        int numCellsAcross =
            this.getSGMMatrix().getSGMMatrixSize().getNumColumns();
        int cellWidth = (this.getWidth() - (this.getPixelsBetweenCells() *
            (numCellsAcross + 1))) / numCellsAcross;
        int numCellsDown =
            this.getSGMMatrix().getSGMMatrixSize().getNumRows();
        int cellHeight = (this.getHeight() - (this.getPixelsBetweenCells() *
            (numCellsDown + 1))) / numCellsDown;

        this.answerRow = numCellsDown - 1;
        this.answerColumn = numCellsAcross - 1;

        // Set up storage for SGM cell images
        this.setSGMCellImages(
            new SGMCellImage[numCellsDown][numCellsAcross]);

        // Determine if we should draw an answer choice
        boolean drawAnswerChoice = false;
        if ((answerChoice > -1) && (answerChoice < 
            this.getSGMMatrix().getNumAnswerChoicesGenerated()))
        {
            drawAnswerChoice = true;
        }
        
        // Now draw in the SGM cells
        int x = this.getPixelsBetweenCells();
        int y = this.getPixelsBetweenCells();
        g2.setColor(Color.BLACK);
        boolean answerCell = false;
        for (int row = 0; row < numCellsDown; row++)
        {
            for (int col = 0; col < numCellsAcross; col++)
            {   
                // Check to see if we're drawing answer cell
                if ((row == (numCellsDown - 1)) &&
                    (col == (numCellsAcross - 1)))
                {
                    answerCell = true;
                }
                                                                                
                // Create image for current cell
                SGMCellImage sgmCellImage;
                if (answerCell && drawAnswerChoice)
                {
                    sgmCellImage = new SGMCellImage(cellWidth, cellHeight,
                        this.getSGMMatrix().getAnswerChoices().
                        get(answerChoice));
                }
                else
                {
                    sgmCellImage = new SGMCellImage(cellWidth, cellHeight,
                        this.getSGMMatrix().getSGMCells()[row][col]);
                }

                // Store image for possible later retrieval
                this.getSGMCellImages()[row][col] = sgmCellImage;
                                    
                // If no answer choice specified, don't draw the answer, which
                // is always the bottom right cell of the matrix
                if (answerCell && !drawAnswerChoice)
                {
                    // Draw an empty white cell   
                    currentColor = g2.getColor();
                    currentBackground = g2.getBackground();
                    g2.setColor(Color.WHITE);
                    g2.setBackground(Color.WHITE);
                    background = new Rectangle(x, y, cellWidth, cellHeight);
                    g2.fill(background);
                    g2.draw(background);
                    g2.setColor(currentColor);
                    g2.setBackground(currentBackground);
                }
                else
                {                
                    // Draw the cell into the matrix image  
                    g2.drawImage(sgmCellImage, null, x, y);
                }
                
                // Update draw position for next iteration
                x += (cellWidth + this.getPixelsBetweenCells());
            }
            
            // Update draw position for next iteration
            x = this.getPixelsBetweenCells();            
            y += (cellHeight + this.getPixelsBetweenCells());
        }
    }
    
    public void setAnswerCellImage(SGMCellImage image)
    {
        this.sgmCellImages[answerRow][answerColumn] = image;

        // need to also change BufferedImage data for that part of matrix
        int x = answerColumn*sgmCellImagePixelSize +
            (answerColumn+1)*pixelsBetweenCells;
        int y = answerRow*sgmCellImagePixelSize +
            (answerRow+1)*pixelsBetweenCells;
        for (int i=0; i<image.getHeight(); i++)
        {
            for (int j=0; j<image.getWidth(); j++)
            {
                this.setRGB(x+j, y+i, image.getRGB(j, i));
            }
        }
    }

    public SGMCellImage[][] getSGMCellImages()
    {
        return this.sgmCellImages;
    }

    protected void setSGMCellImages(
        final SGMCellImage[][] sgmCellImages)
    {
        this.sgmCellImages = sgmCellImages;
    }
}
