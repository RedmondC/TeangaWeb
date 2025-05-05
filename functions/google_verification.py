from googleapiclient.discovery import build
from google.oauth2 import service_account
from subscriptions import update_subscription_status, Subscription, SubscriptionHistoryEntry


def handle_purchase(data: dict):
    credentials = service_account.Credentials.from_service_account_file(
        "google_services.json"
    )

    with build("androidpublisher", "v3", credentials=credentials) as service:
        for purchase in data["purchases"]:
            result = service.purchases()
            result = (
                result.subscriptions()
                .get(
                    packageName="com.teanga",
                    subscriptionId=purchase["productId"],
                    token=purchase["token"],
                )
                .execute()
            )

            if result is not None:
                write_to_db(result)


def write_to_db(data: dict):
    update_subscription_status(list(map(convert_google_play_response_to_subscription, data)))

def convert_google_play_response_to_subscription(data: dict) -> Subscription:
    start_time = int(data.get("startTimeMillis", 0))
    purchase_id = data.get("orderId", "")
    product_id = data.get("developerPayload")
    if product_id == "":
        product_id = "product_id_example"
    is_active = data.get("autoRenewing", False) and data.get("cancelReason", 0) == 0

    history_entry = SubscriptionHistoryEntry(
        createdAt=start_time,
        actionTitle="Product Purchased",
        description=f"Subscription started for product {product_id} with order ID {purchase_id}.",
    )

    return Subscription(
        productId=product_id,
        purchaseId=purchase_id,
        startDate=start_time,
        isActive=is_active,
        history=[history_entry],
    )