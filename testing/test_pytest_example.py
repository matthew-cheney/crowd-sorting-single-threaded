import os
import tempfile

import pytest

import crowdsorting


@pytest.fixture
def client():
    db_fd, crowdsorting.app.config['DATABASE'] = tempfile.mkstemp()
    crowdsorting.app.config['TESTING'] = True

    with crowdsorting.app.test_client() as client:
        with crowdsorting.app.app_context():
            crowdsorting.init_db()
        yield client

    os.close(db_fd)
    os.unlink(crowdsorting.app.config['DATABASE'])