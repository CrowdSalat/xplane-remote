import control_xplane as xp
import logging
import os, sys

logger = logging.getLogger(__name__)


def config_logger():
     logger.setLevel(logging.DEBUG)
     
     formatter = logging.Formatter('%(asctime)s - %(name)s-%(funcName)s - %(levelname)s - %(message)s')
     
     ch = logging.StreamHandler()
     ch.setFormatter(formatter)

     script_path = os.path.dirname(sys.argv[0])
     fh = logging.FileHandler(os.path.join(script_path, __name__ + '.log'), encoding='utf-8')
     fh.setFormatter(formatter)

     logger.addHandler(ch)
     logger.addHandler(fh)



def trainings_set00():
    logger.info('run:' + trainings_set00)
    # fixture
    start_alt = 1000
    xp.climb_to(start_alt, 200)
    xp.wait_until_altitude_reached(start_alt,reset_time=True)     

    #parable
    fpms = [200.0, 300.0, 400.0, 500.0]
    climbs = (-100, 150)


    for fpm in fpms:
        for climb in climbs:
            logger.info('Climb to {} ft with {} fpm.'.format(climb,fpm))
            xp.climb_wait_until_reached_and_reset_time(climb, fpm)

    # banks
    bank_modes = {1,2,3,4,5,6}
    for bank in bank_modes:
        logger.info('Turn in Mode {}.'.format(bank))
        xp.fly_banks(bank_mode=bank)


def main():
    config_logger()
    xp.init_xp_remote()

    xp.rst_msn_time()

    #trainings_set00()

    xp.close_xp_remote()
    pass

if __name__ == "__main__":
    main()