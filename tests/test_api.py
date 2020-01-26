import os
import tempfile
import pytest
import app


@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True

    with app.app.test_client() as client:
        with app.app.app_context():
            # Some app initialization here
            print('Init app...')
        yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])


def test_index(client):
    """Testing index route"""

    rv = client.get('/')

    print(rv)
