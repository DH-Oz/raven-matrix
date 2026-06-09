/*
 * File:                SGMScore.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Nov 6, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: SGMScore.java,v $
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
 * Revision 1.3  2007/11/30 23:10:57  zobenz
 * Work in progress on stochastic SGM generation
 *
 * Revision 1.2  2007/11/30 16:27:52  zobenz
 * Implemented missing hashCode functions; Implemented SGMScore and SGMScoreDistribution
 *
 * Revision 1.1  2007/11/07 16:47:46  zobenz
 * Interim checkin; working on implementing SGM generation code.
 *
 */
 
package gov.sandia.cognition.generator.matrix;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMScore implements Comparable<SGMScore>
{
    private double score;
    
    public SGMScore(
        final double score)
    {
        this.setScore(score);
    }
    
    public double getScore()
    {
        return this.score;
    }
    
    private void setScore(
        final double score)
    {
        this.score = score;
    }
    
    public int compareTo(
        final SGMScore other)
    {
        return Double.compare(this.getScore(), other.getScore());
    }
    
    @Override
    public boolean equals(
        final Object other)
    {
        if ((other == null) || !(other instanceof SGMScore))
        {
            return false;
        }
        else
        {
            return equals((SGMScore)other);
        }        
    }

    @Override
    public int hashCode()
    {
        int hash = 5;
        hash = 53 * hash + (int) (Double.doubleToLongBits(this.score) ^
            (Double.doubleToLongBits(this.score) >>> 32));
        return hash;
    }
    
    public boolean equals(SGMScore other)
    {
        if (other.getScore() == this.getScore())
        {
            return true;
        }
        else
        {
            return false;
        }
    } 


}
