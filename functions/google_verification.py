import logging

from googleapiclient.discovery import build
from subscriptions import (
    update_subscription_status,
    Subscription,
    SubscriptionHistoryEntry,
)


def handle_purchase(data: dict, credentials, subscriptions_reference):
    is_purchase, action_title, description = parse_notification(data)
    if is_purchase:
        with build("androidpublisher", "v3", credentials=credentials) as service:
            google_result = (
                service.purchases()
                .subscriptions()
                .get(
                    packageName="com.teanga",
                    subscriptionId=data.get("subscriptionId"),
                    token=data.get("purchaseToken"),
                )
                .execute()
            )

            if google_result is not None:
                update_subscription_status(
                    [
                        convert_google_play_response_to_subscription(
                            google_result, action_title, description
                        )
                    ],
                    subscriptions_reference,
                )
                service.purchases().subscriptions().acknowledge(
                    packageName="com.teanga",
                    subscriptionId=data.get("subscriptionId"),
                    token=data.get("purchaseToken"),
                    body={},
                ).execute()
            else:
                logging.error(
                    f"Failed to verify purchase id {data["subscriptionId"]} with token {data.get("purchaseToken")}."
                )


def parse_notification(data: dict) -> (bool, str, str):
    notification_type = data.get("notificationType")
    subscription_id = data.get("subscriptionId")
    purchase_token = data.get("purchaseToken")

    if notification_type in [4, 7]:
        return (
            True,
            "Product Purchased",
            f"Subscription started for product {subscription_id} with order ID {purchase_token}.",
        )
    elif notification_type in [1, 2]:
        return (
            True,
            "Product Renewed",
            f"Subscription renewed for product {subscription_id} with order ID {purchase_token}.",
        )

    return False, None, None


def convert_google_play_response_to_subscription(
    data: dict, action_title: str, history_description: str
) -> Subscription:
    start_date = int(data.get("startTimeMillis", 0))
    expire_date = int(data.get("expiryTimeMillis", 0))
    purchase_token = data.get("purchaseToken")
    subscription_id = data.get("subscriptionId")
    print(f"converting response: ${data}")

    history_entry = SubscriptionHistoryEntry(
        created_at=start_date,
        action_title=action_title,
        description=history_description,
    )

    return Subscription(
        product_id=subscription_id,
        purchase_id=purchase_token,
        start_date=start_date,
        expire_date=expire_date,
        history=[history_entry],
    )
