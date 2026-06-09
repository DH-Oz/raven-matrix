/*
 * File:                Grey25SGMFillPattern.java
 * Authors:             Christina Warrender
 * Company:             Sandia National Laboratories
 * Project:             Cognitive Foundry
 * 
 * Copyright November 03, 2008, Sandia Corporation.
 * Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive 
 * license for use of this work by or on behalf of the U.S. Government. Export 
 * of this program may require a license from the United States Government. 
 * See CopyrightHistory.txt for complete details.
 * 
 * Revision History:
 * 
 * $Log: Grey10SGMFillPattern.java,v $
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
 * Revision 1.1  2008/11/05 18:24:26  cewarr
 * Tweaked the grey fill patterns, added two shapes, eliminated squares/circles and repeat use of same shape in a matrix, fixed some problems with wrong answers when numerosity is used.
 *
 * Revision 1.1  2008/11/03 18:50:43  cewarr
 * Added ability to rotate through fill patterns, and two more grey levels so there are 5 fill patterns total.  (bug 1273)
 *
 */

package gov.sandia.cognition.generator.matrix.fillpattern;

import java.awt.Color;

/**
 * @TODO    Document this.
 * 
 * @author  Christina Warrender
 * @since   2.1
 */
public class Grey10SGMFillPattern extends AbstractSGMFillPattern
{
    public static final String DESCRIPTION = "Red";
    
    public Grey10SGMFillPattern()
    {
        super(new Color(0.1f, 0.1f, 0.1f, 0.6f));
    }
    
    public String getDescription()
    {
        return DESCRIPTION;
    }
}
