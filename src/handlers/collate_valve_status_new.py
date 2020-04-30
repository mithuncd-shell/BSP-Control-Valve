print("started")
from handlers.libraries_new import *

from handlers.valve import VALVE
print("lib import copleted")

# path="E:/New folder/Control Valves/valvesPAM/data/live/models"
def collate_status(path):
    print("collate status started")
    status = []
    columns = ["valve_id", "description", "PI.Tag", "alarm", "Email_trigger", "last_predicted_time_stamp", "mode",
               "icon", "color"]

    for filename in glob.glob(os.path.join(path, '*_status.pkl')):
        # print("filename: "+filename)

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

def get_pickle(path):
    print("collate status started")
    status = []
    columns = ["valve_id"]

    for filename in glob.glob(os.path.join(path, '*_status.pkl')):
        f = open(filename, mode="rb")
        valve_status = pickle.load(f)
        status.append([valve_status["valve_id"]])
    valve_status = pd.DataFrame(np.array(status), columns=columns)
    return valve_status

def load_valve_data(path, valve_id):
    f_name = path + "\\" + valve_id + ".pkl"
    valve, success, error = VALVE.from_pickle(f_name)
    if success:
        valve = valve.output
        # valve.to_csv('Valve_output.csv')
        # print(valve.shape)
        valve["datetime"] = valve.index.strftime("%Y-%m-%d %H:%M:%S")
        valve = valve.reset_index(drop=True)
        # print(valve.dtypes)
        return valve
    else:
        raise ValueError(error)

def load_valve_data180(path, valve_id):
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

def training_data_kpi(path, valve_id, start_date, end_date):
    f_name = path + "\\" + valve_id + ".pkl"
    valve, success, error = VALVE.from_pickle(f_name)
    if success:
        valve = valve.output
        valve["datetime"] = valve.index.strftime("%Y-%m-%d %H:%M:%S")
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.min.time())
        valve = valve[(valve.index > start_date) & (valve.index < end_date)]
        valve = valve.reset_index(drop=True)
        valve = valve[['target', 'prediction', 'deviation']]

        mae = mean_absolute_error(valve.target, valve.prediction)
        rmse = mean_squared_error(valve.target, valve.prediction)
        r2 = r2_score(valve.target, valve.prediction)

        return [rmse, mae, r2]
    else:
        raise ValueError(error)


def testing_data_kpi(path, valve_id, start_date, end_date):
    f_name = path + "\\" + valve_id + ".pkl"
    valve, success, error = VALVE.from_pickle(f_name)
    if success:
        valve = valve.output
        valve["datetime"] = valve.index.strftime("%Y-%m-%d %H:%M:%S")
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.min.time())
        valve = valve[(valve.index > start_date) & (valve.index < end_date)]
        valve = valve.reset_index(drop=True)
        valve = valve[['target', 'prediction', 'deviation']]

        mae = mean_absolute_error(valve.target, valve.prediction)
        rmse = mean_squared_error(valve.target, valve.prediction)
        r2 = r2_score(valve.target, valve.prediction)

        return [rmse, mae, r2]
    else:
        raise ValueError(error)


def get_coeff1(path, valve_id):
    f_name = path + "\\" + valve_id + ".pkl"
    valve, success, error = VALVE.from_pickle(f_name)
    if success:
        print("Claclauting coeff")
        df_coeff = valve.model.get_coeff(valve.feature_pi_tags)[0]
        df_stats = valve.stats
        df_coeff['Coefficient'] = round(df_coeff['Coefficient'], 2)
        df_coeff['abs_coeff'] = round(df_coeff['abs_coeff'], 2)
        # df_coeff.rename(columns={'Input_column': 'Tag'}, inplace=True)
        df_stats['Tag'] = df_stats.index
        df_coefff = pd.merge(df_coeff, df_stats, how='left', left_on=df_coeff.columns[0], right_on='Tag')
        df_coefff['mean'] = round(df_coefff['mean'], 2)
        df_coefff['range'] = round(df_coefff['range'], 2)
        df_coefff = df_coefff.drop(['Tag'], axis=1)
    else:
        print("Claclauting coeff err")
        raise ValueError(error)
    return df_coefff


def read_master_file():
    df = pd.read_pickle(master_file)
    return df


def master_column():
    df = pd.read_pickle(master_file)
    return [df.columns.astype(str).values]


def config_names():
    p = config_path
    names = [f for f in os.listdir(p) if 'json' in f]
    return names


def read_json(val):
    p = config_path + '/' + val + '.json'
    with open(p) as json_file:
        data = json.load(json_file)

    return data

# p = r'C:\Users\Ankur.Parmar\OneDrive - Shell\Projects\2019\Brunei\cv\valves_all\data\live\models'
# load_valve_data(p, 'CPRP07-DCS-40LICA104A_OUT')


