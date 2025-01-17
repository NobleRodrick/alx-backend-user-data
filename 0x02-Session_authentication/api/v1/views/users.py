#!/usr/bin/env python3
"""
Module of Users views.
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User


@app_views.route('/users', methods=['GET'], strict_slashes=False)
def view_all_users() -> str:
    """
    GET /api/v1/users
    Return:
      - list of all User objects JSON represented.
    """
    all_users = [user.to_json() for user in User.all()]
    return jsonify(all_users)


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def view_one_user(user_id: str = None) -> str:
    """
    GET /api/v1/users/:id
    Path parameter:
      - User ID.
    Return:
      - User object JSON represented.
      - 404 if the User ID doesn't exist.
    """
    if user_id is None:
        abort(404)
    if user_id == 'me':
        if request.current_user is None:
            abort(404)
        else:
            return jsonify(request.current_user.to_json())
    user = User.get(user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_json())


@app_views.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def delete_user(user_id: str = None) -> str:
    """
    DELETE /api/v1/users/:id
    Path parameter:
      - User ID.
    Return:
      - empty JSON is the User has been correctly deleted.
      - 404 if the User ID doesn't exist.
    """
    if user_id is None:
        abort(404)
    user = User.get(user_id)
    if user is None:
        abort(404)
    user.remove()
    return jsonify({}), 200


@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user() -> str:
    """
    POST /api/v1/users/
    JSON body:
      - email.
      - password.
      - last_name (optional).
      - first_name (optional).
    Return:
      - User object JSON represented.
      - 400 if can't create the new User.
    """
    user_data = None
    the_error_message = None
    try:
        user_data = request.get_json()
    except Exception as e:
        user_data = None
    if user_data is None:
        the_error_message = "Wrong format"
    if the_error_message is None and user_data.get("email", "") == "":
        the_error_message = "email missing"
    if the_error_message is None and user_data.get("password", "") == "":
        the_error_message = "password missing"
    if the_error_message is None:
        try:
            user = User()
            user.email = user_data.get("email")
            user.password = user_data.get("password")
            user.first_name = user_data.get("first_name")
            user.last_name = user_data.get("last_name")
            user.save()
            return jsonify(user.to_json()), 201
        except Exception as e:
            the_error_message = "Can't create User: {}".format(e)
    return jsonify({'error': the_error_message}), 400


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def update_user(user_id: str = None) -> str:
    """
    PUT /api/v1/users/:id
    Path parameter:
      - User ID.
    JSON body:
      - last_name (optional).
      - first_name (optional).
    Return:
      - User object JSON represented.
      - 404 if the User ID doesn't exist.
      - 400 if can't update the User.
    """
    if user_id is None:
        abort(404)
    user = User.get(user_id)
    if user is None:
        abort(404)
    user_data = None
    try:
        user_data = request.get_json()
    except Exception as e:
        user_data = None
    if user_data is None:
        return jsonify({'error': "Wrong format"}), 400
    if user_data.get('first_name') is not None:
        user.first_name = user_data.get('first_name')
    if user_data.get('last_name') is not None:
        user.last_name = user_data.get('last_name')
    user.save()
    return jsonify(user.to_json()), 200
