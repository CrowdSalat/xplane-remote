import unittest
import control_xplane as xpr


class Test_Xplane_Remote(unittest.TestCase):
    
    def setUp(self):
        #xpr.init_xp_remote()
        pass
    def tearDown(self):
        #xpr.close_xp_remote()
        pass

    @classmethod
    def setUpClass(cls):
        xpr.init_xp_remote()
        pass
    @classmethod
    def tearDownClass(cls):
        xpr.close_xp_remote()
        pass

    def test_reset_mission_time(self):
        xpr.rst_msn_time()
        msn_time = xpr.get_dref(xpr.DREF_MISSN_TIME)
        self.assertTrue(msn_time < 2.0)

    def test_get_current_altitude(self):
        alti = xpr.get_current_altitude()
        self.assertTrue(900.0 < alti < 1200)

    def test_climb_to(self):
        xpr.climb_to(10000, 2000)

    def test_climb(self):
        xpr.climb(100,1000)
    
    def test_set_current_altitude(self):
        expeted_planned_alti = 2000.0
        xpr.set_planned_altitude(expeted_planned_alti)

        actual_planned_alti = xpr.get_dref(xpr.DREF_AP_SET_ALTI_IN_FEET)
        self.assertEquals(expeted_planned_alti, actual_planned_alti)
    
    def test_activate_modes(self):
        xpr.activate_mode_vs(True)
        xpr.activate_mode_heading(True)
    
    def test_set_planned_climbrate(self):
        xpr.set_planned_climbrate(200.0)
        xpr.set_planned_climbrate(0.0)

    # direction
    def test_get_heading(self):
        degree = xpr.get_current_heading() 

    def test_set_heading_delta(self):
        xpr.set_heading_delta(10.0)

    def test_set_heading(self):
        xpr.set_heading(0.0)

    def test_fly_banks(self):
        xpr.fly_banks()

    # maneuver definition
    def test_maneuver_def(self):
        start_altitude = 1000
        climb = 200
        climb_rate = 200 
        heading_change = 0 
        bank_angle = 0
        expected_maneuver = {
          "start_altitude": start_altitude,
          "climb": climb,
          "climb_rate": climb_rate,
          "heading_change": heading_change,
          "bank_angle": bank_angle
          }
        maneuver = xpr.define_flight_maneuver(start_altitude, climb, climb_rate, heading_change, bank_angle)
        self.assertEquals(maneuver, expected_maneuver)

    def test_permutations(self):
        start_altitudes = [1000, 1001]
        climbs = [200,201]
        climb_rates = [300, 301] 
        heading_changes = [1,2] 
        bank_angles = [10,11]
        maneuvers = xpr.define_flight_maneuvers(start_altitudes, climbs, climb_rates,
            heading_changes, bank_angles, sort=True)
        expected_permutation_nr = 2 * 2 * 2 * 2 * 2
        self.assertEqual(len(maneuvers), expected_permutation_nr)

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