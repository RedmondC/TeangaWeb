import logging

from googleapiclient.discovery import build
from google.oauth2 import service_account
from subscriptions import (
    update_subscription_status,
    Subscription,
    SubscriptionHistoryEntry,
)
import os
from json import loads


def handle_purchase(data: dict):
    credentials = service_account.Credentials.from_service_account_info(
        loads(os.getenv("google_services"))
    )

    with build("androidpublisher", "v3", credentials=credentials) as service:
        for purchase in data["purchases"]:
            result = (
                service.purchases()
                .subscriptions()
                .get(
                    packageName="com.teanga",
                    subscriptionId=purchase["subscriptionId"],
                    token=purchase["purchaseToken"],
                )
                .execute()
            )

            if result is not None:
                # todo check notification type
                is_purchase, action_title, description = parse_notification(result)
                if is_purchase:
                    update_subscription_status(
                        [convert_google_play_response_to_subscription(result, action_title, description)]
                    )
                    service.purchases().subscriptions().acknowledge(
                        packageName="com.teanga",
                        subscriptionId=purchase["subscriptionId"],
                        token=purchase["purchaseToken"],
                        body={},
                    ).execute()
            else:
                logging.error(f"Failed to verify purchase id {purchase["subscriptionId"]} with token {purchase["purchaseToken"]}.")

def parse_notification(result: dict) -> (bool, str, str):
    notification_type = result.get("notificationType")
    subscription_id = result.get("subscriptionId")
    purchase_token = result.get("purchaseToken")

    if notification_type in [4, 7]:
        return True, "Product Purchased", f"Subscription started for product {subscription_id} with order ID {purchase_token}."
    elif notification_type in [1, 2]:
        return True, "Product Renewed", f"Subscription renewed for product {subscription_id} with order ID {purchase_token}."

    return False, None, None

def convert_google_play_response_to_subscription(data: dict, action_title: str, history_description: str) -> Subscription:
    start_date = int(data.get("startTimeMillis", 0))
    expire_date = int(data.get("expiryTimeMillis", 0))
    purchase_id = data.get("orderId", "")
    product_id = data.get("developerPayload")
    if product_id == "":
        product_id = "product_id_example"
    is_active = data.get("autoRenewing", False) and data.get("cancelReason", 0) == 0

    history_entry = SubscriptionHistoryEntry(
        created_at=start_date,
        action_title=action_title,
        description=history_description,
    )

    return Subscription(
        product_id=product_id,
        purchase_id=purchase_id,
        start_date=start_date,
        expire_date=expire_date,
        is_active=is_active,
        history=[history_entry]
    )
