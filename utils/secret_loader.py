import os
from typing import Optional
from utils.cmbird_logger import logger
from utils.crypto import CryptoUtil


def get_secret(env_name: str, passphrase_env: Optional[str] = None, default: Optional[str] = None) -> Optional[str]:
    """从环境变量读取机密，支持明文与 ENC 信封格式，并可用口令解密。

    - 明文：以 "plain:" 开头，返回其余部分
    - 加密：以 "ENC:" 开头，使用 passphrase_env 指定的口令环境变量解密
    - 其他：直接返回原值
    """
    val = os.getenv(env_name)
    if val is None:
        logger.debug(f"环境变量 {env_name} 未设置，返回默认值")
        return default

    low = val.lower()
    if low.startswith("plain:"):
        return val[len("plain:"):]

    if low.startswith("enc:"):
        passphrase = os.getenv(passphrase_env) if passphrase_env else None
        if not passphrase:
            logger.error(f"解密失败：未提供口令环境变量 {passphrase_env}")
            return default
        try:
            return CryptoUtil.decrypt_envelope(val, passphrase)
        except Exception as e:
            logger.error(f"解密环境变量 {env_name} 失败: {e}")
            return default

    return val


def encrypt_for_env(plaintext: str, passphrase: str) -> str:
    """将明文使用口令加密为 ENC 信封字符串，适合写入环境变量"""
    return CryptoUtil.encrypt_text_with_password(plaintext, passphrase)