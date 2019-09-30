import unittest
import writeDataToXPlane as xpr


class Test_Xplane_Remote(unittest.TestCase):
    
    def setUp(self):
        xpr.init_xp_remote()

    def tearDown(self):
        xpr.close_xp_remote()

    @classmethod
    def setUpClass(cls):
        #xpr.init_xp_remote()
        pass
    @classmethod
    def tearDownClass(clss):
        pass


    def test_get_current_altitude(self):
        alti = xpr.get_current_altitude()
        self.assertTrue(900.0 < alti < 1200)

    def test_climb_to(self):
        xpr.climb_to(2000, 500)
    
    #DELETE
    def test_set_current_altitude(self):
        expeted_planned_alti = 2000.0
        xpr.set_planned_altitude(expeted_planned_alti)

        actual_planned_alti = xpr.get_dref(xpr.DREF_AP_SET_ALTI_IN_FEET)
        self.assertEquals(expeted_planned_alti, actual_planned_alti)
    
    #DELETE
    def test_activate_modes(self):
        xpr.activate_mode_vs(True)
    #DELETE
    def test_set_planned_climbrate(self):
        xpr.set_planned_climbrate(200.0)
        xpr.set_planned_climbrate(0.0)

    

    #not an actual test, just here for convenience
    def test_ask_dref_values(self):
        drefs = ['sim/cockpit2/autopilot/altitude_dial_ft',
        ''
        ]
        print('')
        for dref in drefs:
            print(xpr.get_dref(dref))
        self.assertTrue(True)
    
 
if "__main__" == __name__:
    unittest.main()