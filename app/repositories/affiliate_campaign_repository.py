from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AffiliateCampaigns
from app.repositories.base_repository import BaseRepository
from app.schemas.affiliate_campaigns import (
    AffiliateCampaignPagination,
    AffiliateCampaignQueryRequest,
    AffiliateCampaignResponse,
)


class AffiliateCampaignRepository(
    BaseRepository[
        AffiliateCampaigns,
        AffiliateCampaignResponse,
        AffiliateCampaignPagination,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            model=AffiliateCampaigns,
            response_schema=AffiliateCampaignResponse,
            pagination_schema=AffiliateCampaignPagination,
            not_found_message="Campaign not found",
            already_exists_message="Campaign already exists",
            search_fields=["name", "description", "landing_page_url"],
        )

    async def get_all(
        self,
        db: AsyncSession,
        pagination: AffiliateCampaignQueryRequest,
    ) -> AffiliateCampaignPagination:
        filters = self.base_filters()

        if pagination.search:
            filters.extend(self.build_search_filters(pagination.search))

        if pagination.active is not None and hasattr(self.model, "active"):
            filters.append(self.model.active == pagination.active)

        if pagination.merchant_id:
            filters.append(self.model.merchant_id == pagination.merchant_id)

        if pagination.status is not None:
            filters.append(self.model.status == pagination.status)

        if pagination.campaign_type is not None:
            filters.append(self.model.campaign_type == pagination.campaign_type)

        count_stmt = select(func.count()).select_from(self.model)
        if filters:
            count_stmt = count_stmt.where(*filters)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        total_pages = (
            (total + pagination.page_size - 1) // pagination.page_size if total else 0
        )

        stmt = select(self.model)
        if filters:
            stmt = stmt.where(*filters)

        order_field = self.get_order_field()
        if order_field is not None:
            stmt = stmt.order_by(order_field.desc())

        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )

        result = await db.execute(stmt)
        items = result.scalars().all()

        return self.pagination_schema(
            items=[self.response_schema.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


affiliate_campaign_repository = AffiliateCampaignRepository()
