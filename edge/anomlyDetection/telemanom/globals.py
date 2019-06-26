import sys
import os
import typing as tp
from datetime import datetime as dt
import logging
import yaml


class ConfigInformation:
    def __init__(self, config):
        self.config = config
        self.time = dt.now().strftime("%Y-%m-%d_%H.%M.%S")
        self._logger = None

        self._modelPath = os.path.join(
            "model", config.model_id + ".h5")
        self._logPath = os.path.join(
            'log', ''.join( ( config.model_id, '_', self.time, '.log')))

        self._smoothedErrorPath = os.path.join(
            "result", ''.join( ( config.model_id, '_', self.time, '_smoothed_error-%s.npy')))
        self._y_hat_path = os.path.join(
            "result", ''.join( ( config.model_id, '_', self.time, '_y_hat-%s.npy')))

    def checkDirsAndFiles(self):

        paths = ['model', 'log', 'result']
        for p in paths:
            try:
                os.makedirs( p)
            except FileExistsError:
                print( "directory '%s' exists as a file" % (p,))
                # sys.exit(1)

        mp = self._modelPath
        if os.path.isfile( mp):
            if self.config.train:
                # 清除旧的模型文件
                try:
                    os.remove( mp)
                except OSError:
                    print( "cannot delete old model file '%s'" % (mp,))
                    sys.exit(1)
        elif not self.config.train:
            # 模型文件不存在
            print( "model file '%s' must exist when predicting" % (mp,))
            sys.exit(1)

    def setupLogger(self):
        self._logger = logging.getLogger( 'telemanom')

        hdlr = logging.FileHandler( self._logPath)
        formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter( formatter)
        self._logger.addHandler( hdlr)
        self._logger.setLevel( logging.INFO)

        stdout = logging.StreamHandler( sys.stdout)
        stdout.setLevel( logging.INFO)
        self._logger.addHandler( stdout)

        self._logger.info( "Runtime params:")
        self._logger.info( "----------------")
        for attr in dir( self.config):
            if "__" not in attr and attr != 'info':
                self._logger.info( '%s: %s' % ( attr, getattr( self.config, attr)))
        self._logger.info( "----------------\n")

    @property
    def modelPath(self):
        return self._modelPath

    @property
    def logger(self):
        return self._logger

    def smoothedErrorPath(self, testName):
        return self._smoothedErrorPath % (testName,)

    def y_hat_path(self, testName):
        return self._y_hat_path % (testName,)


class Config:
    """Loads parameters from config.yaml into global object"""

    def __init__( self, paths: tp.List[str], train: bool):
        """
        读取配置文件。运行时将被覆盖的属性名：config_paths  info  train

        :param paths: 配置文件路径的列表
        :param train: 布尔值，为真则为训练，为假则为预测
        """

        config_paths = []

        for p in paths:
            if not os.path.isfile( p):
                print( "config file '%s' cannot be detected and is ignored" % (p,))
                continue
            config_paths.append(p)

            with open( p, "r") as f:
                dictionary = yaml.load( f.read(), Loader=yaml.SafeLoader)
                for k, v in dictionary.items():
                    setattr( self, k, v)

        self.config_paths = config_paths
        self.info: ConfigInformation = None
        self.train = train


_global_config: Config = None


def installGlobalConfig( conf: Config):
    global _global_config
    _global_config = conf
    conf.info = ConfigInformation( conf)
    conf.info.checkDirsAndFiles()
    conf.info.setupLogger()


def getGlobalConfig():
    return _global_config
