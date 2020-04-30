from handlers.libraries import *
from handlers.valve import VALVE

# path="E:/New folder/Control Valves/valvesPAM/data/live/models"


def collate_status(path):
    status = []
    columns = ["valve_id", "description", "PI.Tag", "alarm", "Email_trigger", "last_predicted_time_stamp", "mode",
               "icon", "color"]
    print(path)
    for filename in glob.glob(os.path.join(path, '*_status.pkl')):
        #print("filename: "+filename)

        f = open(filename, mode="rb")
        valve_status = pickle.load(f)
        if valve_status["mode"] == 1:
            icon = "hand-paper"
            color = "yellow"
        elif valve_status["alarm"] == 1:
            icon = "thumbs-down"
            color = "red"
        else:
            icon = "thumbs-up"
            color = "green"
        status.append([valve_status["valve_id"],
                       valve_status["description"],
                       valve_status["output_pi_tag"],
                       valve_status["alarm"],
                       valve_status["alarm_trigger"],
                       valve_status["last_predicted_time_stamp"],
                       valve_status["mode"],
                       icon,
                       color]
                      )
    valve_status = pd.DataFrame(np.array(status), columns=columns)
    valve_status["alarm"] = valve_status["alarm"].apply(pd.to_numeric, errors='coerce')
    valve_status["Email_trigger"] = valve_status["Email_trigger"].apply(pd.to_numeric, errors='coerce')
    valve_status["mode"] = valve_status["mode"].apply(pd.to_numeric, errors='coerce')
    return valve_status


def load_valve_data(path, valve_id):
    f_name = path + "\\" + valve_id + ".pkl"
    valve, success, error = VALVE.from_pickle(f_name)
    if success:
        start_time = datetime.strptime(valve.status["last_predicted_time_stamp"], "%Y-%m-%d %H:%M:%S")
        print(start_time)
        valve = valve.output
        # print(valve.shape)
        start_time = start_time - timedelta(days=180)
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        new_data = valve.loc[start_time:, ].copy()
        new_data["datetime"] = new_data.index.strftime("%Y-%m-%d %H:%M:%S")
        new_data = new_data.reset_index(drop=True)

        # print(valve.dtypes)
        # (new_data.shape)
        return new_data
    else:
        raise ValueError(error)


# load_valve_data(r"C:\Users\S-R.Subramanian\OneDrive - Shell\Oman-PDO\Control Valve\Sprint11\code\valvesPAM\data\live\models","26FCV1161")
