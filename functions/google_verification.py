import logging

from googleapiclient.discovery import build
from subscriptions import (
    update_subscription_status,
    Subscription,
    SubscriptionHistoryEntry,
)

sub_duration = {
    "product_id_example" : 2629800000 # one month
}

def handle_purchase(data: dict, event_time: int , credentials, subscriptions_reference):
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

            print(google_result)
            if google_result.get("purchaseState") == 0:
                update_subscription_status(
                    [
                        convert_google_play_response_to_subscription(
                            data.get("purchaseToken"), action_title, description, event_time, data.get("subscriptionId")
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
            f"Subscription started for product {subscription_id} with purchase token {purchase_token}.",
        )
    elif notification_type in [1, 2]:
        return (
            True,
            "Product Renewed",
            f"Subscription renewed for product {subscription_id} with original purchase token {purchase_token}.",
        )

    return False, None, None


def convert_google_play_response_to_subscription(
    purchase_token: str, action_title: str, history_description: str, event_time: int, subscription_id: str
) -> Subscription:
    expire_date = event_time + sub_duration[subscription_id]

    history_entry = SubscriptionHistoryEntry(
        created_at=event_time,
        action_title=action_title,
        description=history_description,
    )

    return Subscription(
        product_id=subscription_id,
        purchase_id=purchase_token,
        start_date=event_time,
        expire_date=expire_date,
        history=[history_entry],
    )
