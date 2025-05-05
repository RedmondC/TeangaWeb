import logging

from appstoreserverlibrary.api_client import AppStoreServerAPIClient, APIException
from appstoreserverlibrary.models.Environment import Environment
from flask import Flask, request
from future.backports.urllib.error import HTTPError

from apple_verification import apple_notifications
from google_verification import handle_purchase
from index_page import render_index

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.logger.setLevel(logging.INFO)


def read_private_key(path_to_p8_file):
    with open(path_to_p8_file, "rb") as key_file:
        private_key = key_file.read()
    return private_key


@app.route("/google-validate-purchases", methods=["POST"])
def verify_google():
    data = request.get_json()
    try:
        handle_purchase(data)
    except HTTPError as e:
        logging.error("Google - A http error occurred: ", e)
        return "An error occurred", e.response.status_code
    except Exception as e:
        logging.error("Google - An unexpected error occurred: ", e)
        return "An unexpected occurred.", 500

    return "Success", 200


@app.route("/user-update-apple", methods=["POST"])
def verify_apple():
    data = request.get_json()
    signed_payload = data.get("signedPayload")
    try:
        if not signed_payload:
            logging.info("No JSON signed payload received in request %s", data)
            return "Invalid JSON", 400
        else:
            apple_notifications(signed_payload)
    except HTTPError as e:
        logging.error("Apple - A http error occurred: ", e)
        return "An error occurred", e.response.status_code
    except Exception as e:
        logging.error("Apple - An unexpected error occurred: ", e)
        return "An unexpected occurred.", 500


@app.route("/")
def main():
    return render_index()
