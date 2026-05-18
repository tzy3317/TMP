import os
from dotenv import load_dotenv

from exceptions import MissingConfigError, InvalidConfigError

_REQUIRED_VARS = ["LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY"]
_DEFAULT_TIMEOUT = 60
_DEFAULT_MAX_TOKENS = 4096
_DEFAULT_TEMPERATURE = 0.7
_DEFAULT_TOP_P = 1.0


class LLMConfig:
    __slots__ = ('_base_url', '_model', '_api_key', '_timeout', '_max_tokens', '_temperature', '_top_p')

    def __init__(self, base_url: str, model: str, api_key: str,
                 timeout: int = _DEFAULT_TIMEOUT,
                 max_tokens: int = _DEFAULT_MAX_TOKENS,
                 temperature: float = _DEFAULT_TEMPERATURE,
                 top_p: float = _DEFAULT_TOP_P) -> None:
        object.__setattr__(self, '_base_url', base_url)
        object.__setattr__(self, '_model', model)
        object.__setattr__(self, '_api_key', api_key)
        object.__setattr__(self, '_timeout', timeout)
        object.__setattr__(self, '_max_tokens', max_tokens)
        object.__setattr__(self, '_temperature', temperature)
        object.__setattr__(self, '_top_p', top_p)

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def model(self) -> str:
        return self._model

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def top_p(self) -> float:
        return self._top_p

    def __setattr__(self, name, value):
        raise AttributeError("LLMConfig is immutable")


def _load_env_file() -> None:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(root_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)


def _get_env_var(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return value.strip()


def _validate_required_vars() -> dict[str, str]:
    result = {}
    for var_name in _REQUIRED_VARS:
        value = _get_env_var(var_name)
        if value is None:
            raise MissingConfigError(var_name)
        result[var_name] = value
    return result


def _validate_url_format(url: str) -> None:
    if not (url.startswith("http://") or url.startswith("https://")):
        raise InvalidConfigError(
            variable="LLM_BASE_URL",
            value=url,
            reason="必须以 http:// 或 https:// 开头"
        )
    if not url.endswith("/v1"):
        raise InvalidConfigError(
            variable="LLM_BASE_URL",
            value=url,
            reason="必须以 /v1 结尾"
        )
    if url.endswith("/v1/"):
        raise InvalidConfigError(
            variable="LLM_BASE_URL",
            value=url,
            reason="末尾有多余斜杠，应为 /v1 而非 /v1/"
        )


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    prefix = key[:4]
    suffix = key[-4:]
    return prefix + "***...***" + suffix


def _build_config() -> LLMConfig:
    _load_env_file()
    required = _validate_required_vars()
    _validate_url_format(required["LLM_BASE_URL"])
    config = LLMConfig(
        base_url=required["LLM_BASE_URL"],
        model=required["LLM_MODEL"],
        api_key=required["LLM_API_KEY"]
    )
    return config


LLM_CONFIG: LLMConfig = _build_config()