/*
 * File:                WhiteSGMFillPattern.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 3, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: WhiteSGMFillPattern.java,v $
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
 * Revision 1.4  2007/12/10 21:59:06  zobenz
 * Cleaned up surface feature generation to improve visual layout
 *
 * Revision 1.3  2007/12/10 19:56:04  zobenz
 * Filled in rest of answer choice generation by randomly manipulating parameters of surface features
 *
 * Revision 1.2  2007/12/06 23:28:33  zobenz
 * Refactored to provide more robust implementation of surface feature transformation, including support for multiple structure features per layer.
 *
 * Revision 1.1  2007/12/04 00:03:40  zobenz
 * Implemented fill pattern attribute of surface features.
 *
 */
 
package gov.sandia.cognition.generator.matrix.fillpattern;

import java.awt.Color;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class WhiteSGMFillPattern extends AbstractSGMFillPattern
{   
    public static final String DESCRIPTION = "White";
    
    public WhiteSGMFillPattern()
    {
        super(new Color(1.0f, 1.0f, 1.0f, 0.0f));
    }
    
    public String getDescription()
    {
        return DESCRIPTION;
    }
}
