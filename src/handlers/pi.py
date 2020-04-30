from handlers.libraries import *


class PI(object):
    # ################## Define the PI Server here .
    # To get the right name-> open the tool
    # "AboutSDK" -> go to connections -> get the name of the PI Server from the list of available PI Servers
    # PIServerName = 'mus-as-111'  # Name of the PIServer
    # StartTime = '01-01-2018 00:00:00'  # StartTime in LocalTime in "DD-MM-YYYY HH:MM:SS" format
    # EndTime = '02-01-2018 00:00:00'  # End time in LocalTime in "DD-MM-YYYY HH:MM:SS" format
    # Retrieval_Interval = '10m'  # Frequency of retrieval of Data points from PI
    # Input_TagListCSV = 'tag_list.csv'  # List of PI Tags
    # Output_PIDataCSV = 'PDOTest.csv'  # Retrieved data of PITags in LocalTimeStamp (not in UTC)
    # ################## Change the PI Server name to the correct PI Server ################

    def __init__(self, pi_server: str):
        """
        initialize pi object to do pi related activities
        :param pi_server: name of the pi server
        """
        try:
            self.pi_srv = Dispatch('PISDK.PISDK').Servers(pi_server)
            self.pi_time = Dispatch('PITimeServer.PITime')
            self.pi_time_intervals = Dispatch('PITimeServer.TimeIntervals')
            self.pi_time_format = Dispatch('PITimeServer.PITimeFormat')
        except Exception as e:
            raise ValueError("unable to contact pi_server : " + str(pi_server) + " " + str(e))

    def get_snapshot(self, tag_name: str):
        """
        Retrieve the last known value of the PI-tag
        :param tag_name: (str): PI tag name
        :return: pandas data frame: index=datetime, col_1=interpolated values, success status and error logs
        """
        data = pd.DataFrame()
        try:
            tag = self.pi_srv.PIPoints(tag_name)
            data, success, error = self.to_df([tag.Data.Snapshot], tag_name)
        except Exception as e:
            success = False
            error = " unable to fetch snapshot of pi data" + str(e)
        return data, success, error

    def get_data(self, tag_name: str, t_start: str, t_end: str, t_interval: str):
        """
        Retrieve interpolated data from the PI-serverF
        :param tag_name: (str): PI tag name
        :param t_start: (str): PI time format (ex. '*-72h')
        :param t_end: (str): PI time format (ex. '*')
        :param t_interval: (str): PI time format (ex. '1h')
        :return: pandas data frame: index=datetime, col_1=interpolated values, success status and error logs
        """
        data = pd.DataFrame()
        try:
            tag = self.pi_srv.PIPoints(tag_name)
            pi_values = tag.Data.InterpolatedValues2(t_start, t_end, t_interval, asynchStatus=None)
            data, success, error = self.to_df(pi_values, tag_name)
        except Exception as e:
            success = False
            error = " unable to fetch pi data" + str(e)
        return data, success, error

    def get_data_multiple(self, tags: list, t_start: str, t_end: str, t_interval: str):
        """
        Retrieve interpolated data from the PI-server for multiple tags
        :param tags: (list): List of PI tag names
        :param t_start: (str): PI time format (ex. '*-72h')
        :param t_end: (str): PI time format (ex. '*')
        :param t_interval: (str): PI time format (ex. '1h')
        :return: pandas data frame: index=datetime, cols=interpolated values, success status, error logs
        """
        values = []
        df_values = pd.DataFrame()
        success = True
        error = ""
        try:
            for tag in tags:
                df, success, error = self.get_data(tag, t_start, t_end, t_interval)
                # drop duplicated indices -> result of summer-to-winter time
                # transition. Not doing this results in the subsequent join() to
                # spiral out of control
                try:
                    df = df[~df.index.duplicated()]
                    values.append(df)
                except Exception as e:
                    success = False
                    error = "Unable to get data for -" + tag + "--" + str(e)
                    break
            df_values = pd.DataFrame().join(values, how='outer')
        except Exception as e:
            success = False
            error = "Unable to get data " + str(e)
        return df_values, success, error

    def is_valid_tag(self, tag_name: str):
        """
        Checks whether the tag_name exists on the PI-server
        :param tag_name: (str): PI tag name
        :return: boolean: Returns boolean True in case the tag exists, success status and error logs
        """
        try:
            self.pi_srv.PIPoints(tag_name)
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "not a valid tag" + str(e)
        return success, error

    def to_df(self, pi_values: list, col_name: str = 'value'):
        """
        Converts a list of PI-value objects to a pandas data frame
        :param pi_values: (list): List of PI-value objects
        :param col_name: (str): desired name of the pandas df column
        :return: data frame: index=datetime, column=list_of_values, success status and error logs
        """
        success = True
        error = ""
        data = pd.DataFrame()
        try:
            values = []
            date_time = []
            for v in pi_values:
                try:
                    # values.append(float(v.Value))
                    values.append(str(v.Value))
                    dt, success, error1 = self.epoch_to_dt(v.TimeStamp)
                    if success:
                        date_time.append(dt)
                    else:
                        error += error1
                except Exception as e:
                    error += str(e)
                    pass
            data = pd.DataFrame({'Timestamp': date_time, col_name: values})
            data = data.set_index('Timestamp')
        except Exception as e:
            success = False
            error = "Unable to convert pi data to pandas data frame:" + str(e)
        return data, success, error

    def time_format(self, arg: str):
        """
        Converts a relative time str to a PI datetime formatted string
        :param arg: (str): relative time string i.e. '*' or '*-24h'
        :return: str: formatted datetime i.e. '17-10-2017 9:48:15', success status, error logs
        """
        try:
            self.pi_time_format.InputString = arg
            dt = self.pi_time_format.OutputString
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "Unable to format datetime " + str(e)
            dt = None
        return dt, success, error

    def write_back_to_pi(self, tag_name: str, value: str, time_stamp: str):
        """
        Write Back Values to PI
        :param tag_name: (str): PITagName
        :param value: (str):Value to write
        :param time_stamp: (str): LocalTime in "DD-MM-YYYY HH:MM:SS" format
        :return success status and error logs
        """
        pi_server = self.pi_srv
        try:
            pi_tag = pi_server.PIPoints(tag_name)
            try:
                pi_tag.Data.UpdateValue(value, time_stamp, 0, None)
                success = True
                error = ""
            except Exception as e:
                success = False
                error = " You need write access on the PI Tag mentioned: " + str(e)
        except Exception as e:
            success = False
            error = "PI TagName not found in PI Server: " + str(e)
        return success, error

    @staticmethod
    def epoch_to_dt(timestamp: float):
        """
        Convert epoch to human readable date
        :param timestamp: (float): Unix epoch timestamp i.e. '1508227058.0'
        :return: (datetime object) , success status, error logs
        """
        dt = None
        try:
            dt = datetime.fromtimestamp(timestamp)
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "Failed to Convert Time Stamp " + str(e)
        return dt, success, error
