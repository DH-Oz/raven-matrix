/*
 * File:                SGMBaseCell.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 1, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMBaseCell.java,v $
 * Revision 1.3  2010/12/22 21:48:58  zobenz
 * Fixed naming of SGMMatrix
 *
 * Revision 1.2  2010/12/21 16:10:57  zobenz
 * Normalized documentation to match tool name.
 *
 * Revision 1.1  2010/12/21 15:50:05  zobenz
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
 * Revision 1.14  2008/11/05 18:24:26  cewarr
 * Tweaked the grey fill patterns, added two shapes, eliminated squares/circles and repeat use of same shape in a matrix, fixed some problems with wrong answers when numerosity is used.
 *
 * Revision 1.13  2007/12/13 20:57:09  zobenz
 * Finished filling in some documentation that was marked TODO; as an aside, the code currently has a bug if you set max structure features per layer> 1
 *
 * Revision 1.12  2007/12/13 20:53:16  zobenz
 * Implemented XOR and AND; fixed surface feature equality check
 *
 * Revision 1.11  2007/12/10 20:08:48  zobenz
 * Rearranged classes into appropriate packages
 *
 * Revision 1.10  2007/12/05 23:20:47  zobenz
 * Disabled Rotate structure feature while debugging; fixed comparison of SGM cells
 *
 * Revision 1.9  2007/12/05 20:44:55  zobenz
 * Improved answer choice generation; Replaced SetIteration structure feature with Identity structure feature; added Rotate structure feature (which has a bug right now)
 *
 * Revision 1.8  2007/12/04 23:55:19  zobenz
 * Working on generating answer choices; a mechanism is implemented to generate variations on the correct answer, but it is limited.
 *
 * Revision 1.7  2007/11/21 22:28:30  zobenz
 * Implemented SGMMatrix, which is composed of layers; starting work on stochastic generation of SGMs to fit a specified score distribution
 *
 * Revision 1.6  2007/11/21 18:01:08  zobenz
 * SGMLayer implementation completed
 *
 * Revision 1.5  2007/11/13 22:58:55  zobenz
 * Working on infrastructure to get structure features working; almost there
 *
 * Revision 1.4  2007/11/13 20:28:12  zobenz
 * Fixed painting colors; fixed line surface feature; updated proof of concept code
 *
 * Revision 1.3  2007/11/13 18:11:55  zobenz
 * Proof of concept rendering SGMCell to window, bottom to top
 *
 * Revision 1.2  2007/11/12 23:20:39  zobenz
 * Working on being able to render matrices to screen and to bitmap
 *
 * Revision 1.1  2007/11/01 22:57:55  zobenz
 * Initial stubs
 *
 */
 
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.generator.matrix.surface.SGMSurfaceFeature;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMBaseCell implements SGMCell
{
    private List<SGMSurfaceFeature> surfaceFeatures;
    private SGMLocation location;
    
    public SGMBaseCell(
            SGMLocation location,
            List<SGMSurfaceFeature> surfaceFeatures)
    {
        this.setSurfaceFeatures(surfaceFeatures);
        this.setLocation(location);
    }
    
    public SGMBaseCell(
            SGMLocation location,
            SGMSurfaceFeature... surfaceFeatures)
    {
        this(location, Arrays.asList(surfaceFeatures));
    }
    
    public SGMLocation getLocation()
    {
        return this.location;
    }

    public List<SGMSurfaceFeature> getSurfaceFeatures()
    {
        return this.surfaceFeatures;
    }

    protected void setSurfaceFeatures(
        List<SGMSurfaceFeature> surfaceFeatures)
    {
        this.surfaceFeatures = surfaceFeatures;
    }

    protected void setLocation(SGMLocation location)
    {
        this.location = location;
    }

    public SGMCompositeCell combineWith(SGMCell other)
    {
        // Sanity check on location of cells - needs to be the same
        if (!this.getLocation().equals(other.getLocation()))
        {
            throw new SGMLocationMismatchException(
                "SGMCells must be located at same SGMLocation: " +
                "(" + this.getLocation().getRow() +
                "," + this.getLocation().getColumn() + ") !=" +
                "(" + other.getLocation().getRow() +
                "," + other.getLocation().getColumn() + ")");            
        }
        
        return this.combineWithIgnoringLocation(other);        
    }
    
    public SGMCompositeCell combineWithIgnoringLocation(SGMCell other)
    {                
        // Combine surface features from the this and the other cell
        List<SGMSurfaceFeature> combinedSurfaceFeatures = new
            ArrayList<SGMSurfaceFeature>(this.getSurfaceFeatures().size() +
            other.getSurfaceFeatures().size());
        combinedSurfaceFeatures.addAll(this.getSurfaceFeatures());
        combinedSurfaceFeatures.addAll(other.getSurfaceFeatures());
                
        return new SGMCompositeCell(this.getLocation(),
            combinedSurfaceFeatures);
    }

    @Override
    public boolean equals(Object other)
    {
        if ((other == null) || !(other instanceof SGMCell))
        {
            return false;
        }
        else
        {
            return equals((SGMCell)other);
        }    
    }

    @Override
    public int hashCode()
    {
        int hash = 7;
        hash = 29 * hash + (this.surfaceFeatures != null ? this.surfaceFeatures.hashCode() : 0);
        hash = 29 * hash + (this.location != null ? this.location.hashCode() : 0);
        return hash;
    }
    
    private boolean containsFeatureCheck(
            final SGMSurfaceFeature feature,
            List<SGMSurfaceFeature> surfaceFeature)
    {
        for (SGMSurfaceFeature otherFeature : surfaceFeatures)
        {
            if (feature.equals(otherFeature))
            {
                return true;
            }
        }
        return false;
    }
    
    public boolean equals(SGMCell other)
    {
        // Built-in List contains check is wrong thing to do here (which is 
        // why we don't do it) - don't want that it contains the same object
        // reference, but rather that there is some surface feature that
        // fundamentally _equals_ this surface feature in terms of its 
        // properties
        
        // TODO - this is inefficient - optimize it
        
        if (this.getSurfaceFeatures().size() != other.getSurfaceFeatures().size())
            return false;
        
        for (SGMSurfaceFeature feature : other.getSurfaceFeatures())
        {
            if (!containsFeatureCheck(feature, this.getSurfaceFeatures()))
            {
                return false;
            }
        }
        for (SGMSurfaceFeature feature: this.getSurfaceFeatures())
        {
            if (!containsFeatureCheck(feature, other.getSurfaceFeatures()))
            {
                return false;
            }
        }
        return true;               
    } 
}
