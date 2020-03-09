import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
@app.route('/api/users/')
def get_users():
    return success_response(DB.get_all_users())

@app.route('/api/users/', methods=['POST'])
def create_user():
    body = json.loads(request.data)
    name = body["name"]
    username = body["username"]
    balance = 0 if body.get("balance") is None else body["balance"]
    user_id = DB.insert_users_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is not None:
        return success_response(user, 201)
    return failure_response("Something went wrong while creating user!")

@app.route('/api/user/<int:user_id>/')
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is not None:
        return success_response(user, 201)
    return failure_response("User not found!")

@app.route('/api/user/<int:user_id>/', methods=['DELETE'])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is not None:
        DB.delete_user_by_id(user_id)
        return success_response(user)
    return failure_response("User not found!")

@app.route('/api/send/', methods=['POST'])
def transfer_balance():
    body = json.loads(request.data)
    sender_id = body["sender_id"]
    receiver_id = body["receiver_id"]
    amount = body["amount"]
    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if (sender is not None and receiver is not None):
        sender_balance = sender["balance"] - amount
        if sender_balance < 0:
            return failure_response("Not enough money in sender!")
        receiver_balance = sender["balance"] + amount
        DB.update_user_by_id(sender_id, sender_balance)
        DB.update_user_by_id(receiver_id, receiver_balance)
        return success_response(body)
    return failure_response("Users not found!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
