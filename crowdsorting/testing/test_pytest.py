import os
import tempfile

import pytest

import crowdsorting


@pytest.fixture
def client():
    crowdsorting.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing/_ignoreMe_crowdsorting.db'
    crowdsorting.app.config[
        'PAIRS_BEING_PROCESSED_PATH'] = 'testing/_ignoreMe_pairsbeingprocessed.pkl'
    crowdsorting.app.config['TESTING'] = True

    with crowdsorting.app.test_client() as client:
        with crowdsorting.app.app_context():
            crowdsorting.db.drop_all()
            crowdsorting.db.create_all()
        yield client

def test_vanilla(client):
    assert True


