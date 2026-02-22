import logging
from unittest.mock import Mock

from schemas.hf import OrganizationStatistics, ModelStatistics, User
from jobs.hourly import organization_updates, model_updates, check_for_updates

logger = logging.getLogger(__name__)

OLD_MODEL = ModelStatistics(repo_id="org-x/model-x", downloads=980, likes=480)

NEW_MODEL = ModelStatistics(repo_id="org-x/model-x", downloads=1020, likes=520)

ADDED_MODEL = ModelStatistics(repo_id="org-x/model-z", downloads=50, likes=4)

OLD_ORG = OrganizationStatistics(
    repo_id="org-x",
    followers=[User(username="alice", fullname="Alice")],
    num_followers=1,
    num_models=3,
    top_three_models=[
        OLD_MODEL,
        ModelStatistics(repo_id="org-x/model-y", downloads=980, likes=480),
        ModelStatistics(repo_id="org-x/model-n", downloads=9, likes=1),
    ],
)

NEW_ORG = OrganizationStatistics(
    repo_id="org-x",
    followers=[
        User(username="alice", fullname="Alice"),
        User(username="bob", fullname="Bob", organizations=["nvidia"]),
    ],
    num_followers=2,
    num_models=4,
    top_three_models=[
        NEW_MODEL,
        ModelStatistics(repo_id="org-x/model-y", downloads=980, likes=480),
        ADDED_MODEL,
    ],
)


def make_fake_app():
    """Return a reusable fake Slack app."""
    app = Mock()
    app.client.chat_postMessage = Mock()
    return app
