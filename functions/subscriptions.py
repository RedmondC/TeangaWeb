import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_services.json"

db = firestore.Client()
subscriptions_reference = db.collection("subscriptions")


@dataclass
class SubscriptionHistoryEntry:
    createdAt: int
    actionTitle: str
    description: str


@dataclass
class Subscription:
    productId: str
    purchaseId: str
    startDate: int
    isActive: bool
    history: List[SubscriptionHistoryEntry]

    def update(self, new_sub: "Subscription") -> "Subscription":
        self.isActive = new_sub.isActive
        self.startDate = new_sub.startDate
        self.history.extend(new_sub.history)
        return self


@dataclass
class UserSubscriptions:
    subscriptions: List[Subscription] = field(default_factory=list)


def get_subscription_status(transaction_ids: List[str]) -> UserSubscriptions:
    subscriptions = []
    for tx_id in transaction_ids:
        doc = subscriptions_reference.document(tx_id).get()
        if doc.exists:
            data = doc.to_dict()
            subscription = Subscription(
                productId=data["productId"],
                purchaseId=data["purchaseId"],
                startDate=data["startDate"],
                isActive=data["isActive"],
                history=[
                    SubscriptionHistoryEntry(**entry) for entry in data["history"]
                ],
            )
            subscriptions.append(subscription)
    return UserSubscriptions(subscriptions=subscriptions)


def write_subscriptions_to_db(user_subscriptions: UserSubscriptions):
    for subscription in user_subscriptions.subscriptions:
        doc_data = {
            "productId": subscription.productId,
            "purchaseId": subscription.purchaseId,
            "startDate": subscription.startDate,
            "isActive": subscription.isActive,
            "history": [entry.__dict__ for entry in subscription.history],
        }
        subscriptions_reference.document(subscription.purchaseId).set(doc_data)


def update_subscription_status(
    new_subscriptions: List[Subscription],
) -> UserSubscriptions:
    user_subs = get_subscription_status(
        list(map(get_transaction_id, new_subscriptions))
    )
    merged = merge_subscriptions(
        user_subs.subscriptions,
        new_subscriptions,
    )
    user_subs.subscriptions = merged
    write_subscriptions_to_db(user_subs)
    return user_subs


def get_transaction_id(sub: Subscription) -> str:
    return sub.purchaseId


def merge_subscriptions(
    current: List[Subscription], new_subs: List[Subscription]
) -> List[Subscription]:
    merged = current[:]
    for new_sub in new_subs:
        existing = next(
            (sub for sub in merged if sub.productId == new_sub.productId), None
        )
        if existing:
            idx = merged.index(existing)
            merged[idx] = existing.update(new_sub)
        else:
            merged.append(new_sub)
    return merged
