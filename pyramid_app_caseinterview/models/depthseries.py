from uuid import UUID as pyUUID

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Float

from pyramid_app_caseinterview.models import Base


class Depthseries(Base):
    __tablename__ = "depthseries"

    id: Mapped[pyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )
    depth: Mapped[float] = mapped_column(Float, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=True)
