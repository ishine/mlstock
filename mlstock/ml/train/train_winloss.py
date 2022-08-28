import logging

from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from mlstock.ml.train.train_action import TrainAction
from mlstock.utils import utils

logger = logging.getLogger(__name__)


class TrainWinLoss(TrainAction):

    def get_model_name(self):
        return f"winloss_xgboost_{utils.now()}.model"

    def set_target(self, df_data):
        df_data['target'] = df_data.target.apply(lambda x: 1 if x > 0 else 0)
        logger.info("设置target为分类：0跌，1涨")
        return df_data

    def _train(self, X_train, y_train):
        """
        Xgboost来做输赢判断，参考：https://cloud.tencent.com/developer/article/1656126
        :return:
        """
        # https://so.muouseo.com/qa/em6w1x8w20k8.html
        le = LabelEncoder()
        y_train = le.fit_transform(y_train)

        # 创建xgb分类模型实例
        model = XGBClassifier(nthread=1)
        # 待搜索的参数列表空间
        param_lst = {"max_depth": [3, 5, 7, 9],
                     "n_estimators": [*range(10, 110, 20)]}  # [10, 30, 50, 70, 90]

        # 创建网格搜索
        grid_search = GridSearchCV(model,
                                   param_grid=param_lst,
                                   cv=5,
                                   verbose=10,
                                   scoring='auc',
                                   n_jobs=16)  # 最多16个进程同时跑
        # 基于flights数据集执行搜索
        grid_search.fit(X_train, y_train)

        # 输出搜索结果
        logger.debug("GridSearch出最优参数：%r", grid_search.best_estimator_)

        return grid_search.best_estimator_