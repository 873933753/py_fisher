from app.schemas.drift import DriftItem, DriftListData, DriftDetail
from app.libs.enums import DriftStatus


# 单个drift
class DriftViewModel:
    def _prepare_data(drift, user_id: int) -> dict:
        data = drift.model_dump()
        # 判断当前用户是请求者还是赠送者
        data["you_are"] = "requester" if drift.requester_id == user_id else "gifter"
        # 判断交易文字显示
        data["status_str"] = DriftStatus.get_status_str(drift.status, data["you_are"])
        data["operator"] = (
            drift.gifter_nickname
            if data["you_are"] == "requester"
            else drift.requester_nickname
        )
        return data

    @staticmethod
    def to_item(drift, user_id: int) -> DriftItem:
        return DriftItem.model_validate(DriftViewModel._prepare_data(drift, user_id))

    @staticmethod
    def to_detail(drift, user_id: int) -> DriftDetail:
        return DriftDetail.model_validate(DriftViewModel._prepare_data(drift, user_id))


# drift列表
class DriftCollectionViewModel:
    """列表"""

    def __init__(self, drifts, user_id: int):
        self.total = len(drifts)
        self.items = [DriftViewModel.to_item(d, user_id) for d in drifts]

    def to_schema(self) -> DriftListData:
        return DriftListData(items=self.items)
