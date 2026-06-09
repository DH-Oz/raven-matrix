/*
 * File:                SGMFillPatternGenerator.java
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
 * $Log: SGMFillPatternGenerator.java,v $
 * Revision 1.1  2010/12/21 15:50:07  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:20:56  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:35  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:26  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.3  2008/11/03 18:50:43  cewarr
 * Added ability to rotate through fill patterns, and two more grey levels so there are 5 fill patterns total.  (bug 1273)
 *
 * Revision 1.2  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.1  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.1  2007/12/04 15:28:31  zobenz
 * Fill patterns stochastically generated.
 *
 */
 
package gov.sandia.cognition.generator.matrix.fillpattern;

import java.util.List;
import java.util.Random;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMFillPatternGenerator
{
    public static SGMFillPattern generateFillPattern(
        final Random random)
    {
        // TODO - through reflection dynamically determine the 
        // SGMFillPatterns available... [20071130 ZOB] this turns out to
        // be extremely non-trivial to do, sadly (although ServiceLoader in Java
        // 6 may help).  One way to do it with reflection can be found here:
        // http://lists.apple.com/archives/Java-dev/2006/Jun/msg00109.html
        
        // Stochastically choose the fill pattern
        SGMFillPattern fillPattern = null;
        int type = random.nextInt(3);
        switch (type)
        {
            case 0:
                fillPattern = new WhiteSGMFillPattern();
                break;
            case 1:
                fillPattern = new Grey75SGMFillPattern();
                break;
            case 2:
                fillPattern = new BlackSGMFillPattern();
                break;
        }
        
        return fillPattern;
    }
    
    public static SGMFillPattern generateFillPattern(
        final List<SGMFillPattern> allowedFillPatterns,
        final Random random)
    {        
        if (allowedFillPatterns == null)
        {
            return generateFillPattern(random);
        }
        
        // Stochastically choose the fill pattern from among those allowed
        return allowedFillPatterns.get(
            random.nextInt(allowedFillPatterns.size()));                        
    }
}
