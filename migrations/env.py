import asyncio
from logging.config import fileConfig
from alembic import context

from sqlalchemy.ext.asyncio import create_async_engine

from app.database.base import Base
from app.core.config import settings

from app.models.user import User  # noqa
from app.models.friendship import Friendship  # noqa
from app.models.conversation import Conversation  # noqa
from app.models.message import Message  # noqa
from app.models.unread import ConversationUnread  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # needed for SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,  # Needed for SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    url = settings.database_url

    connectable = create_async_engine(url, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


main()
