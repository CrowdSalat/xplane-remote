import unittest
import writeDataToXPlane as xpr


class Test_Xplane_Remote(unittest.TestCase):
    
    def test_init(self):
        val = xpr.get_dreaf(xpr.DREF_AP_SET_ALTI_IN_FTMSL2)
        val2 = xpr.get_dreaf(xpr.DREF_AP_SET_ALTI_IN_FTMSL)

        
        xpr.read_rref()

        print(xpr.dref_dict)
        xpr.send_rref(xpr.DREF_AP_SET_ALTI_IN_FTMSL2, 0)
        xpr.send_rref(xpr.DREF_AP_SET_ALTI_IN_FTMSL, 0)

        self.assertTrue(val != 0.0)
        self.assertTrue(val2 != 0.0)
    
    

    def test_set_coordinates(self):
        xpr.set_position_x()
        self.assertTrue(True)

    def test_set_msntime(self):
        xpr.rst_msn_time()
        self.assertTrue(True)

    def test_read_drefs(self):
        xpr.request_refs()
        self.assertTrue(True)

    def test_climb_to(self):
        start_alt = 1500.0
        altitude = 200.0
        fpm = 200.0

        val = xpr.get_dreaf(xpr.DREF_INDICATOR_ALTI)
        xpr.climb_to(start_alt, fpm)
        self.assertTrue(True)


    
 
if "__main__" == __name__:
    unittest.main()