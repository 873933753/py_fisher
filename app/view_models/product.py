from app.schemas.product import ProductItem, ProductSearchData


class ProductViewModel:
    @staticmethod
    def _first_image(record: dict) -> str:
        main_img_list = record.get("mainImgList") or []
        if main_img_list and isinstance(main_img_list[0], dict):
            return main_img_list[0].get("fileUrl", "")
        return ""

    @classmethod
    def from_record(cls, record: dict) -> ProductItem:
        return ProductItem(
            id=str(record.get("id", "")),
            productName=record.get("productName", ""),
            productSubtitle=record.get("productSubtitle", "") or "",
            salePrice=record.get("salePrice", ""),
            orgPrice=float(record.get("orgPrice") or 0),
            stock=int(record.get("stock") or 0),
            image=cls._first_image(record),
            isbn=record.get("productName", ""),  # 原始 productName → isbn
        )


class ProductCollectionViewModel:
    def __init__(self):
        self.data: ProductSearchData | None = None

    def fill(self, yushu_product, keyword: str, page: int, size: int):
        self.data = ProductSearchData(
            keyword=keyword,
            page=page,
            size=size,
            total=yushu_product.total,
            pages=yushu_product.pages,
            type=yushu_product.type,
            items=[
                ProductViewModel.from_record(record) for record in yushu_product.list
            ],
        )
