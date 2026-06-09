/*
 * File:                TopLeftCornerOutSGMLocationTransformTest.java
 * Authors:             zobenz
 * Company:             Sandia National Laboratories
 * Project:             Analogy LDRD
 * 
 * Copyright Dec 14, 2007, Sandia Corporation.  Under the terms of Contract 
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
 * $Log: TopLeftCornerOutSGMLocationTransformTest.java,v $
 * Revision 1.1  2010/12/21 15:50:08  zobenz
 * Migrated matrix generation code into standalone project
 *
 * Revision 1.1  2010/12/20 23:21:09  zobenz
 * Went from sgm package namespace to generator.matrix
 *
 * Revision 1.1  2010/12/20 18:58:41  zobenz
 * Renamed packages in preparation for migrating SGM code out to separate SGMT project.
 *
 * Revision 1.1  2010/12/20 17:52:32  zobenz
 * Refactoring to conform to Sandia Generated Matrix name for tool.
 *
 * Revision 1.2  2007/12/17 22:02:26  zobenz
 * Finished implementing unit test
 *
 * Revision 1.1  2007/12/14 21:40:09  zobenz
 * Implemented TopLeftCornerOutSGMLocationTransform and associated infrastructure improvements
 *
 */
 
package gov.sandia.cognition.generator.matrix.locationtransform;

import gov.sandia.cognition.generator.matrix.locationtransform.TopLeftCornerOutSGMLocationTransform;
import gov.sandia.cognition.generator.matrix.SGMLocation;
import gov.sandia.cognition.generator.matrix.SGMMatrixSize;
import java.util.ArrayList;
import java.util.List;
import junit.framework.TestCase;

/**
 * @TODO - add description
 *
 * @author zobenz
 * @since 2.0
 */
public class TopLeftCornerOutSGMLocationTransformTest extends TestCase {
    
    public TopLeftCornerOutSGMLocationTransformTest(String testName) {
        super(testName);
    }            

    @Override
    protected void setUp() throws Exception {
        super.setUp();
    }

    @Override
    protected void tearDown() throws Exception {
        super.tearDown();
    }

    /**
     * Test of populateBaseLocations method, of class TopLeftCornerOutSGMLocationTransform.
     */
    public void testPopulateBaseLocations()
    {
        System.out.println("populateBaseLocations");
        
        // 3x3
        SGMMatrixSize sgmMatrixSize = new SGMMatrixSize(3, 3);
        TopLeftCornerOutSGMLocationTransform instance =
            new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        SGMLocation baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);       
        
        // 1x1
        sgmMatrixSize = new SGMMatrixSize(1, 1);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);    
        
        // 1x4
        sgmMatrixSize = new SGMMatrixSize(1, 4);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);  
        
        // 4x1
        sgmMatrixSize = new SGMMatrixSize(4, 1);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);  
        
        // 2x4        
        sgmMatrixSize = new SGMMatrixSize(2, 4);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);  
        
        // 4x2
        sgmMatrixSize = new SGMMatrixSize(4, 2);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);
        
        // 3x5
        sgmMatrixSize = new SGMMatrixSize(3, 5);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);  
        
        // 10x3
        sgmMatrixSize = new SGMMatrixSize(10, 3);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        assertEquals(instance.getBaseLocations().size(), 1);
        baseLocation = instance.getBaseLocations().get(0);
        assertEquals(baseLocation.getRow(), 0);
        assertEquals(baseLocation.getColumn(), 0);  
    }

    /**
     * Test of createNextLocation method, of class TopLeftCornerOutSGMLocationTransform.
     */
    public void testCreateNextLocation()
    {        
        System.out.println("createNextLocation");
        
        // 3x3
        SGMMatrixSize sgmMatrixSize = new SGMMatrixSize(3, 3);
        List<SGMLocation> sgmLocations = new ArrayList<SGMLocation>(8);
        TopLeftCornerOutSGMLocationTransform instance =
            new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        SGMLocation baseLocation = instance.getBaseLocations().get(0);
        SGMLocation currentLocation =
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 8);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 0);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 1);
        assertEquals(sgmLocations.get(2).getColumn(), 0);
        assertEquals(sgmLocations.get(3).getRow(), 0);
        assertEquals(sgmLocations.get(3).getColumn(), 1);
        assertEquals(sgmLocations.get(4).getRow(), 0);
        assertEquals(sgmLocations.get(4).getColumn(), 1);
        assertEquals(sgmLocations.get(5).getRow(), 1);
        assertEquals(sgmLocations.get(5).getColumn(), 1);
        assertEquals(sgmLocations.get(6).getRow(), 0);
        assertEquals(sgmLocations.get(6).getColumn(), 2);
        assertEquals(sgmLocations.get(7).getRow(), 1);
        assertEquals(sgmLocations.get(7).getColumn(), 2);
                
        // 1x1
        sgmMatrixSize = new SGMMatrixSize(1, 1);
        sgmLocations = new ArrayList<SGMLocation>(0);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);        
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 0);
        
        // 1x4
        sgmMatrixSize = new SGMMatrixSize(1, 4);
        sgmLocations = new ArrayList<SGMLocation>(3);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);        
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 3);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 0);
        assertEquals(sgmLocations.get(1).getColumn(), 1);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 2);
        
        // 4x1
        sgmMatrixSize = new SGMMatrixSize(4, 1);
        sgmLocations = new ArrayList<SGMLocation>(3);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);        
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 3);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 1);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 2);
        assertEquals(sgmLocations.get(2).getColumn(), 0);
                
        // 2x4
        sgmMatrixSize = new SGMMatrixSize(2, 4);
        sgmLocations = new ArrayList<SGMLocation>(7);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);        
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 7);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 0);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 1);
        assertEquals(sgmLocations.get(3).getRow(), 0);
        assertEquals(sgmLocations.get(3).getColumn(), 1);
        assertEquals(sgmLocations.get(4).getRow(), 0);
        assertEquals(sgmLocations.get(4).getColumn(), 2);
        assertEquals(sgmLocations.get(5).getRow(), 0);
        assertEquals(sgmLocations.get(5).getColumn(), 2);
        assertEquals(sgmLocations.get(6).getRow(), 0);
        assertEquals(sgmLocations.get(6).getColumn(), 3);
        
        // 4x2
        sgmMatrixSize = new SGMMatrixSize(4, 2);
        sgmLocations = new ArrayList<SGMLocation>(7);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);        
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 7);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 0);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 1);
        assertEquals(sgmLocations.get(2).getColumn(), 0);
        assertEquals(sgmLocations.get(3).getRow(), 0);
        assertEquals(sgmLocations.get(3).getColumn(), 1);
        assertEquals(sgmLocations.get(4).getRow(), 2);
        assertEquals(sgmLocations.get(4).getColumn(), 0);
        assertEquals(sgmLocations.get(5).getRow(), 1);
        assertEquals(sgmLocations.get(5).getColumn(), 1);
        assertEquals(sgmLocations.get(6).getRow(), 2);
        assertEquals(sgmLocations.get(6).getColumn(), 1);
        
        // 3x5
        sgmMatrixSize = new SGMMatrixSize(3, 5);
        sgmLocations = new ArrayList<SGMLocation>(14);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);        
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 14);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 0);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 1);
        assertEquals(sgmLocations.get(2).getColumn(), 0);
        assertEquals(sgmLocations.get(3).getRow(), 0);
        assertEquals(sgmLocations.get(3).getColumn(), 1);
        assertEquals(sgmLocations.get(4).getRow(), 0);
        assertEquals(sgmLocations.get(4).getColumn(), 1);
        assertEquals(sgmLocations.get(5).getRow(), 1);
        assertEquals(sgmLocations.get(5).getColumn(), 1);
        assertEquals(sgmLocations.get(6).getRow(), 0);
        assertEquals(sgmLocations.get(6).getColumn(), 2);
        assertEquals(sgmLocations.get(7).getRow(), 0);
        assertEquals(sgmLocations.get(7).getColumn(), 2);
        assertEquals(sgmLocations.get(8).getRow(), 1);
        assertEquals(sgmLocations.get(8).getColumn(), 2);
        assertEquals(sgmLocations.get(9).getRow(), 0);
        assertEquals(sgmLocations.get(9).getColumn(), 3);
        assertEquals(sgmLocations.get(10).getRow(), 0);
        assertEquals(sgmLocations.get(10).getColumn(), 3);
        assertEquals(sgmLocations.get(11).getRow(), 1);
        assertEquals(sgmLocations.get(11).getColumn(), 3);
        assertEquals(sgmLocations.get(12).getRow(), 0);
        assertEquals(sgmLocations.get(12).getColumn(), 4);
        assertEquals(sgmLocations.get(13).getRow(), 1);
        assertEquals(sgmLocations.get(13).getColumn(), 4);
        
        // 10x3
        sgmMatrixSize = new SGMMatrixSize(10, 3);
        sgmLocations = new ArrayList<SGMLocation>(29);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);        
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(instance.
                getParentLocationForStructureFeatureUse(currentLocation));
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 29);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 0);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 1);
        assertEquals(sgmLocations.get(2).getColumn(), 0);
        assertEquals(sgmLocations.get(3).getRow(), 0);
        assertEquals(sgmLocations.get(3).getColumn(), 1);
        assertEquals(sgmLocations.get(4).getRow(), 0);
        assertEquals(sgmLocations.get(4).getColumn(), 1);
        assertEquals(sgmLocations.get(5).getRow(), 2);
        assertEquals(sgmLocations.get(5).getColumn(), 0);
        assertEquals(sgmLocations.get(6).getRow(), 1);
        assertEquals(sgmLocations.get(6).getColumn(), 1);
        assertEquals(sgmLocations.get(7).getRow(), 0);
        assertEquals(sgmLocations.get(7).getColumn(), 2);
        assertEquals(sgmLocations.get(8).getRow(), 3);
        assertEquals(sgmLocations.get(8).getColumn(), 0);
        assertEquals(sgmLocations.get(9).getRow(), 2);
        assertEquals(sgmLocations.get(9).getColumn(), 1);
        assertEquals(sgmLocations.get(10).getRow(), 1);
        assertEquals(sgmLocations.get(10).getColumn(), 2);
        assertEquals(sgmLocations.get(11).getRow(), 4);
        assertEquals(sgmLocations.get(11).getColumn(), 0);
        assertEquals(sgmLocations.get(12).getRow(), 3);
        assertEquals(sgmLocations.get(12).getColumn(), 1);
        assertEquals(sgmLocations.get(13).getRow(), 2);
        assertEquals(sgmLocations.get(13).getColumn(), 2);
        assertEquals(sgmLocations.get(14).getRow(), 5);
        assertEquals(sgmLocations.get(14).getColumn(), 0);
        assertEquals(sgmLocations.get(15).getRow(), 4);
        assertEquals(sgmLocations.get(15).getColumn(), 1);
        assertEquals(sgmLocations.get(16).getRow(), 3);
        assertEquals(sgmLocations.get(16).getColumn(), 2);
        assertEquals(sgmLocations.get(17).getRow(), 6);
        assertEquals(sgmLocations.get(17).getColumn(), 0);
        assertEquals(sgmLocations.get(18).getRow(), 5);
        assertEquals(sgmLocations.get(18).getColumn(), 1);
        assertEquals(sgmLocations.get(19).getRow(), 4);
        assertEquals(sgmLocations.get(19).getColumn(), 2);
        assertEquals(sgmLocations.get(20).getRow(), 7);
        assertEquals(sgmLocations.get(20).getColumn(), 0);
        assertEquals(sgmLocations.get(21).getRow(), 6);
        assertEquals(sgmLocations.get(21).getColumn(), 1);
        assertEquals(sgmLocations.get(22).getRow(), 5);
        assertEquals(sgmLocations.get(22).getColumn(), 2);
        assertEquals(sgmLocations.get(23).getRow(), 8);
        assertEquals(sgmLocations.get(23).getColumn(), 0);
        assertEquals(sgmLocations.get(24).getRow(), 7);
        assertEquals(sgmLocations.get(24).getColumn(), 1);
        assertEquals(sgmLocations.get(25).getRow(), 6);
        assertEquals(sgmLocations.get(25).getColumn(), 2);
        assertEquals(sgmLocations.get(26).getRow(), 8);
        assertEquals(sgmLocations.get(26).getColumn(), 1);
        assertEquals(sgmLocations.get(27).getRow(), 7);
        assertEquals(sgmLocations.get(27).getColumn(), 2);
        assertEquals(sgmLocations.get(28).getRow(), 8);
        assertEquals(sgmLocations.get(28).getColumn(), 2);
    }

    /**
     * Test of getParentLocationForStructureFeatureUse method, of class TopLeftCornerOutSGMLocationTransform.
     */
    public void testGetParentLocationForStructureFeatureUse()
    {
        System.out.println("getParentLocationForStructureFeatureUse");
        
        // 3x3
        SGMMatrixSize sgmMatrixSize = new SGMMatrixSize(3, 3);
        List<SGMLocation> sgmLocations = new ArrayList<SGMLocation>(9);
        TopLeftCornerOutSGMLocationTransform instance =
            new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        SGMLocation baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        SGMLocation currentLocation =
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 9);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 1);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 1);
        assertEquals(sgmLocations.get(3).getRow(), 2);
        assertEquals(sgmLocations.get(3).getColumn(), 0);
        assertEquals(sgmLocations.get(4).getRow(), 1);
        assertEquals(sgmLocations.get(4).getColumn(), 1);
        assertEquals(sgmLocations.get(5).getRow(), 0);
        assertEquals(sgmLocations.get(5).getColumn(), 2);
        assertEquals(sgmLocations.get(6).getRow(), 2);
        assertEquals(sgmLocations.get(6).getColumn(), 1);
        assertEquals(sgmLocations.get(7).getRow(), 1);
        assertEquals(sgmLocations.get(7).getColumn(), 2);
        assertEquals(sgmLocations.get(8).getRow(), 2);
        assertEquals(sgmLocations.get(8).getColumn(), 2);
                
        // 1x1
        sgmMatrixSize = new SGMMatrixSize(1, 1);
        sgmLocations = new ArrayList<SGMLocation>(1);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 1);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        
        // 1x4
        sgmMatrixSize = new SGMMatrixSize(1, 4);
        sgmLocations = new ArrayList<SGMLocation>(4);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 4);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 0);
        assertEquals(sgmLocations.get(1).getColumn(), 1);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 2);
        assertEquals(sgmLocations.get(3).getRow(), 0);
        assertEquals(sgmLocations.get(3).getColumn(), 3);
        
        // 4x1
        sgmMatrixSize = new SGMMatrixSize(4, 1);
        sgmLocations = new ArrayList<SGMLocation>(4);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 4);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 1);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 2);
        assertEquals(sgmLocations.get(2).getColumn(), 0);
        assertEquals(sgmLocations.get(3).getRow(), 3);
        assertEquals(sgmLocations.get(3).getColumn(), 0);
                
        // 2x4
        sgmMatrixSize = new SGMMatrixSize(2, 4);
        sgmLocations = new ArrayList<SGMLocation>(8);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 8);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 1);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 1);
        assertEquals(sgmLocations.get(3).getRow(), 1);
        assertEquals(sgmLocations.get(3).getColumn(), 1);
        assertEquals(sgmLocations.get(4).getRow(), 0);
        assertEquals(sgmLocations.get(4).getColumn(), 2);
        assertEquals(sgmLocations.get(5).getRow(), 1);
        assertEquals(sgmLocations.get(5).getColumn(), 2);
        assertEquals(sgmLocations.get(6).getRow(), 0);
        assertEquals(sgmLocations.get(6).getColumn(), 3);
        assertEquals(sgmLocations.get(7).getRow(), 1);
        assertEquals(sgmLocations.get(7).getColumn(), 3);
        
        // 4x2
        sgmMatrixSize = new SGMMatrixSize(4, 2);
        sgmLocations = new ArrayList<SGMLocation>(8);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 8);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 1);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 1);
        assertEquals(sgmLocations.get(3).getRow(), 2);
        assertEquals(sgmLocations.get(3).getColumn(), 0);
        assertEquals(sgmLocations.get(4).getRow(), 1);
        assertEquals(sgmLocations.get(4).getColumn(), 1);
        assertEquals(sgmLocations.get(5).getRow(), 3);
        assertEquals(sgmLocations.get(5).getColumn(), 0);
        assertEquals(sgmLocations.get(6).getRow(), 2);
        assertEquals(sgmLocations.get(6).getColumn(), 1);
        assertEquals(sgmLocations.get(7).getRow(), 3);
        assertEquals(sgmLocations.get(7).getColumn(), 1);
        
        // 3x5
        sgmMatrixSize = new SGMMatrixSize(3, 5);
        sgmLocations = new ArrayList<SGMLocation>(15);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 15);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 1);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 1);
        assertEquals(sgmLocations.get(3).getRow(), 2);
        assertEquals(sgmLocations.get(3).getColumn(), 0);
        assertEquals(sgmLocations.get(4).getRow(), 1);
        assertEquals(sgmLocations.get(4).getColumn(), 1);
        assertEquals(sgmLocations.get(5).getRow(), 0);
        assertEquals(sgmLocations.get(5).getColumn(), 2);
        assertEquals(sgmLocations.get(6).getRow(), 2);
        assertEquals(sgmLocations.get(6).getColumn(), 1);
        assertEquals(sgmLocations.get(7).getRow(), 1);
        assertEquals(sgmLocations.get(7).getColumn(), 2);
        assertEquals(sgmLocations.get(8).getRow(), 0);
        assertEquals(sgmLocations.get(8).getColumn(), 3);
        assertEquals(sgmLocations.get(9).getRow(), 2);
        assertEquals(sgmLocations.get(9).getColumn(), 2);
        assertEquals(sgmLocations.get(10).getRow(), 1);
        assertEquals(sgmLocations.get(10).getColumn(), 3);
        assertEquals(sgmLocations.get(11).getRow(), 0);
        assertEquals(sgmLocations.get(11).getColumn(), 4);
        assertEquals(sgmLocations.get(12).getRow(), 2);
        assertEquals(sgmLocations.get(12).getColumn(), 3);
        assertEquals(sgmLocations.get(13).getRow(), 1);
        assertEquals(sgmLocations.get(13).getColumn(), 4);
        assertEquals(sgmLocations.get(14).getRow(), 2);
        assertEquals(sgmLocations.get(14).getColumn(), 4);
        
        // 10x3
        sgmMatrixSize = new SGMMatrixSize(10, 3);
        sgmLocations = new ArrayList<SGMLocation>(30);
        instance = new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        instance.populateBaseLocations();        
        baseLocation = instance.getBaseLocations().get(0);
        sgmLocations.add(baseLocation);
        currentLocation = 
            instance.createNextLocation(baseLocation);
        while (!currentLocation.equals(baseLocation))
        {
            sgmLocations.add(currentLocation);
            currentLocation = instance.createNextLocation(currentLocation);
        }        
        assertEquals(sgmLocations.size(), 30);
        assertEquals(sgmLocations.get(0).getRow(), 0);
        assertEquals(sgmLocations.get(0).getColumn(), 0);
        assertEquals(sgmLocations.get(1).getRow(), 1);
        assertEquals(sgmLocations.get(1).getColumn(), 0);
        assertEquals(sgmLocations.get(2).getRow(), 0);
        assertEquals(sgmLocations.get(2).getColumn(), 1);
        assertEquals(sgmLocations.get(3).getRow(), 2);
        assertEquals(sgmLocations.get(3).getColumn(), 0);
        assertEquals(sgmLocations.get(4).getRow(), 1);
        assertEquals(sgmLocations.get(4).getColumn(), 1);
        assertEquals(sgmLocations.get(5).getRow(), 0);
        assertEquals(sgmLocations.get(5).getColumn(), 2);
        assertEquals(sgmLocations.get(6).getRow(), 3);
        assertEquals(sgmLocations.get(6).getColumn(), 0);
        assertEquals(sgmLocations.get(7).getRow(), 2);
        assertEquals(sgmLocations.get(7).getColumn(), 1);
        assertEquals(sgmLocations.get(8).getRow(), 1);
        assertEquals(sgmLocations.get(8).getColumn(), 2);
        assertEquals(sgmLocations.get(9).getRow(), 4);
        assertEquals(sgmLocations.get(9).getColumn(), 0);
        assertEquals(sgmLocations.get(10).getRow(), 3);
        assertEquals(sgmLocations.get(10).getColumn(), 1);
        assertEquals(sgmLocations.get(11).getRow(), 2);
        assertEquals(sgmLocations.get(11).getColumn(), 2);
        assertEquals(sgmLocations.get(12).getRow(), 5);
        assertEquals(sgmLocations.get(12).getColumn(), 0);
        assertEquals(sgmLocations.get(13).getRow(), 4);
        assertEquals(sgmLocations.get(13).getColumn(), 1);
        assertEquals(sgmLocations.get(14).getRow(), 3);
        assertEquals(sgmLocations.get(14).getColumn(), 2);
        assertEquals(sgmLocations.get(15).getRow(), 6);
        assertEquals(sgmLocations.get(15).getColumn(), 0);
        assertEquals(sgmLocations.get(16).getRow(), 5);
        assertEquals(sgmLocations.get(16).getColumn(), 1);
        assertEquals(sgmLocations.get(17).getRow(), 4);
        assertEquals(sgmLocations.get(17).getColumn(), 2);
        assertEquals(sgmLocations.get(18).getRow(), 7);
        assertEquals(sgmLocations.get(18).getColumn(), 0);
        assertEquals(sgmLocations.get(19).getRow(), 6);
        assertEquals(sgmLocations.get(19).getColumn(), 1);
        assertEquals(sgmLocations.get(20).getRow(), 5);
        assertEquals(sgmLocations.get(20).getColumn(), 2);
        assertEquals(sgmLocations.get(21).getRow(), 8);
        assertEquals(sgmLocations.get(21).getColumn(), 0);
        assertEquals(sgmLocations.get(22).getRow(), 7);
        assertEquals(sgmLocations.get(22).getColumn(), 1);
        assertEquals(sgmLocations.get(23).getRow(), 6);
        assertEquals(sgmLocations.get(23).getColumn(), 2);
        assertEquals(sgmLocations.get(24).getRow(), 9);
        assertEquals(sgmLocations.get(24).getColumn(), 0);
        assertEquals(sgmLocations.get(25).getRow(), 8);
        assertEquals(sgmLocations.get(25).getColumn(), 1);
        assertEquals(sgmLocations.get(26).getRow(), 7);
        assertEquals(sgmLocations.get(26).getColumn(), 2);
        assertEquals(sgmLocations.get(27).getRow(), 9);
        assertEquals(sgmLocations.get(27).getColumn(), 1);
        assertEquals(sgmLocations.get(28).getRow(), 8);
        assertEquals(sgmLocations.get(28).getColumn(), 2);
        assertEquals(sgmLocations.get(29).getRow(), 9);
        assertEquals(sgmLocations.get(29).getColumn(), 2);
    }

    /**
     * Test of getDescription method, of class TopLeftCornerOutSGMLocationTransform.
     */
    public void testGetDescription()
    {
        System.out.println("getDescription");
        SGMMatrixSize sgmMatrixSize = new SGMMatrixSize(3, 3);
        TopLeftCornerOutSGMLocationTransform instance =
            new TopLeftCornerOutSGMLocationTransform(sgmMatrixSize);
        String expResult = TopLeftCornerOutSGMLocationTransform.DESCRIPTION;
        String result = instance.getDescription();
        assertEquals(expResult, result);
    }

}
