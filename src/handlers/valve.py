from handlers.libraries import *
from handlers.pi import PI
from handlers.valve_model import MODEL


class VALVE:
    def __init__(self):
        """
        Initialize the valve object
        """
        self.id = None
        self.location = None
        self.type = None
        self.description = None
        self.output_pi_tag = None
        self.mode_pi_tag = None
        self.filter_pi_tags = list()
        self.filter_condition = list()
        self.exclusion_pi_tags = list()
        self.feature_pi_tags = list()
        self.max_features = 50
        self.pi_raw_data = pd.DataFrame()
        self.training_data = pd.DataFrame()
        self.output = pd.DataFrame()
        self.stats = pd.DataFrame()
        self.model_training_period = {"start": "", "end": ""}
        self.model_testing_period = {"start": "", "end": ""}
        self.band_pass_filter = {"lower_limit": 0.05, "upper_limit": 99.95}
        self.alert_parameters = {"deviation_threshold": 5.0, "alarm_trigger": 30, "alarm_stop": 48}
        self.model = MODEL()
        self.status = {"valve_id": None, "description": None, "output_pi_tag": None, "alarm": 0, "alarm_trigger": 0,
                       "last_predicted_time_stamp": "2017-01-01 00:00:00", "mode": 0,
                       "alarm_KPI1": 0, "alarm_KPI2": 0}
        self.pi = PI
        self.pi_server_name = ""
        self.data_interval = '10min'
        self.pi_write_back_tag1 = ""
        self.pi_write_back_tag2 = ""
        self.inclusion_list = list()
        # print(self)

    def assign_properties(self, config: dict):
        """
        adds the valve configuration info to the valve object
        :param config:  a dictionary with basic info related to the valve
        :return: success status and error log
        """
        try:
            self.id = config["valve_id"]
            self.location = config["location"]
            self.type = config["type"]
            self.description = config["description"]
            self.output_pi_tag = config["op_pi_tag"]
            if config["mode_pi_tag"] != "":
                self.mode_pi_tag = config["mode_pi_tag"]
            else:
                self.mode_pi_tag = None
            self.filter_pi_tags = config["filter_pi_tags"]
            self.filter_condition = config["filter_conditions"]
            self.exclusion_pi_tags = config["exclusion_pi_tags"]
            self.max_features = int(config["maximum_features"])
            self.band_pass_filter["lower_limit"] = config["band_pass_lower_limit"]
            self.band_pass_filter["upper_limit"] = config["band_pass_upper_limit"]
            self.model_training_period["start"] = config["training_period"][0]
            self.model_training_period["end"] = config["training_period"][1]
            self.model_testing_period["start"] = config["testing_period"][0]
            self.model_testing_period["end"] = config["testing_period"][1]
            self.alert_parameters["deviation_threshold"] = float(config["deviation_threshold"])
            self.alert_parameters["alarm_trigger"] = int(config["alarm_trigger"])
            self.alert_parameters["alarm_stop"] = int(config["alarm_stop"])
            self.data_interval = config["interval"]
            self.pi_server_name = config["PIServerName"]
            # self.pi = PI(config["PIServerName"])
            self.pi_write_back_tag1 = config["pi_write_back_tag"][0]
            self.pi_write_back_tag2 = config["pi_write_back_tag"][1]
            self.inclusion_list = config["inclusion_pi_tags"]
            success, error = self.model.select_algorithm(config["model"])
        except Exception as e:
            success = False
            error = " unable to assign the config to valve" + str(e)
        return success, error

    def add_data_from_master(self, data_master: pd.DataFrame):
        """
        select the data from master data using correlation matrix
        :param data_master:  pandas data frame of master pi data with all pi tags of an asset
        :return: success status and error logs
        """

        # this section find the size and shape of master data
        data_master_columns = list(data_master)
        subset_columns = self.feature_pi_tags.copy()
        subset_columns.append(self.output_pi_tag)
        if self.mode_pi_tag is not None:
            subset_columns.append(self.mode_pi_tag)
        missing_columns = [col for col in subset_columns if col not in data_master_columns]
        if len(missing_columns) == 0:
            self.pi_raw_data = data_master[subset_columns].copy()
            success = True
            error = ""
        else:
            success = False
            error = "following columns are missing in the master file " + str(missing_columns)
        return success, error

    def add_training_data(self, data_x: pd.DataFrame, data_y: pd.DataFrame):
        """
        This function create the training data based on two input data frames
        :param data_x: normalized data in pandas data frame format
        :param data_y: raw data in pandas data frame format
        :return: success status and error logs
        """
        if len([i for i in self.inclusion_list if i in data_x.columns]) != len(self.inclusion_list):
            print("Not the right Inclusion List")
        try:
            self.training_data = pd.merge(left=data_x[self.feature_pi_tags],
                                          right=data_y[self.output_pi_tag],
                                          left_index=True,
                                          right_index=True,
                                          how="inner")
            self.training_data = self.training_data.rename(columns={self.output_pi_tag: "target"})
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " Assigning training data  and valve data is failed" + str(e)
        return success, error

    def find_feature_pi_tags(self, data_master: pd.DataFrame):
        """
        select the data from master data using correlation  and create the training data
        :param data_master:  pandas data frame of master pi data with all pi tags of an asset
        :return: success status and error logs
        """
        # this section remove exclusion tags from master data
        subset_data_norm = pd.DataFrame()
        subset_data, success, error = self.remove_columns(data_master, self.exclusion_pi_tags)
        if success:
            # this section filter rows of the master data based on mode tags
            subset_data, success, error = self.mode_filter(subset_data, self.mode_pi_tag, self.filter_condition)
        if success:
            # This section coerce the data to numeric
            subset_data = subset_data.loc[subset_data['filter'] == 0]
            #print("after mode filter applied: data shape: ", subset_data.shape)
            subset_columns = list(subset_data)
            if self.mode_pi_tag != "" and self.mode_pi_tag is not None:
                subset_columns.remove(self.mode_pi_tag)
            subset_data = subset_data[subset_columns]
            subset_data, success, error = self.coerce_data(subset_data)
        if success:
            # this section filter rows of the master data based on training period
            subset_data, success, error = self.filter_rows_by_period(subset_data, self.model_training_period)
        if success:
            # this section filter rows of the master data based on band pass filter and null values
            subset_data, success, error = self.filter_rows_by_column_values(subset_data,
                                                                            self.output_pi_tag,
                                                                            self.band_pass_filter)
        if success:
            # removing rows where output variable value is null
            subset_data, success, error = self.filter_rows_by_column_null(subset_data, self.output_pi_tag)
        if success:
            # normalize data
            subset_data_norm, success, error = self.transform_data(subset_data)
        if success:
            # this section compute the correlation matrix with respect to valve output Pi tag
            success, error = self.calculate_correlation(subset_data_norm)
        if success:
            # this section add valve raw pi data
            success, error = self.add_data_from_master(data_master)
        if success:
            # adding the training data to the valve object
            success, error = self.add_training_data(subset_data_norm, subset_data)
        return success, error

    def pull_data_from_pi(self):
        """
        update the valve data from pi to latest time stamp
        :return: live data, success status, error logs
         """

        pi = PI(self.pi_server_name)
        tag_list = self.feature_pi_tags.copy()
        tag_list.append(self.output_pi_tag)
        if self.mode_pi_tag is not None:
             tag_list.append(self.mode_pi_tag)
        start_time = datetime.strptime(self.status["last_predicted_time_stamp"], "%Y-%m-%d %H:%M:%S")
        start_time = start_time - timedelta(days=1)
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        # start_time = self.status["last_predicted_time_stamp"]
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        live_data, success, error = pi.get_data_multiple(tag_list, start_time, end_time, self.data_interval)
        #live_data.to_csv("live_data.csv")
        return live_data, success, error

    def write_data_to_pi(self):
        """
        This function write the latest prediction and alarm value to PI
        :return: success status and error logs
        """
        pi = PI(self.pi_server_name)
        success, error = pi.write_back_to_pi(self.pi_write_back_tag1, self.output["prediction"].values[-1],
                                             self.status["last_predicted_time_stamp"])
        if success:
            success, error = pi.write_back_to_pi(self.pi_write_back_tag2, str(self.status["alarm"]),
                                                 self.status["last_predicted_time_stamp"])
        return success, error

    def transform_data(self, data: pd.DataFrame):
        """
        transform the valve data for model training
        :param data :pandas data frame
        :return: normalized data as pandas data frame, success status and error logs
        """
        data_norm = pd.DataFrame
        try:
            data = data.apply(pd.to_numeric, errors='coerce')
            data = data.fillna(method='ffill').fillna(method='bfill')
            columns = list(data)
            # columns.remove(self.output_pi_tag)
            range1 = data[columns].max() - data[columns].min()
            # print(range1[range1 > 0].index.values)
            columns = range1[range1 > 0].index.values
            mean = data[columns].mean()
            range1 = data[columns].max() - data[columns].min()
            data_norm = (data[columns] - mean) / range1
            # data_norm = pd.merge(left=data_norm, right=data[self.output_pi_tag],
            #                      left_index=True, right_index=True, how="inner")
            self.stats = pd.merge(left=pd.DataFrame(mean), right=pd.DataFrame(range1),
                                  left_index=True, right_index=True, how="inner")
            self.stats.columns = ["mean", "range"]
            # print(self.stats)
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " normalizing the training data is failed" + str(e)
        return data_norm, success, error

    def prepare_data_for_prediction(self, data: pd.DataFrame):
        """
        transform the valve data for model prediction
        :param data :pandas data frame
        :return:  prepared data as pandas data frame, success status and error logs
        """
        try:
            data = data.fillna(method='ffill').fillna(method='bfill')
            data, success, error = self.mode_filter(data, self.mode_pi_tag, self.filter_condition)

            if success:
                filter_data = data["filter"]
                if self.mode_pi_tag is not None:
                    mode_data = data[self.mode_pi_tag].copy()
                data, success, error = self.coerce_data(data)
                data = data.fillna(method='ffill').fillna(method='bfill')
                if success:
                    valve_output = data[self.output_pi_tag].copy()
                    columns = self.feature_pi_tags.copy()
                    data = data[columns]
                    for col in columns:
                        stats = self.stats.loc[col]
                        if data[col].isnull().all():
                            data[col] = stats['mean']
                            print("WARNING(prediction may be wrong): values is missing "
                                  "for more than 1 day for the pi tag", col,
                                  " will be replaced by mean value")
                        data[col] = (data[col] - stats['mean'])/stats["range"]
                    data = pd.merge(left=data, right=valve_output, left_index=True, right_index=True, how="inner")
                    data = pd.merge(left=data, right=filter_data, left_index=True, right_index=True, how="inner")
                    data = data.rename(columns={self.output_pi_tag: "target"})
                    if self.mode_pi_tag is not None:
                        data = pd.merge(left=data, right=mode_data, left_index=True, right_index=True, how="inner")
                        data = data.rename(columns={self.mode_pi_tag: "mode"})
                    else:
                        data["mode"] = ""
                    success = True
                    error = ""
        except Exception as e:
            success = False
            error = "Unable to normalize the data using stats info" + str(e)
        return data, success, error

    def train_model(self):
        """
        train the valve model using training period
        :return: success status and error logs
        """
        try:
            columns = list(self.training_data)
            columns.remove("target")
            x = self.training_data[columns].values
            y = self.training_data["target"].values
            self.model.train_model(x, y)
            coeff, success, error = self.model.get_coeff(columns)
            if success:
                columns1 = coeff["Input_column"].values.tolist()
                self.feature_pi_tags = columns1.copy()
                columns1.append("target")
                self.training_data = self.training_data[columns1]
                columns = list(self.training_data).copy()
                columns.remove("target")
                x = self.training_data[columns].values
                y = self.training_data["target"].values
                self.model.train_model(x, y)
                success = True
                error = ""
        except Exception as e:
            success = False
            error = " Model training is failed" + str(e)
        return success, error

    def predict_valve_opening(self, data: pd.DataFrame):
        """
        predict the valve opening for the given transformed data
        :param data (pandas data frame) input data for model prediction
        :return: data as pandas data frame, success status and error logs
        """
        try:
            data1 = data[self.feature_pi_tags]
            x = data1.values
            prediction = self.model.predict(x)
            success = True
            error = ""
            data["prediction"] = prediction
        except Exception as e:
            success = False
            error = "unable to predict output values for the given input data " + str(e)
        return data, success, error

    def update_alarm(self, deviation_threshold: float, alarm_trigger: int, alarm_stop: int):
        """
        recompute the alarm for the whole valve data
        :param deviation_threshold: (float) to create alarm if the deviation above this value
        :param alarm_trigger: (int) number of consecutive points to observe the deviation above
        the threshold value to trigger an alarm
        :param alarm_stop: (int) number of consecutive points to observe the deviation below the threshold
        value to stop the alarm
        :return: success status and error logs
        """
        self.alert_parameters = {"deviation_threshold": deviation_threshold,
                                 "alarm_trigger": alarm_trigger,
                                 "alarm_stop": alarm_stop}
        deviation = self.output["deviation"]
        alarm, counter1, counter2, success, error = self.qsum(deviation, deviation_threshold,
                                                              alarm_trigger,
                                                              alarm_stop,
                                                              0, 0)
        if success:
            self.output["alarm"] = alarm["alarm"]
            self.output["alarm_trigger"] = alarm["alarm_trigger"]
            success, error = self.update_status(counter1, counter2)
        return success, error

    def compute_alarm(self, data: pd.DataFrame):
        """
        this function compute the alarm for the given data
        :param data: pandas data frame should have a deviation column
        :return: qsum alarm, alarm status, success status, error logs
        """
        deviation = data["deviation"]
        alarm, counter1, counter2, success, error = self.qsum(deviation,
                                                              self.alert_parameters["deviation_threshold"],
                                                              self.alert_parameters["alarm_trigger"],
                                                              self.alert_parameters["alarm_stop"],
                                                              self.status["alarm_KPI1"], self.status["alarm_KPI2"])
        return alarm, counter1, counter2, success, error

    def update_valve(self):
        """
        update the valve with latest data, predict the valve opening, and update alarms
        :return: success status and error logs
        """
        alarm = pd.DataFrame()
        counter1 = 0
        counter2 = 0
        new_data = self.pi_raw_data.copy()
        #print(new_data.shape)
        try:
            logging.info("Data pull from PI started")
            new_data, success, error = self.pull_data_from_pi()
        except Exception as e:
            success = False
            error = "Data pull from PI failed : " + str(e)
        if success:
            logging.info("Data pull from PI complete")
            try:
                logging.info("Data prep started")
                new_data, success, error = self.prepare_data_for_prediction(new_data)
            except Exception as e:
                success = False
                error = "Data prep failed : " + str(e)
        if success:
            logging.info("Data prep complete")
            try:
                logging.info("Prediction of valve opening started")
                new_data, success, error = self.predict_valve_opening(new_data)
            except Exception as e:
                success = False
                error = "Prediction of valve opening failed : " + str(e)
        if success:
            logging.info("Prediction of valve opening complete")
            try:
                logging.info("Compute deviation started")
                new_data, success, error = self.compute_prediction_deviation(new_data)
            except Exception as e:
                success = False
                error = "Compute deviation failed : " + str(e)
        if success:
            logging.info("Compute deviation complete")
            start_time = datetime.strptime(self.status["last_predicted_time_stamp"], "%Y-%m-%d %H:%M:%S")
            start_time = start_time + timedelta(seconds=10*60)
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                logging.info("Compute alarm started")
                new_data = new_data.loc[start_time:, ]
                alarm, counter1, counter2, success, error = self.compute_alarm(new_data)
            except Exception as e:
                success = False
                error = "Compute alarm failed .Missing last time stamp data " + str(e)
        if success:
            try:
                new_data = pd.merge(left=new_data, right=alarm, left_index=True, right_index=True, how="inner")
                self.output = self.output.append(new_data)
                self.output = self.output.loc[~self.output.index.duplicated(keep='last')]
                success, error = self.update_status(counter1, counter2)
            except Exception as e:
                success=False
                error = "Update valve object failed : " + str(e)
        if success:
            if self.status["alarm_trigger"] == 1:
                try:
                    logging.info("Send email : ")
                    self.send_email()
                except Exception as e:
                    logging.error("Eoor in sending email")
            else:
                logging.info("No email alert ")
        return success, error

    def to_pickle(self, path: str):
        """
        save the valve object to pickle file
        :param path (str) location of the folder where you want to save the model object
        :return: success status and error logs
        """
        try:
            file = open(path + "/" + self.id + ".pkl", mode="wb")
            pickle.dump(self, file)
            file.close()
            file1 = open(path + "/" + self.id + "_status.pkl", mode="wb")
            pickle.dump(self.status, file1)
            file1.close()
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "unable to update the pkl file " + str(e)
            logging.error(error)
        return success, error

    def calculate_correlation(self, data: pd.DataFrame, lasso_filter: bool = False):
        """
        This function compute the correlation matrix for the given target variables against the reference variable
        :param data: pandas data frame
        :param lasso_filter (boolean) to decide whether filter the correlated variable further down by lasso method
        :return: success status and error logs
        """
        try:
            # lasso_filter = False
            columns = list(data)
            columns.remove(self.output_pi_tag)
            # y = data[self.output_pi_tag].values
            # y = data[self.output_pi_tag].apply(pd.to_numeric, errors='coerce')
            # x = data[columns].apply(pd.to_numeric, errors='coerce')
            corr_df = data[columns].corrwith(data[self.output_pi_tag]).abs().sort_values(ascending=False)
            self.feature_pi_tags = corr_df[:self.max_features].index.values.tolist() + self.inclusion_list
            if lasso_filter:
                md = MODEL()
                success, error = md.select_algorithm("lasso")
                if success:
                    success, error = md.train_model(data[self.feature_pi_tags].values, data[self.output_pi_tag].values)
                    if success:
                        coeff, success, error = md.get_coeff(self.feature_pi_tags)
                        if success:
                            try:
                                self.feature_pi_tags = coeff.loc[(coeff["abs_coeff"] > 0.00),
                                                                 "Input_column"].values.tolist()
                            except Exception as e:
                                success = False
                                error = "Unable to get coeff from lasso method" + str(e)
            else:
                success = True
                error = ""
        except Exception as e:
            success = False
            error = " Calculation of correlation matrix is failed" + str(e)
        return success, error

    def re_train(self, period: dict, master_data_file: str):
        """
        retrain the valve using the given period
        :param period: (dictionary) start and end  time stamp
        :param master_data_file: name and file path of master data file
        :return: success status and error logs
        """
        file = open(master_data_file, mode="rb")
        master_data = pickle.load(file)
        self.model_training_period = period
        success, error = self.find_feature_pi_tags(master_data)
        if success:
            success, error = self.train_and_predict()
        return success, error

    def train_and_predict(self):
        """
        this function train and predict for valve
        :return: success status and error logs
        """
        success, error = self.train_model()
        if success:
            # print(self.feature_pi_tags)
            columns = self.feature_pi_tags.copy()
            columns.append(self.output_pi_tag)
            if self.mode_pi_tag != "" and self.mode_pi_tag is not None:
                columns.append(self.mode_pi_tag)

            self.pi_raw_data = self.pi_raw_data[columns]
            success = True
            error = ""
        else:
            success = False
            error = "unable to rearrange raw pi data"
        if success:
            data, success, error = self.prepare_data_for_prediction(self.pi_raw_data)
            if success:
                data, success, error = self.predict_valve_opening(data)
                if success:
                    success, error = self.model.get_kpi(data["target"], data["prediction"])
                    if success:
                        data, success, error = self.compute_prediction_deviation(data)
                        if success:
                            alarm, counter1, counter2, success, error = self.compute_alarm(data)
                            if success:
                                data = pd.merge(left=data, right=alarm, left_index=True, right_index=True, how="inner")
                                self.output = data.copy()
                                success, error = self.update_status(counter1, counter2)
        return success, error

    @staticmethod
    def from_pickle(file_name: str):
        """
        load valve object from pickle file
        :param file_name (str) file name with appropriate folder location
        :return: Valve object, success status and error logs
        """
        valve = VALVE()
        try:
            file = open(file_name, mode="rb")
            valve = pickle.load(file)
            file.close()
            # valve = pickle.load(file)
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "unable to load the model pkl file " + str(e)
        return valve, success, error

    @staticmethod
    def qsum(deviation: pd.Series, deviation_threshold: float, alarm_trigger: int,
             alarm_stop: int, counter1: int = 0, counter2: int = 0):
        """
        this function calculate qsum alarm for the given time series of deviation
        :param deviation: difference between actual and predicted valve opening as pandas time series
        :param deviation_threshold: (float) to create alarm if the deviation above this value
        :param alarm_trigger: (int) number of consecutive points to observe the deviation above
        the threshold value to trigger an alarm
        :param alarm_stop: (int) number of consecutive points to observe the deviation below the threshold
        value to stop the alarm
        :param counter1: (int) iteration counter initial value. if qsum updated for new data
        point, then last counter1 value should be given
        :param counter2: (int) iteration counter initial value. if qsum updated for new data
        point, then last counter1 value should be given
        :return: alarm as pandas data frame,   counter1 as int, counter2 as int, success status, error and error logs
        """
        alarm = pd.DataFrame()
        try:
            alerts = 0
            qsum = []
            alert_start = []
            time_index = deviation.index.values
            deviation = np.array(deviation)
            increment = ((deviation > deviation_threshold) | (deviation < -deviation_threshold)).astype(int)
            for i in range(increment.shape[0]):
                if increment[i] == 1:
                    counter1 += 1
                    counter2 = 0
                elif counter1 > alarm_trigger and increment[i] != 1:
                    counter2 += 1
                    counter1 += 1
                    if counter2 > alarm_stop:
                        counter1 = 0
                        counter2 = 0
                else:
                    counter1 = 0
                    counter2 = 0
                if counter1 > alarm_trigger:
                    if counter1 == alarm_trigger+1:
                        alerts += 1
                        alert_start.append(1)
                    else:
                        alert_start.append(0)
                    qsum.append(1)
                else:
                    qsum.append(0)
                    alert_start.append(0)
                    counter2 = 0
            qsum = pd.DataFrame(np.array(qsum), index=time_index, columns=["alarm"])
            alert_start = pd.DataFrame(np.array(alert_start), index=time_index, columns=["alarm_trigger"])
            alarm = pd.merge(left=qsum, right=alert_start, left_index=True, right_index=True, how="inner")
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "unable to compute alarm " + str(e)
        return alarm, counter1, counter2, success, error

    @staticmethod
    def mode_filter(data: pd.DataFrame, variable: str, conditions: list):
        """
        This function filter the given data by filter conditions
        :param data: pandas data frame, on which you want to apply filter
        :param variable: (str) name of the pi tag where you want to apply mode
        :param conditions: (list) contains the condition and value
        :return: filtered data as pandas data frame, success status and error logs
        """
        success = True
        error = None
        data['filter'] = 0
        if not isinstance(variable, str):
            success = False
            error = " Variable name  must be string"
        if variable == "" or variable is None:
            success = True
            error = ""
            return data, success, error
        if not isinstance(conditions, list):
            success = False
            error = " conditions should be list"
            return data, success, error
        if not (len(conditions) == 2):
            success = False
            error = " Conditions should contain only two elements," \
                    " first is conditional operator, " \
                    " second should be a list of conditional values"
            return data, success, error
        if not (isinstance(conditions[1], list)):
            success = False
            error = " conditional values should be given as list"
            return data, success, error
        if isinstance(conditions[1][0],(int,float)):
            data[variable] = data[variable].apply(pd.to_numeric, errors='coerce')
        try:
            data[variable] = data[variable].fillna(method='ffill').fillna(method='bfill')
        except Exception as e:
            success = False
            error = " mode tag is not available in the master data" + str(e)
        if success:
            condition = []
            for i in range(len(conditions[1])):
                condition.append("data['" + variable + "'] " + conditions[0] + " " + str(conditions[1][i]))
            # print(condition)
            if len(condition) > 1:
                final_condition = "(" + condition[0] + ")"
                for i in range(1, len(condition)):
                    final_condition += " | (" + condition[i] + ")"
            else:
                final_condition = condition[0]
            # print(final_condition)
            try:
                data.ix[eval(final_condition), 'filter'] = 1
            except Exception as e:
                success = False
                error = "filter condition is failed, check the filter condition" + str(e)
        # print("After filter data shape :", data.shape)
        return data, success, error

    @staticmethod
    def coerce_data(data: pd.DataFrame):
        """
        coerce the data to numeric
        :param data: pandas data frame
        :return:  coerced data as pandas data frame, success status, error
        """
        try:
            data = data.apply(pd.to_numeric, errors='coerce')
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " coercing to numeric of the master data is failed" + str(e)
        return data, success, error

    @staticmethod
    def remove_columns(data: pd.DataFrame, exclusion_columns: list):
        """
        This function remove the given input columns
        :param data: pandas data frame
        :param exclusion_columns (list) list of columns to be removed from data
        :return: data with columns removed as pandas data frame, success status, error logs
        """
        try:
            columns = list(data)
            subset_columns = [col for col in columns if col not in exclusion_columns]
            data = data[subset_columns]
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "exclusion of columns from master data failed" + str(e)
        return data, success, error

    @staticmethod
    def filter_rows_by_period(data: pd.DataFrame, period: dict):
        """
        this function filter rows of the data based on given period
        :param data: pandas data frame
        :param period:  dictionary with two keys start, end
        :return: filtered data as pandas data frame, success status, error logs
        """
        try:
            data = data.loc[period["start"]:period["end"]]
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " selecting training period in the master data is failed" + str(e)
        return data, success, error

    @staticmethod
    def filter_rows_by_column_values(data: pd.DataFrame, column: str, band_pass: dict):
        """
        this function filter the data based on band pass filter
        :param data:  pandas data frame
        :param column: filter will be applied on this column
        :param band_pass: dictionary with two keys lower_limit, upper_limit
        :return: filtered data as pandas data frame, success status, error logs
        """
        try:
            data = data[(data[column] > band_pass["lower_limit"]) &
                        (data[column] < band_pass["upper_limit"])]
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " Applying band pass filter to the master data is failed" + str(e)
        return data, success, error

    @staticmethod
    def filter_rows_by_column_null(data: pd.DataFrame, column: str):
        """
        this function filter the data based on band pass filter
        :param data:  pandas data frame
        :param column: filter will be applied on this column
        :return: filtered data as data frame, success status, error logs
        """
        try:
            data = data[(data[column].notnull())]
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " Applying band pass filter to the master data is failed" + str(e)
        return data, success, error

    @staticmethod
    def compute_prediction_deviation(data: pd.DataFrame):
        """
        This function compute the deviation in prediction with respect to target
        :param data: pandas data frame . this data frame should have two columns namely "target", "prediction"
        in addition data should contain the mode tag
        :return: data with deviation column, success status, error logs
        """
        try:
            target = data["target"]
            prediction = data["prediction"]
            deviation = target - prediction
            data["deviation"] = deviation
            data.loc[(data["filter"] == 1), "deviation"] = 0.0
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " unable to calculate deviation for the input data " + str(e)
        return data, success, error

    @staticmethod
    def create_valve(config: dict, master_data_file: str):
        """
        This function create a valve object using config dictionary and train the model and prepare for deployment
        :param config: (dictionary) a input from json file that configure each valve
        :param master_data_file: name and file path of master data file
        :return: valve object, success status and error logs
        """
        valve = VALVE()
        success, error = valve.assign_properties(config)
        if success:
            file = open(master_data_file, mode="rb")
            master_data = pickle.load(file)
            success, error = valve.find_feature_pi_tags(master_data)
        if success:
            success, error = valve.train_and_predict()
            #print(valve.feature_pi_tags)
        return valve, success, error

    def update_status(self, kpi1: int, kpi2: int):
        """
        this function update the latest status of the valved based on prediction
        :param kpi1: qsum (int) kpi1
        :param kpi2: qsum (int) kpi2
        :return: success status and error logs
        """
        try:
            self.status["valve_id"] = self.id
            self.status["description"] = self.description
            self.status["output_pi_tag"] = self.output_pi_tag
            self.status["alarm_KPI1"] = kpi1
            self.status["alarm_KPI2"] = kpi2
            self.status["alarm"] = self.output["alarm"].values[-1]
            self.status["alarm_trigger"] = self.output["alarm_trigger"].values[-1]
            self.status["last_predicted_time_stamp"] = self.output.index.strftime("%Y-%m-%d %H:%M:%S")[-1]
            self.status["mode"] = self.output["filter"].values[-1]
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "unable to update valve status " + str(e)
        return success, error

    def send_email(self):
        try:
            email_user = "BSP-PAM-CV@shell.com"
            email_send = ["mithun.cdharman@shell.com","Ankur.Parmar@shell.com", "s-r.subramanian@shell.com",
                          "A-M.Mohammad@shell.com","N-A.MohdSharif@shell.com","Yazid.Md-Yakub@shell.com","Wing-Chong.Leong@shell.com"]

            subject = "An alert has been detected for {}".format(self.id)

            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = '; '.join(email_send)
            msg['Subject'] = subject
            fp = open('./email_banner.jpg', 'rb')
            msg_image = MIMEImage(fp.read())
            fp.close()
            # Define the image's ID as referenced above
            msg_image.add_header('Content-ID', '<image1>')
            msg.attach(msg_image)
            body = 'Hi All, <br>' \
                + '<br>' \
                + 'An alert has been detected by the Machine Learning model for valve <b>{}</b>  , ' \
                 'please check the following link for more details'.format(self.id) \
                + '<br><br>' \
                + '<a href="' + "http://158.161.174.78:9999//" + '">Monitoring Dashboard</a><br><br>' \
                + '<br>' \
                + '<i>' + 'Note: This is an automated email notification by BSP PAM machine learning model. Please do not reply to this email. '  + '<i>' \
                + '<br><br>' \
                + '<b>' + ' Regards <br> Data Science Team' + '</b>' \
                + '<br>' \
                + '<img src="cid:image1">'
            msg.attach(MIMEText(body, 'html'))
            text = msg.as_string()
            # Send the email (this example assumes SMTP authentication is required)
            smtp = smtplib.SMTP(host='anonsmtp-eu.shell.com', port=25)
            # smtp.connect('smtp.gmail.com', 578)
            smtp.connect('anonsmtp-eu.shell.com', 25)
            smtp.ehlo()
            #smtp.starttls()
            smtp.ehlo()
        # smtp.login(strFrom, 'compressors123')
            smtp.sendmail(email_user, email_send, text)
            smtp.quit()
        except Exception as e:
            error = "Failed to send email alert due to --> " + str(e)
            logging.error(error)
            raise ValueError("Failed to send email alert due to --> " + str(e))
