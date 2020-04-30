from handlers.valve_action import *

if len(sys.argv) < 3:
    raise ValueError("Please provide two inputs such as, update valve_name: "
                     "example to run the code is python this.py update 26FCV5002"
                     "update : update the valve model with latest data"
                     "deploy: move trained valve to live folder"
                     "train : to on board new valve"
                     "retrain: to retrain the valve with new period"
                     "tune_alarm: to tune alarm technique with different parameters")

input_action = str.lower(sys.argv[1])
valve_id = sys.argv[2]
if input_action == "update":
    logging.info("Prediction workflow Started")
    predict_valve(valve_id)
    logging.info("Prediction workflow Ended")
elif input_action == "deploy":
    print(valve_id, input_action, "has started at ", str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    deploy_valve(valve_id)
    print(valve_id, input_action, "is completed successfully")
elif input_action == "train":
    print(valve_id, input_action, "has started at ", str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    train_valve(valve_id)
    print(valve_id, input_action, "is completed successfully")
elif input_action == "retrain":
    re_train_valve(valve_id, sys.argv[3], sys.argv[4])
    print(valve_id, input_action, "is completed successfully")
elif input_action == "tune_alarm":
    tune_alarm(valve_id, float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    print(valve_id, input_action, "is completed successfully")
else:
    raise ValueError("provide any one of the 4 action items on the valve, update, train, retrain, tune_alarm")

