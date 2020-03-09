import unittest
import json
import requests
from app import app
from threading import Thread
from time import sleep

# NOTE: Make sure you run 'pip3 install requests' in your virtualenv

# URL pointing to your local dev host
LOCAL_URL = "http://localhost:5000"

# Sample testing data
SAMPLE_USER = {"name": "Cornell AppDev", "username": "cornellappdev"}

# Request endpoint generators
def gen_users_path(user_id=None):
    base_path = f"{LOCAL_URL}/api/user"
    return base_path + "s/" if user_id is None else f"{base_path}/{str(user_id)}/"

def gen_send_path():
    return f"{LOCAL_URL}/api/send/"

def unwrap_response(response, body={}):
    try:
        return response.json()
    except:
        req = response.request
        raise Exception(f"""
            Error encountered on the following request:

            request path: {req.url}
            request method: {req.method}
            request body: {str(body)}

            There is an uncaught-exception being thrown in your
            method handler for this route!
            """)


class TestRoutes(unittest.TestCase):

#-- USERS ---------------------------------------------

    def test_get_initial_users(self):
        res = requests.get(gen_users_path())
        body = unwrap_response(res)
        assert body["success"]

    def test_create_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user = body["data"]
        assert body["success"]
        assert user["name"] == SAMPLE_USER["name"]
        assert user["username"] == SAMPLE_USER["username"]
        assert user["balance"] == 0

    def test_get_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user = body["data"]

        res = requests.get(gen_users_path(user["id"]))
        body = unwrap_response(res)
        user = body["data"]
        assert body["success"]
        assert user.get('id') is not None
        assert user["name"] == SAMPLE_USER["name"]
        assert user["username"] == SAMPLE_USER["username"]
        assert user["balance"] == 0

    def test_delete_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user_id = body["data"]["id"]

        res = requests.delete(gen_users_path(user_id))
        body = unwrap_response(res)
        assert body["success"]

        res = requests.get(gen_users_path(user_id))
        body = unwrap_response(res)
        assert not body["success"]

    def test_send_money(self):
        user_with_balance = {**SAMPLE_USER, "balance": 10}
        res1 = requests.post(gen_users_path(), data=json.dumps(user_with_balance))
        body = unwrap_response(res1, user_with_balance)
        user_id1 = body["data"]["id"]
        bal1 = body["data"]["balance"]
        assert bal1 == 10

        res2 = requests.post(gen_users_path(), data=json.dumps(user_with_balance))
        body = unwrap_response(res2, user_with_balance)
        user_id2 = body["data"]["id"]
        bal2 = body["data"]["balance"]
        assert bal1 == 10

        send_body = {"sender_id": user_id1, "receiver_id": user_id2, "amount": 6}

        res = requests.post(gen_send_path(), data=json.dumps(send_body))
        body = unwrap_response(res, send_body)
        assert body["success"]
        # balances are now (user1: 4, user2: 16)

        res1 = requests.get(gen_users_path(user_id1))
        body1 = unwrap_response(res1)
        res2 = requests.get(gen_users_path(user_id2))
        body2 = unwrap_response(res2)
        assert body1["data"]["balance"] == 4
        assert body2["data"]["balance"] == 16

        res = requests.post(gen_send_path(), data=json.dumps(send_body))
        body = unwrap_response(res, send_body)
        assert not body["success"]  # cannot overdraw user1's balance
        # balances are still (user1: 4, user2: 16)

        res1 = requests.get(gen_users_path(user_id1))
        body1 = unwrap_response(res1)
        res2 = requests.get(gen_users_path(user_id2))
        body2 = unwrap_response(res2)
        assert body1["data"]["balance"] == 4
        assert body2["data"]["balance"] == 16


    def test_get_invalid_user(self):
        res = requests.get(gen_users_path(1000))
        body = unwrap_response(res)
        assert not body["success"]

    def test_delete_invalid_user(self):
        res = requests.delete(gen_users_path(1000))
        body = unwrap_response(res)
        assert not body["success"]

    def test_user_id_increments(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user_id1 = body["data"]["id"]

        res2 = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res2, SAMPLE_USER)
        user_id2 = body["data"]["id"]

        assert user_id1 + 1 == user_id2


def run_tests():
    sleep(1.5)
    unittest.main()


if __name__ == "__main__":
    thread = Thread(target=run_tests)
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
