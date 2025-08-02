
# Standard library imports
import importlib
import os
import pkgutil
import sys
from logging.config import fileConfig

# Third-party imports
from sqlalchemy import engine_from_config, pool

from alembic import context

# Local application imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import settings
from app.core.database import Base

# Dynamically import all model modules in app.models
models_pkg = 'app.models'
package = importlib.import_module(models_pkg)
for _, module_name, _ in pkgutil.iter_modules(package.__path__):
    importlib.import_module(f"{models_pkg}.{module_name}")

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Set SQLAlchemy URL from settings
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
