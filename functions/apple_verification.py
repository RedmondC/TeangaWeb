import logging

from flask import jsonify
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.signed_data_verifier import (
    VerificationException,
    SignedDataVerifier,
)
from subscriptions import (
    Subscription,
    SubscriptionHistoryEntry,
    update_subscription_status,
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
    payload, status = parse_payload(notification)
    if status == 200:
        handle_subscription_event(payload)


def parse_payload(signed_payload: str):
    try:
        payload = signed_data_verifier.verify_and_decode_notification(
            signed_payload=signed_payload
        )
        logging.info("Verified Apple Notification:\n%s", payload)
        return payload, 200
    except VerificationException as e:
        logging.exception(
            "Failed to verify notification, possible fraud attempt: %s", e
        )
        return jsonify({"error": "internal server error"}), 500


def handle_subscription_event(decoded_data):
    is_purchase, action_title, description = parse_notification(decoded_data)
    if is_purchase:
        update_subscription_status(
            [
                convert_apple_notification_to_subscription(
                    decoded_data, action_title, description
                )
            ]
        )


def parse_notification(data: dict) -> (bool, str, str, str, int, int):
    notification_type = data.get("notificationType")
    subscription_id = data.get("renewalInfo").get("productId")
    transaction_id = data.get("renewalInfo").get("transactionId")

    if notification_type in ["SUBSCRIBED"]:
        return (
            True,
            "Product Purchased",
            f"Subscription started for product {subscription_id} with order ID {transaction_id}.",
        )
    elif notification_type in ["DID_RENEW"]:
        return (
            True,
            "Product Renewed",
            f"Subscription renewed for product {subscription_id} with order ID {transaction_id}.",
        )
    elif notification_type in ["RENEWAL_EXTENDED", "REFUND_REVERSED"]:
        return (
            True,
            "Special action",
            f"The special action {notification_type} has been performed for product {subscription_id} with order ID {transaction_id}.",
        )

    return False, None, None


def convert_apple_notification_to_subscription(
    decoded_data: dict, action_title: str, history_description: str
) -> Subscription:
    data = decoded_data.get("data")
    transaction = data.get("transactionInfo", {})
    renewal_info = data.get("renewalInfo", {})

    product_id = renewal_info.get("subscriptionId")
    purchase_id = transaction.get("transactionId")
    start_date = int(transaction.get("purchaseDate", 0))
    expires_date = int(transaction.get("expiresDate", 0))

    history_entry = SubscriptionHistoryEntry(
        created_at=start_date,
        action_title=action_title,
        description=history_description,
    )

    if renewal_info:
        purchase_id = renewal_info.get("originalTransactionId")
        expires_date = renewal_info.get("gracePeriodExpiresDate")
        start_date = renewal_info.get("recentSubscriptionStartDate")

    return Subscription(
        product_id=product_id,
        purchase_id=purchase_id,
        start_date=start_date,
        expire_date=expires_date,
        history=[history_entry],
    )
