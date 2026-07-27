import requests
from dataclasses import dataclass
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


# 定义一个类，封装 HTTP 请求结果
@dataclass
class HttpResult:
    ok: bool
    status: int
    data: Any = None
    message: Optional[str] = None
    code: Optional[int] = None


# 定义一个类，封装 HTTP 请求方法
class HTTP:
    @staticmethod  # 静态方法，不需要实例化类就可以调用，调用时参数会按位置一一对应
    def _get(url, return_json=True):
        # r 是 requests.get(url) 的响应对象，return_json 默认 True，表示希望按 JSON 解析。
        r = requests.get(url)
        # 如果响应状态码不是 200，则返回空字典或空字符串（原数据格式决定）
        if r.status_code != 200:
            return {} if return_json else ""
        # 如果响应状态码是 200，则返回 JSON 数据或文本数据，取决于 return_json 的值。
        # 三元表达式：return_json=True → r.json() -返回 JSON 数据；
        # return_json=False → r.text -返回文本数据。
        return r.json() if return_json else r.text

    # def post(url, data, return_json=True):
    #   r = requests.post(url, data=data)
    #   if r.status_code != 200:
    #     return {} if return_json else ''
    #   return r.json() if return_json else r.text

    @staticmethod
    def get(url, timeout=20) -> HttpResult:
        try:
            r = requests.get(url, timeout=timeout)
            result = HTTP._build_result(r)
            if not result.ok:
                logger.warning(
                    "第三方请求失败 url=%s status=%s code=%s msg=%s",
                    url,
                    result.status,
                    result.code,
                    result.message,
                )
            return result
        except requests.Timeout:
            return HttpResult(ok=False, status=0, message="请求超时")
        except requests.RequestException as e:
            return HttpResult(ok=False, status=0, message=str(e))

    # 解析响应体为 JSON 或文本
    @staticmethod
    def _parse_body(r: requests.Response) -> Any:
        """尝试把响应体解析成 JSON，失败则返回原始文本"""
        try:
            return r.json()
        except ValueError:
            return r.text

    # 分析响应体，提取业务信息
    @staticmethod
    def _build_result(r: requests.Response) -> HttpResult:
        body = HTTP._parse_body(r)
        status = r.status_code
        # 从 body 里提取业务信息
        # 情况1: 响应体是字典
        if isinstance(body, dict):
            biz_code = body.get("code")
            biz_msg = body.get("msg") or body.get("message")
            biz_data = body.get("data")
        else:
            # 情况2: 响应体是文本
            biz_code = None
            biz_msg = str(body)[:200] if body else None
            biz_data = None

        # 情况1: HTTP 非 200 → 失败
        if status != 200:
            return HttpResult(
                ok=False,
                status=status,
                data=biz_data,
                message=biz_msg or f"HTTP {status}",
                code=biz_code,
            )
        # 情况2: HTTP 200 但业务 code 表示失败（很多接口这样）
        if biz_code is not None and biz_code not in (200, "200", 0):
            return HttpResult(
                ok=False,
                status=status,
                data=biz_data,
                message=biz_msg or "业务错误",
                code=biz_code,
            )
        # 情况3: 成功
        return HttpResult(
            ok=True,
            status=status,
            data=body,  # 完整 body，Spider 再取 data.records
            message=biz_msg,
            code=biz_code,
        )

    @staticmethod
    def post(url, data=None, json=None, timeout=20) -> HttpResult:
        try:
            r = requests.post(url, data=data, json=json, timeout=timeout)
            result = HTTP._build_result(r)
            # 请求失败 - 500、404、403等HTTP状态码
            if not result.ok:
                logger.warning(
                    "第三方请求失败 url=%s status=%s code=%s msg=%s",
                    url,
                    result.status,
                    result.code,
                    result.message,
                )
            return result
        except requests.Timeout:
            return HttpResult(ok=False, status=0, message="请求超时")
        # 请求不存在等其他异常
        except requests.RequestException as e:
            return HttpResult(ok=False, status=0, message=str(e))
