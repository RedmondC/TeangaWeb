from dataclasses import dataclass, field
from typing import List


@dataclass
class SubscriptionHistoryEntry:
    created_at: int
    action_title: str
    description: str


@dataclass
class Subscription:
    product_id: str
    purchase_id: str
    start_date: int
    expire_date: int
    history: List[SubscriptionHistoryEntry]

    def update(self, new_sub: "Subscription") -> "Subscription":
        self.start_date = new_sub.start_date
        self.expire_date = new_sub.expire_date
        self.history.extend(new_sub.history)
        return self


@dataclass
class UserSubscriptions:
    subscriptions: List[Subscription] = field(default_factory=list)


def update_subscription_status(
    new_subscriptions: List[Subscription], subscriptions_reference
):
    user_subs = _get_subscription_status(
        new_subscriptions,
        subscriptions_reference=subscriptions_reference,
    )

    merged = _merge_subscriptions(
        user_subs.subscriptions,
        new_subscriptions,
    )

    user_subs.subscriptions = merged
    _write_subscriptions_to_db(
        user_subs, subscriptions_reference=subscriptions_reference
    )


def _get_subscription_status(
    new_subscriptions: List[Subscription], subscriptions_reference
) -> UserSubscriptions:
    subscriptions = []
    for sub in new_subscriptions:
        doc = subscriptions_reference.document(sub.purchase_id).get()
        if doc.exists:
            data = doc.to_dict()
            subscription = Subscription(
                product_id=data["productId"],
                purchase_id=data["purchaseId"],
                start_date=data["startDate"],
                expire_date=data["expireDate"],
                history=[
                    SubscriptionHistoryEntry(**entry) for entry in data["history"]
                ],
            )
            subscriptions.append(subscription)
    return UserSubscriptions(subscriptions=subscriptions)


def _write_subscriptions_to_db(
    user_subscriptions: UserSubscriptions, subscriptions_reference
):
    for subscription in user_subscriptions.subscriptions:
        doc_data = {
            "productId": subscription.product_id,
            "purchaseId": subscription.purchase_id,
            "startDate": subscription.start_date,
            "expireDate": subscription.expire_date,
            "history": [entry.__dict__ for entry in subscription.history],
        }
        subscriptions_reference.document(subscription.purchase_id).set(doc_data)


def _get_transaction_id(sub: Subscription) -> str:
    return sub.purchase_id


def _merge_subscriptions(
    current: List[Subscription], new_subs: List[Subscription]
) -> List[Subscription]:
    merged = current[:]
    for new_sub in new_subs:
        existing = next(
            (sub for sub in merged if sub.product_id == new_sub.product_id), None
        )
        if existing:
            idx = merged.index(existing)
            merged[idx] = existing.update(new_sub)
        else:
            merged.append(new_sub)
    return merged
