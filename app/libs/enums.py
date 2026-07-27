from enum import IntEnum


class DriftStatus(IntEnum):
    """交易状态"""

    Waiting = 1  # 等待
    Success = 2  # 成功
    Rejected = 3  # 拒绝
    Redraw = 4  # 撤销

    @classmethod
    def get_status_str(cls, status: int, key: str) -> str:
        key_map = {
            1: {
                "requester": "等待对方邮寄",
                "gifter": "等待你邮寄",
            },
            2: {
                "requester": "对方已邮寄",
                "gifter": "你已邮寄",
            },
            3: {
                "requester": "对方已拒绝",
                "gifter": "你已拒绝",
            },
            4: {
                "requester": "你已撤销",
                "gifter": "对方已撤销",
            },
        }
        return key_map[status][key]
