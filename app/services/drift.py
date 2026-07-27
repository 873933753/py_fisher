from app.models.drift import Drift
from app.models.gift import Gift
from app.models.wish import Wish
from app.libs.enums import DriftStatus
from app.database import auto_commit
from sqlmodel import Session
from app.models.user import User
from app.forms.drift import DriftForm
from app.view_models.product import ProductViewModel


# 确认已邮寄的业务逻辑
def confirm_mailed(session: Session, drift: Drift, current_user: User) -> None:
    gift = Gift.get_gift_by_id(session, drift.gift_id)
    wish = Wish.get_wish_by_user(session, gift.isbn, drift.requester_id)
    with auto_commit(session):
        drift.status = DriftStatus.Success
        current_user.beans += 1  # 邮寄成功 +1
        gift.launched = True  # 当前用户 - 商品状态修改为已赠送
        wish.launched = True  # 索要用户 - 心愿清单状态修改为已完成


# 提交索要的业务逻辑
def create_drift_request(
    session: Session,
    form: DriftForm,
    current_user: User,
    gift: Gift,
) -> Drift:
    current_product = ProductViewModel.from_record(gift.book)

    drift = Drift(
        recipient_name=form.recipient_name,
        mobile=form.mobile,
        message=form.message,
        address=form.address,
        gift_id=gift.id,
        gifter_id=gift.user_id,
        gifter_nickname=gift.user.nickname,
        requester_id=current_user.id,
        requester_nickname=current_user.nickname,
        product_title=current_product.productName,
        isbn=current_product.isbn,
        product_img=current_product.image,
    )

    with auto_commit(session):
        session.add(drift)
        current_user.beans -= 1

    return drift


# 撤销索要的业务逻辑
def redraw_drift_request(
    session: Session,
    drift: Drift,
    current_user: User,
) -> None:
    with auto_commit(session):
        drift.status = DriftStatus.Redraw
        current_user.beans += 1


# 拒绝索要的业务逻辑
def request_reject_service(
    session: Session,
    drift: Drift,
) -> None:
    requester = User.get_user_by_id(session, drift.requester_id)
    with auto_commit(session):
        drift.status = DriftStatus.Rejected
        requester.beans += 1
