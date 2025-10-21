from __future__ import annotations
import os
import base64
from dataclasses import dataclass
from typing import Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from utils.cmbird_logger import logger


@dataclass(frozen=True)
class EnvelopeV1:
    """加密信封格式 v1
    格式字符串：ENC:v1|alg=aesgcm|salt=<b64>|nonce=<b64>|ct=<b64>
    """
    alg: str
    salt_b64: str
    nonce_b64: str
    ct_b64: str

    def as_string(self) -> str:
        return f"ENC:v1|alg={self.alg}|salt={self.salt_b64}|nonce={self.nonce_b64}|ct={self.ct_b64}"

    @staticmethod
    def parse(s: str) -> "EnvelopeV1":
        if not s or not s.lower().startswith("enc:"):
            raise ValueError("不是 ENC 信封字符串")
        body = s[len("ENC:"):]
        parts = body.split("|")
        if len(parts) < 4 or not parts[0].lower().startswith("v1"):
            raise ValueError("不支持的信封版本")
        kv = {}
        for p in parts[1:]:
            k, _, v = p.partition("=")
            kv[k] = v
        alg = kv.get("alg", "aesgcm")
        salt_b64 = kv.get("salt")
        nonce_b64 = kv.get("nonce")
        ct_b64 = kv.get("ct")
        if not salt_b64 or not nonce_b64 or not ct_b64:
            raise ValueError("信封缺少必要字段")
        return EnvelopeV1(alg, salt_b64, nonce_b64, ct_b64)


class CryptoUtil:
    """加密工具类：使用 AES-GCM 与 PBKDF2 派生密钥"""
    DEFAULT_ALG = "aesgcm"

    @staticmethod
    def _derive_key(password: str, salt: bytes, length: int = 32, iterations: int = 200_000) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=length, salt=salt, iterations=iterations)
        return kdf.derive(password.encode("utf-8"))

    @staticmethod
    def encrypt_text_with_password(text: str, password: str) -> str:
        if text is None:
            raise ValueError("text 不能为空")
        if not password:
            raise ValueError("password 不能为空")
        salt = os.urandom(16)
        key = CryptoUtil._derive_key(password, salt)
        aes = AESGCM(key)
        nonce = os.urandom(12)
        ct = aes.encrypt(nonce, text.encode("utf-8"), None)
        env = EnvelopeV1(
            alg=CryptoUtil.DEFAULT_ALG,
            salt_b64=base64.b64encode(salt).decode("ascii"),
            nonce_b64=base64.b64encode(nonce).decode("ascii"),
            ct_b64=base64.b64encode(ct).decode("ascii"),
        )
        logger.debug("文本加密完成，生成 ENC 信封")
        return env.as_string()

    @staticmethod
    def decrypt_envelope(envelope: str, password: str) -> str:
        if not password:
            raise ValueError("password 不能为空")
        env = EnvelopeV1.parse(envelope)
        if env.alg.lower() != CryptoUtil.DEFAULT_ALG:
            raise ValueError(f"不支持的算法: {env.alg}")
        salt = base64.b64decode(env.salt_b64)
        nonce = base64.b64decode(env.nonce_b64)
        ct = base64.b64decode(env.ct_b64)
        key = CryptoUtil._derive_key(password, salt)
        aes = AESGCM(key)
        pt = aes.decrypt(nonce, ct, None)
        logger.debug("信封解密完成")
        return pt.decode("utf-8")