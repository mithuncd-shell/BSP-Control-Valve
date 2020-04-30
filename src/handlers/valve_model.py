from handlers.libraries import *


class MODEL:
    def __init__(self):
        """
        Initialize the valve model object
        """
        self.algorithm_name = "lasso"
        self.algorithm = Lasso(alpha=0.1, max_iter=10000, tol=0.1, normalize=False)
        self.train = self.algorithm.fit
        self.predict = self.algorithm.predict
        self.parameter = {"Alpha": 0.1, "Max_iter": 10000, "Tol": 0.1, "Normalize": False}
        self.KPI = {"RMSE": None, "MAE": None, "R2": None}
        # print(self)

    def select_algorithm(self, name: str = "lasso"):
        """
        This function assign the model parameters according to the user model choice
        :param name: (str) name of the model
        :return: success status and error logs
        """
        success = True
        error = ""
        self.algorithm_name = name.lower()
        if self.algorithm_name == "lasso":
            self.algorithm = Lasso(alpha=0.1, max_iter=10000, tol=0.1, normalize=False)
            self.parameter = {"Alpha": 0.1, "Max_iter": 10000, "Tol": 0.1, "Normalize": False}
        elif self.algorithm_name == "ridge":
            self.algorithm = Ridge(alpha=0.1, max_iter=10000, tol=0.1, normalize=False)
            self.parameter = {"Alpha": 0.1, "Max_iter": 10000, "Tol": 0.1, "Normalize": False}
        elif self.algorithm_name == "elasticnet":
            self.algorithm = ElasticNet(alpha=0.1, max_iter=5000, random_state=0,fit_intercept=True, precompute=False)
            self.parameter = {"Alpha": 0.1, "Random_state": 0, "Max_iter": 5000, "Fit_intercept": True,
                              "Precompute": False}
        elif self.algorithm_name == "Randomforest":
            self.algorithm = RandomForestRegressor()
            self.parameter = {"SubsamplingRate": 0.7, "NumTrees": 500, "FeatureSubsetStrategy": "auto",
                              "ExpCoeff": True, "Compact": True, "RandomState": 0}
        else:
            success = False
            error = "wrong algorithm selected, choose one among the four (lasso, ridge, elasticnet, randomforest"
        if not success:
            return success, error
        self.train = self.algorithm.fit
        self.predict = self.algorithm.predict
        return success, error

    def get_coeff(self, tags: list):
        """
        get the coeff for each of tag from the model
        :param tags: list of tags
        :return: success status, error logs
        """
        coeff = pd.DataFrame()
        try:
            # print(self.algorithm.coef_)
            coeff = pd.DataFrame(np.array([tags, list(self.algorithm.coef_)]).transpose(),
                                 columns=['Input_column', 'Coefficient'])
            coeff['Coefficient'] = pd.to_numeric(coeff['Coefficient'], errors='coerce')
            coeff['abs_coeff'] = abs(coeff['Coefficient'])
            coeff = coeff.sort_values(by='abs_coeff', ascending=False).reset_index(drop=True)
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "unable to get the coeff" + str(e)
        return coeff, success, error

    def get_kpi(self, target, predicted):
        """
        This function calculate KPIs for the given data set
        :param target:  actual valve opening values
        :param predicted: predicted valve opening  values
        :return: success status and error logs
        """
        try:
            self.KPI["MAE"] = mean_absolute_error(target, predicted)
            self.KPI["RMSE"] = mean_squared_error(target, predicted)
            self.KPI["R2"] = r2_score(target, predicted)
            success = True
            error = ""
        except Exception as e:
            success = False
            error = " unable to compute model KPIs" + str(e)
        return success, error

    def train_model(self, x: np.array, y: np.array):
        """
        this function train the model
        :param x: (numpy array) set of independent variables data
        :param y: (numpy array 1d) set of dependent variable data
        :return: success status and error logs
        """
        try:

            self.train = self.algorithm.fit(np.array(x), np.array(y).T)
            success = True
            error = ""
        except Exception as e:
            success = False
            error = "unable to fit the model" + str(e)
        return success, error
