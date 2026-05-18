class ConfigError(Exception):
    """配置错误基类"""
    pass


class MissingConfigError(ConfigError):
    """必配环境变量缺失"""

    VARIABLE: str

    def __init__(self, variable: str) -> None:
        self.VARIABLE = variable
        message = f"配置错误：环境变量 '{variable}' 未设置。\n请检查 .env 文件"
        super().__init__(message)


class InvalidConfigError(ConfigError):
    """配置值格式错误"""

    VARIABLE: str
    VALUE: str
    REASON: str

    def __init__(self, variable: str, value: str, reason: str) -> None:
        self.VARIABLE = variable
        self.VALUE = self._mask(value)
        self.REASON = reason
        message = f"配置错误：'{variable}' 的值无效。\n原因：{reason}\n当前值：{self.VALUE}"
        super().__init__(message)

    @staticmethod
    def _mask(value: str) -> str:
        return value[:4] + "***" + value[-4:] if len(value) > 8 else "***"