import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


def test_mna_migration_adds_missing_columns_and_preserves_existing_observations():
    path = Path(__file__).parents[1] / 'alembic/versions/20261004_07_mna_assessment_fields.py'
    spec = importlib.util.spec_from_file_location('mna_migration', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    engine = create_engine('sqlite://')
    with engine.begin() as connection:
        connection.execute(text('CREATE TABLE mna_responses (id INTEGER PRIMARY KEY, mna_total NUMERIC, mna_a12 NUMERIC)'))
        connection.execute(text('INSERT INTO mna_responses VALUES (1, 23, 0)'))
        module.op = Operations(MigrationContext.configure(connection))
        module.upgrade()
        module.upgrade()
        names = {column['name'] for column in inspect(connection).get_columns('mna_responses')}
        assert {'q19_calf_circumference_assess', 'mna_a12', 'mac_cm', 'cc_cm'} <= names
        assert connection.execute(text('SELECT mna_total, mna_a12, cc_cm FROM mna_responses')).one() == (23, 0, None)
        module.downgrade()
        assert connection.execute(text('SELECT mna_total, mna_a12 FROM mna_responses')).one() == (23, 0)
    engine.dispose()
