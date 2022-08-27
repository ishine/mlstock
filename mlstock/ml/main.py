import argparse
import logging
import os.path

from mlstock.ml.data import factor_service
from mlstock.ml.train.train_pct import TrainPct
from mlstock.ml.train.train_winloss import TrainWinLoss
from mlstock.utils import utils

logger = logging.getLogger(__name__)


def load_data(args):
    start_date = args.start_date
    end_date = args.end_date
    num = args.num
    is_industry_neutral = args.industry_neutral

    if args.preload is not None:
        if not os.path.exists(args.preload):
            logger.error("训练数据文件[%s]不存在！", args.preload)
            exit()
        df_data, factor_names = factor_service.load_from_file(args.preload)
        return df_data, factor_names

    # 那么就需要从新计算了
    df_weekly, factor_names = factor_service.calculate(start_date, end_date, num, is_industry_neutral)
    return df_weekly, factor_names


def main(args):
    df_data, factor_names = load_data(args)

    train_pct = TrainPct(factor_names)
    train_winloss = TrainWinLoss(factor_names)

    if args.train == 'all':
        train_pct.evaluate(train_pct.train(df_data))
        train_winloss.evaluate(train_winloss.train(df_data))
        return
    if args.train == 'pct':
        train_pct.evaluate(train_pct.train(df_data))
        return
    if args.train == 'winloss':
        train_winloss.evaluate(train_winloss.train(df_data))
        return


"""
python -m mlstock.ml.main -d
python -m mlstock.ml.main -d --train all
python -m mlstock.ml.main -d --train pct
python -m mlstock.ml.main -d --train winloss
python -m mlstock.ml.main -d --train winloss --preload data/features_20180101_20200101_20220815165011.csv
python -m mlstock.ml.main -n 50 -d
python -m mlstock.ml.main -n 50 -d -s 20080101 -e 20220901
python -m mlstock.ml.main -n 50 -d -s 20180101 -e 20200101
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # 数据相关的
    parser.add_argument('-s', '--start_date', type=str, default="20090101", help="开始日期")
    parser.add_argument('-e', '--end_date', type=str, default="20220901", help="结束日期")
    parser.add_argument('-n', '--num', type=int, default=100000, help="股票数量，调试用")
    parser.add_argument('-p', '--preload', type=str, default=None, help="预先加载的因子数据文件的路径，不再从头计算因子")
    parser.add_argument('-in', '--industry_neutral', action='store_true', default=False, help="是否做行业中性处理")

    # 训练相关的
    parser.add_argument('-t', '--train', type=str, default="all", help="all|pct|winloss : 训练所有|仅训练收益|仅训练涨跌")

    # 全局的
    parser.add_argument('-d', '--debug', action='store_true', default=False, help="是否调试")

    args = parser.parse_args()

    if args.debug:
        print("【调试模式】")
        utils.init_logger(file=True, log_level=logging.DEBUG)
    else:
        utils.init_logger(file=True, log_level=logging.INFO)

    main(args)
