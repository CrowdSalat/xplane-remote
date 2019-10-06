import control_xplane as xp
import logging
import os, sys

logger_name = 'create_trainingsdata'
logger = logging.getLogger(logger_name)


def config_logger():
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s-%(funcName)s - %(levelname)s - %(message)s')
    
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    script_path = os.path.dirname(sys.argv[0])
    fh = logging.FileHandler(os.path.join(script_path, logger_name + '.log'), encoding='utf-8')
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

def trainings_set00():
    logger.info('run trainings_set00')
    xp.rst_msn_time()
    # fixture
    
    #parable
    start_alt = [1000]
    climbs = [-100, 100]
    fpms = [200.0, 300.0, 400.0, 500.0]
    parable = xp.define_flight_maneuvers(start_alt, climbs, fpms, [0],[0])
    #logger.info(parable)
    xp.fly(parable)

    # banks
    bank_modes = [1,2,3,4,5,6]
    banks = xp.define_flight_maneuvers([-1], [0], [0], [90], bank_modes)
    #logger.info(parable)

    xp.fly(banks)


def trainings_set01():
    # parable 
    altitudes = [1000, 2000, 3000, 4000, 5000, 6000]
    climb = [100, -100]
    climb_rates = [300, 400, 500]

    maneuvers = xp.define_flight_maneuvers(altitudes, climb, climb_rates, [0], [0])
    xp.fly(maneuvers)

def main():
    config_logger()
    xp.init_xp_remote()
    trainings_set00()

    xp.close_xp_remote()
     

if __name__ == "__main__":
    main()