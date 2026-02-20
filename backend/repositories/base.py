"""
Base repository class providing common CRUD operations and SQLAlchemy async session management.

All concrete repositories inherit from BaseRepository to gain standardized
create, read, update, delete, and list operations against SQLAlchemy models.
The repository layer encapsulates all ORM/SQL logic — services interact via
repository interfaces only.
"""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic base repository providing common CRUD operations for SQLAlchemy models.

    Type Parameters:
        T: The SQLAlchemy model class this repository manages.

    Attributes:
        model: The SQLAlchemy model class.
        session: The async database session for executing queries.
    """

    model: Type[T]

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the base repository with an async database session.

        Args:
            session: SQLAlchemy AsyncSession instance for database operations.
        """
        self.session = session

    async def get_by_id(self, record_id: int) -> Optional[T]:
        """
        Retrieve a single record by its primary key ID.

        Args:
            record_id: The integer primary key of the record.

        Returns:
            The model instance if found, None otherwise.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == record_id)
        )
        return result.scalars().first()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[T]:
        """
        Retrieve all records with optional pagination.

        Args:
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of model instances.
        """
        result = await self.session.execute(
            select(self.model)
            .order_by(self.model.id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """
        Retrieve a single record matching a specific field value.

        Args:
            field_name: Name of the model column to filter on.
            value: The value to match against.

        Returns:
            The first matching model instance, or None if not found.

        Raises:
            AttributeError: If the field_name does not exist on the model.
        """
        column = getattr(self.model, field_name)
        result = await self.session.execute(
            select(self.model).where(column == value)
        )
        return result.scalars().first()

    async def get_many_by_field(
        self,
        field_name: str,
        value: Any,
        offset: int = 0,
        limit: int = 100,
    ) -> List[T]:
        """
        Retrieve multiple records matching a specific field value with pagination.

        Args:
            field_name: Name of the model column to filter on.
            value: The value to match against.
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of matching model instances.

        Raises:
            AttributeError: If the field_name does not exist on the model.
        """
        column = getattr(self.model, field_name)
        result = await self.session.execute(
            select(self.model)
            .where(column == value)
            .order_by(self.model.id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> T:
        """
        Create a new record from a dictionary of field values.

        Args:
            data: Dictionary mapping column names to values for the new record.

        Returns:
            The newly created model instance with generated fields populated.
        """
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def create_instance(self, instance: T) -> T:
        """
        Persist an already-constructed model instance.

        Args:
            instance: A SQLAlchemy model instance to add to the session.

        Returns:
            The persisted model instance with generated fields populated.
        """
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update_by_id(self, record_id: int, data: dict[str, Any]) -> Optional[T]:
        """
        Update a record by its primary key ID with the given field values.

        Args:
            record_id: The integer primary key of the record to update.
            data: Dictionary mapping column names to updated values.
                  Only provided fields are updated; others remain unchanged.

        Returns:
            The updated model instance if found, None otherwise.
        """
        if not data:
            return await self.get_by_id(record_id)

        await self.session.execute(
            update(self.model)
            .where(self.model.id == record_id)
            .values(**data)
        )
        await self.session.flush()
        return await self.get_by_id(record_id)

    async def delete_by_id(self, record_id: int) -> bool:
        """
        Delete a record by its primary key ID.

        Args:
            record_id: The integer primary key of the record to delete.

        Returns:
            True if a record was deleted, False if no record was found.
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id == record_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def count(self) -> int:
        """
        Count total number of records in the table.

        Returns:
            Integer count of all records.
        """
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0

    async def count_by_field(self, field_name: str, value: Any) -> int:
        """
        Count records matching a specific field value.

        Args:
            field_name: Name of the model column to filter on.
            value: The value to match against.

        Returns:
            Integer count of matching records.

        Raises:
            AttributeError: If the field_name does not exist on the model.
        """
        column = getattr(self.model, field_name)
        result = await self.session.execute(
            select(func.count()).select_from(self.model).where(column == value)
        )
        return result.scalar() or 0

    async def exists(self, record_id: int) -> bool:
        """
        Check if a record with the given ID exists.

        Args:
            record_id: The integer primary key to check.

        Returns:
            True if the record exists, False otherwise.
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.id == record_id)
        )
        count = result.scalar() or 0
        return count > 0

    async def commit(self) -> None:
        """
        Commit the current transaction.

        Use sparingly — prefer letting the dependency injection layer
        manage transaction boundaries via session lifecycle.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Roll back the current transaction.
        """
        await self.session.rollback()
