/*
 * File:                SGMLocationTransformGenerator.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 6, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMLocationTransformGenerator.java,v $
 * Revision 1.2  2010/12/21 16:10:58  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:07  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:20:55  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:38  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:27  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.5  2008/10/07 21:42:05  zobenz
 * Functioning SGM Builder GUI
 *
 * Revision 1.4  2007/12/14 21:40:09  zobenz
 * Implemented TopLeftCornerOutSGMLocationTransform and associated infrastructure improvements
 *
 * Revision 1.3  2007/12/11 17:35:32  zobenz
 * Improved numerosity to use consistent scaling and positioning across cells along location transform
 *
 * Revision 1.2  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.1  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.1  2007/12/06 23:28:33  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 */
 
package gov.sandia.cognition.generator.matrix.locationtransform;

import gov.sandia.cognition.generator.matrix.SGMMatrixSize;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMLocationTransformGenerator
{
    public enum LocationTransformType
    {
        UNSPECIFIED,
        HORIZONTAL,
        VERTICAL,
        DIAGONAL_TOP_LEFT_TO_BOTTOM_RIGHT,
        DIAGONAL_BOTTOM_LEFT_TO_TOP_RIGHT,
        TOP_LEFT_CORNER_OUT;
    }
    
    public static SGMLocationTransform generateLocationTransform(
        final SGMMatrixSize sgmMatrixSize,
        final Random random)
    {
        return generateLocationTransform(sgmMatrixSize, random,
            LocationTransformType.UNSPECIFIED);
    }
    
    public static SGMLocationTransform generateLocationTransform(
        final SGMMatrixSize sgmMatrixSize,
        final Random random,
        final LocationTransformType locationTransformType)
    {
        // TODO - through reflection dynamically determine the 
        // SGMLocationTransforms available... [20071130 ZOB] this turns out to
        // be extremely non-trivial to do, sadly (although ServiceLoader in Java
        // 6 may help).  One way to do it with reflection can be found here:
        // http://lists.apple.com/archives/Java-dev/2006/Jun/msg00109.html
        
        // Stochastically chose the type of location transform       
        SGMLocationTransform locationTransform = null;
        int type = -1;
        if (locationTransformType == LocationTransformType.UNSPECIFIED)
        {
            // Generate stochastically
            if ((sgmMatrixSize.getNumRows() % 2 == 0) ||
                (sgmMatrixSize.getNumRows() != sgmMatrixSize.getNumColumns()))
            {
                // Exclude diagonal location transforms, as they require
                // a square matrix with odd number of rows and columns
                type = random.nextInt(3);
            }
            else
            {
                type = random.nextInt(5);                    
            }
        }
        else if (locationTransformType == LocationTransformType.HORIZONTAL)
        {
            // Horizontal
            type = 0;
        }
        else if (locationTransformType == LocationTransformType.VERTICAL)
        {
            // Vertical
            type = 1;
        }
        else if (locationTransformType == 
            LocationTransformType.TOP_LEFT_CORNER_OUT)
        {
            // Top Left Corner Out
            type = 2;
        }
        else if (locationTransformType == 
            LocationTransformType.DIAGONAL_BOTTOM_LEFT_TO_TOP_RIGHT)
        {
            // Diagnoal Bottom Left to Top Right
            type = 3;
        }
        else
        {
            // Diagonal Top Left to Bottom Right
            type = 4;
        }
        switch (type)
        {
            case 0:
                locationTransform =
                    new HorizontalSGMLocationTransform(sgmMatrixSize);
                break;
            case 1:
                locationTransform =
                    new VerticalSGMLocationTransform(sgmMatrixSize);
                break;
            case 2:
                locationTransform =
                    new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
                break;
            case 3:
                locationTransform = 
                    new DiagonalBottomLeftTopRightSGMLocationTransform(
                    sgmMatrixSize);
                break;
            case 4:
                locationTransform =
                    new DiagonalTopLeftBottomRightSGMLocationTransform(
                    sgmMatrixSize);
                break;   
        }
        
        return locationTransform;
    }
}
