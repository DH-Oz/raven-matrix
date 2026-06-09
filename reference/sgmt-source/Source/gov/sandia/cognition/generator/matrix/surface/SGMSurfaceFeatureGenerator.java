/*
 * File:                SGMSurfaceFeatureGenerator.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 30, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMSurfaceFeatureGenerator.java,v $
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
 * Revision 1.10  2008/11/05 18:24:26  cewarr
 * Tweaked the grey fill patterns, added two shapes, eliminated squares/circles and repeat use of same shape in a matrix, fixed some problems with wrong answers when numerosity is used.
 *
 * Revision 1.9  2008/10/15 19:02:29  zobenz
 * Added tee and triangle surface features, which are both kinds of a path based surface feature
 *
 * Revision 1.8  2008/10/15 17:49:03  zobenz
 * Made surface feature sizes more visually distinct.
 *
 * Revision 1.7  2008/10/15 16:28:49  zobenz
 * Minor GUI updates; preparing to add new surface features
 *
 * Revision 1.6  2008/02/27 16:15:09  zobenz
 * Exposed each individual level + VIL in AnalogyModel; tweaked SGM generation
 *
 * Revision 1.5  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.4  2007/12/11 15:20:27  zobenz
 * Fixed scaling transform when rendering cell; adjusted scaling setting in numerosity; removed various debug statements
 *
 * Revision 1.3  2007/12/10 21:59:05  zobenz
 * Cleaned up surface feature generation to improve visual layout
 *
 * Revision 1.2  2007/12/10 20:11:07  zobenz
 * Fixed imports
 *
 * Revision 1.1  2007/12/10 20:08:47  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.8  2007/12/06 19:04:41  zobenz
 * Committing working implementation in preparation for overhauling way in which structure features are applied
 *
 * Revision 1.7  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.6  2007/12/05 20:44:55  zobenz
 * Improved answer choice generation; Replaced SetIteration structure feature with Identity structure feature; added Rotate structure feature (which has a bug right now)
 *
 * Revision 1.5  2007/12/04 18:34:20  zobenz
 * Changed stochastic rotation generation to be in increments of pi/2
 *
 * Revision 1.4  2007/12/04 15:28:31  zobenz
 * Fill patterns stochastically generated.
 *
 * Revision 1.3  2007/12/04 00:03:40  zobenz
 * Implemented fill pattern attribute of surface features.
 *
 * Revision 1.2  2007/12/03 23:09:21  zobenz
 * Initial implementation of a complete top to bottom stochastic generation of SGMs
 *
 * Revision 1.1  2007/11/30 23:10:58  zobenz
 * Work in progress on stochastic SGM generation
 *
 */
 
package gov.sandia.cognition.generator.matrix.surface;

import gov.sandia.cognition.generator.matrix.SGMPoint;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPattern;
import gov.sandia.cognition.generator.matrix.fillpattern.SGMFillPatternGenerator;
import java.util.List;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMSurfaceFeatureGenerator
{   
    public static SGMSurfaceFeature generateSurfaceFeature(
        final int sgmCellImagePixelSize,
        final Random random)                
    {
        return generateSurfaceFeature(sgmCellImagePixelSize, null, random);
    }
    
    public static SGMSurfaceFeature generateSurfaceFeature(
        final int sgmCellImagePixelSize,
        final List<SGMFillPattern> allowedFillPatterns,
        final Random random)                
    {
        // TODO - through reflection dynamically determine the 
        // SGMSurfaceFeatures available... [20071130 ZOB] this turns out to
        // be extremely non-trivial to do, sadly (although ServiceLoader in Java
        // 6 may help).  One way to do it with reflection can be found here:
        // http://lists.apple.com/archives/Java-dev/2006/Jun/msg00109.html
                    
        SGMSurfaceFeature surfaceFeature = null;
        double halfCellImagePixelSize = sgmCellImagePixelSize / 2.0;
        double quarterCellImagePixelSize = halfCellImagePixelSize / 2.0;
        double eigthCellImagePixelSize = quarterCellImagePixelSize / 2.0;        
        
        // Width and height set to 1/4, 1/2, or 3/4 the cell image pixel size,
        // with at least one of the dimensions > 1/2 thce cell image pixel size
        // But disallow width=height (squares, circles...)
        double width = (((double)random.nextInt(3)) * quarterCellImagePixelSize) 
            + quarterCellImagePixelSize;
        double height;
        if (width == 2*quarterCellImagePixelSize)
            height = 3*quarterCellImagePixelSize;
        else if (width == 3*quarterCellImagePixelSize)
            height = 2*quarterCellImagePixelSize;
        else    
            height = (((double)random.nextInt(2)) * quarterCellImagePixelSize)
                + halfCellImagePixelSize;           
        if (random.nextBoolean())
        {
            double temp = width;
            width = height;
            height = temp;
        }
        
        // Always set initial rotation to 0
        int rotation = 0;
        
        // Always locate at center to begin with
        SGMPoint sgmPoint =
            new SGMPoint(halfCellImagePixelSize, halfCellImagePixelSize);
        
        // Stochastically choose a fill pattern
        SGMFillPattern fillPattern =
            SGMFillPatternGenerator.generateFillPattern(allowedFillPatterns,
            random);
        
        // Stochastically choose the type of surface feature
        int type = random.nextInt(6);            
        switch (type)
        {
            case 0:                                        
                surfaceFeature =
                    new EllipseSGMSurfaceFeature(width, height, rotation,
                    sgmPoint, fillPattern);
                break;
            case 1:
                surfaceFeature =
                    new RectangleSGMSurfaceFeature(width, height, rotation,
                    sgmPoint, fillPattern);
                break;
            case 2:
                surfaceFeature =
                    new TriangleSGMSurfaceFeature(width, height, rotation,
                    sgmPoint, fillPattern);
                break;
            case 3:
                surfaceFeature =
                    new TeeSGMSurfaceFeature(width, height, rotation,
                    sgmPoint, fillPattern);
                break;
            case 4:
                surfaceFeature = 
                    new DiamondSGMSurfaceFeature(width, height, rotation,
                    sgmPoint, fillPattern);
                break;
            case 5:
                surfaceFeature = 
                    new TrapezoidSGMSurfaceFeature(width, height, rotation,
                    sgmPoint, fillPattern);
                break;
//            case 4:
//                surfaceFeature =
//                    new LineSGMSurfaceFeature(width, rotation, sgmPoint,
//                    fillPattern);
//                break;                
        }        
        
        return surfaceFeature;
    }
}
