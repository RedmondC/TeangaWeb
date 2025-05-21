import logging
import os

from appstoreserverlibrary.api_client import AppStoreServerAPIClient, APIException
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.signed_data_verifier import VerificationException
from apple_verification import apple_notifications
from google_verification import handle_purchase
from googleapiclient.errors import HttpError
from index_page import render_index
from flask import Flask, request

print("Starting Flask app...")

# Check if secrets are available
print("google_services is set:", bool(os.environ.get("google_services")))
print("subscriptions_private_key is set:", bool(os.environ.get("subscriptions_private_key")))


app = Flask(__name__, static_url_path="/static", static_folder="static")
app.logger.setLevel(logging.INFO)

print("Flask app created")

@app.route("/google-validate-purchases", methods=["POST"])
def verify_google():
    data = request.get_json()
    try:
        handle_purchase(data.get("subscriptionNotification"))
    except HttpError:
        logging.error(f"Google - A http error occurred for request: {data}")
        return "An error occurred.", 400
    except Exception as e:
        logging.error(f"Google - An unexpected error occurred for request: {data}")
        logging.error(e)
        return "An unexpected error occurred.", 500

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
    except VerificationException:
        logging.exception("Failed to handle Apple notification: ", data)
        return "An error occurred", 400
    except Exception:
        logging.error("Apple - An unexpected error occurred for notification: ", data)
        return "An unexpected error occurred.", 500


@app.route("/")
def main():
    return render_index()
