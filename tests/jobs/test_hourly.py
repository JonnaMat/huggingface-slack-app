from unittest.mock import Mock

from jobs.hourly import organization_updates, model_updates, check_for_updates
from tests.utils import (
    ADDED_MODEL,
    OLD_ORG,
    OLD_MODEL,
    NEW_MODEL,
    NEW_ORG,
    make_fake_app,
)


def test_organization_updates():
    fake_hf = Mock()
    fake_hf.get_new_models.return_value = [ADDED_MODEL]

    message = organization_updates(fake_hf, "org-x", OLD_ORG, NEW_ORG)

    assert message == (
        "*:fire::fire::fire: `org-x` :fire::fire::fire:*\n\n"
        "*👥* *1 new follower:* Bob @ nvidia\n"
        "*🛠* *1 new model:* `org-x/model-z` – 50 downloads, 4 ❤️\n"
        "*🏆* *Top Models updated*\n"
        "    1. `org-x/model-x` – 1,020 downloads, 520 ❤️\n"
        "    2. `org-x/model-y` – 980 downloads, 480 ❤️\n"
        "    3. ~`org-x/model-n`~ -> `org-x/model-z` – 50 downloads, 4 ❤️"
    )


def test_model_updates():
    message = model_updates("org-x/model-x", OLD_MODEL, NEW_MODEL)
    print(message)
    assert (
        message
        == ":tada: `org-x/model-x` crossed 1,000 downloads and 500 likes! (1,020 downloads, 520 ❤️)"
    )


def test_check_for_updates_posts(monkeypatch):

    fake_app = make_fake_app()

    fake_store = Mock()
    fake_store._load.return_value = {
        "C123": {
            "org-x": OLD_ORG,
            "org-x/model-x": OLD_MODEL,
        }
    }
    fake_store.get_subscriptions.return_value = {
        "org-x": OLD_ORG,
        "org-x/model-x": OLD_MODEL,
    }

    fake_hf = Mock()
    fake_hf.get_model_statistics.return_value = NEW_MODEL
    fake_hf.get_organization_statistics.return_value = NEW_ORG
    fake_hf.get_new_models.return_value = [ADDED_MODEL]

    monkeypatch.setattr("jobs.hourly.SubscriptionStore", lambda: fake_store)
    monkeypatch.setattr("jobs.hourly.HFService", lambda: fake_hf)

    check_for_updates(fake_app)

    calls = fake_app.mock_calls

    assert len(calls) == 2
    assert calls[0].kwargs["text"] == (
        "*:fire::fire::fire: `org-x` :fire::fire::fire:*\n\n"
        "*👥* *1 new follower:* Bob @ nvidia\n"
        "*🛠* *1 new model:* `org-x/model-z` – 50 downloads, 4 ❤️\n"
        "*🏆* *Top Models updated*\n"
        "    1. `org-x/model-x` – 1,020 downloads, 520 ❤️\n"
        "    2. `org-x/model-y` – 980 downloads, 480 ❤️\n"
        "    3. ~`org-x/model-n`~ -> `org-x/model-z` – 50 downloads, 4 ❤️"
    )
    assert calls[1].kwargs["text"] == (
        ":tada: `org-x/model-x` crossed 1,000 downloads and 500 likes! (1,020 downloads, 520 ❤️)"
    )
