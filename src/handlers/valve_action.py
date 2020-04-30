from handlers.libraries import *
from handlers.valve import VALVE


def predict_valve(valve_id: str):
    """
    this function update the valve with latest data
    :param valve_id: name of the valve
    :return: None
    """
    #print("time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        logging.info("PKL file unpickle started")
        valve, success, error = VALVE.from_pickle(deployment_path + "/" + valve_id + ".pkl")
    except:
        logging.error("PKL file unpickle failed")
    if not success:
        logging.error(error)
        raise ValueError(error)
    else:
        logging.info("PKL file unpickle complete")
        logging.info("Update valve object started")
        success, error = valve.update_valve()
    if not success:
        logging.error(error)
        raise ValueError(error)
    else:
        logging.info("Update valve object completed")
        logging.info("Update pkl file started")
        success, error = valve.to_pickle(deployment_path)
    if success:
        logging.info("Update pkl file completed")
        logging.info("Writeback to PI started")
        success, error = valve.write_data_to_pi()
    if not success:
        logging.error(error)
        raise ValueError(error)
    else:
        logging.info("Writeback to PI complete")


import os
def train_valve(valve_id: str):
    """
    this function train the valve and prepare for deployment
    :param valve_id: name of the valve
    :return: None
    """
    cwd_ =os.getcwd()
    #print(cwd_)
    config_file = config_path + "\\" + valve_id + ".json"
    fp = open(config_file)
    config = json.load(fp)
    valve, success, error = VALVE.create_valve(config=config, master_data_file=master_file)
    if not success:
        raise ValueError(error)
    else:
        #print(valve.output.shape)
        success, error = valve.to_pickle(model_path)
    if not success:
        raise ValueError(error)


def deploy_valve(valve_id: str):
    """
    this function deploy the latest model
    :param valve_id: name of the valve
    :return: None
    """
    try:
        source = model_path + "/" + valve_id + ".pkl"
        target = deployment_path + "/" + valve_id + ".pkl"
        shutil.copy(source, target)
        source = model_path + "/" + valve_id + "_status.pkl"
        target = deployment_path + "/" + valve_id + "_status.pkl"
        shutil.copy(source, target)

    except Exception as e:
        raise ValueError("unable to deploy the valve", valve_id, str(e))


def re_train_valve(valve_id: str, start: str, end: str):
    """
    this function retrain the valve with latest data
    :param valve_id: name of the valve
    :param start: training starting time stamp
    :param end: training end time stamp
    :return: None
    """
    valve, success, error = VALVE.from_pickle(model_path + "/" + valve_id + ".pkl")
    if not success:
        raise ValueError(error)
    else:
        period = {"start": start, "end": end}
        success, error = valve.re_train(period=period, master_data_file=master_file)
    if not success:
        raise ValueError(error)
    else:
        success, error = valve.to_pickle(model_path)
    if not success:
        raise ValueError(error)


def tune_alarm(valve_id: str, deviation_threshold: float, alarm_trigger: int, alarm_stop: int):
    """
    this function tune the alarm
    :param valve_id: (str) name of the valve
    :param deviation_threshold: (float) threshold value of deviation
    :param alarm_trigger: (int) trigger value
    :param alarm_stop: (int) alarm stop value
    :return:
    """
    valve, success, error = VALVE.from_pickle(model_path + "/" + valve_id + ".pkl")
    if not success:
        raise ValueError(error)
    else:
        success, error = valve.update_alarm(deviation_threshold, alarm_trigger, alarm_stop)
    if not success:
        raise ValueError(error)
    else:
        success, error = valve.to_pickle(model_path)
    if not success:
        raise ValueError(error)
