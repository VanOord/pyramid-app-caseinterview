from abc import ABCMeta
from functools import partial
from uuid import UUID as pyUUID

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import MetaData
from sqlalchemy.types import Float

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class DeclarativeABCMeta(DeclarativeMeta, ABCMeta):
    """Intersection of DeclarativeMeta and ABCMeta."""

    pass


declarative_base_with_abc = partial(declarative_base, metaclass=DeclarativeABCMeta)

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base_with_abc(metadata=metadata)


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
