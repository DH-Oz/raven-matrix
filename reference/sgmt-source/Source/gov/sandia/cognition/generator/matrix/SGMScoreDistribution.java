/*
 * File:                SGMScoreDistribution.java
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
 * $Log: SGMScoreDistribution.java,v $
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
 * Revision 1.5  2010/11/12 16:42:19  jdbasil
 * Fixed build error from change to data histograms.
 *
 * Revision 1.4  2009/05/29 22:02:40  jdbasil
 * Updated from changes to binning.
 *
 * Revision 1.3  2007/11/30 23:10:58  zobenz
 * Work in progress on stochastic SGM generation
 *
 * Revision 1.2  2007/11/30 16:27:52  zobenz
 * Implemented missing hashCode functions; Implemented SGMScore and SGMScoreDistribution
 *
 */
 
package gov.sandia.cognition.generator.matrix;

import gov.sandia.cognition.statistics.distribution.DataCountTreeSetBinnedMapHistogram;
import java.util.Map;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class SGMScoreDistribution
{
    private DataCountTreeSetBinnedMapHistogram<SGMScore> bins;
    private Map<SGMScore, Integer> binSizeLimits;
    
    public SGMScoreDistribution(
        final DataCountTreeSetBinnedMapHistogram<SGMScore> bins,
        final Map<SGMScore, Integer> binSizeLimits)
    {
        // Sanity check to make sure we were provided correct number
        // of bin size limits
        if (bins.getBinCount() != binSizeLimits.keySet().size())
        {                       
            throw new IllegalArgumentException("Number of bins must" +
                "be the same as the number of bin size limits provided");            
        }
        else
        {
            this.setBins(bins);
            this.setBinSizeLimits(binSizeLimits);            
        }        
    }   
    
    public boolean addSGMScore(
        final SGMScore sgmScore)
    {
        // Check to see if we've hit limit for the bin this SGM score
        // goes in to
        SGMScore bin = this.bins.getBinner().findBin(sgmScore);
        if (this.getBins().getCount(bin) >= this.getBinSizeLimits().get(bin))
        {        
            // Limit hit, reject
            return false;
        }
        else
        {
            // Still room, accept and insert
            this.getBins().add(sgmScore);
            return true;
        }
    }
    
    public boolean distributionAchieved()
    {
        boolean achieved = true;
                
        // Check to see if each bin is filled
        for (SGMScore bin : this.getBins().getDomain())
        {
            if (this.getBins().getCount(bin) < this.getBinSizeLimits().get(bin))
            {
                // Current bin is not filled, so distribution not achieved
                achieved = false;
                break;
            }
        }
        
        return achieved;
    }

    private DataCountTreeSetBinnedMapHistogram<SGMScore> getBins()
    {
        return bins;
    }

    private void setBins(
        DataCountTreeSetBinnedMapHistogram<SGMScore> bins)
    {
        this.bins = bins;
    }

    private Map<SGMScore, Integer> getBinSizeLimits()
    {
        return binSizeLimits;
    }

    private void setBinSizeLimits(
        final Map<SGMScore, Integer> binSizeLimits)
    {
        this.binSizeLimits = binSizeLimits;
    }
}
