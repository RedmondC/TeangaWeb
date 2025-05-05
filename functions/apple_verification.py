from flask import jsonify
import logging
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.signed_data_verifier import (
    VerificationException,
    SignedDataVerifier,
)


def read_root_certs(path_to_file):
    with open(path_to_file, "rb") as key_file:
        cert = key_file.read()
    return cert


root_certificates = read_root_certs("AppleIncRootCertificate.cer")
enable_online_checks = True
bundle_id = "com.teanga"
environment = Environment.SANDBOX
app_apple_id = None
signed_data_verifier = SignedDataVerifier(
    root_certificates, enable_online_checks, environment, bundle_id, app_apple_id
)


def apple_notifications(notification: str):
    payload, _ = parse_payload(notification)
    print("Received ", payload)


def parse_payload(signed_payload: str):
    try:
        payload = signed_data_verifier.verify_and_decode_notification(
            signed_payload=signed_payload
        )
        logging.info("✅ Verified Apple Notification:\n%s", payload)
        return payload, 200
    except VerificationException as e:
        logging.exception(
            "Failed to verify notification, possible fraud attempt: %s", e
        )
        return jsonify({"error": "internal server error"}), 500
