import json
from datetime import datetime
from pathlib import Path

from filelock import FileLock

from schemas.hf import OrganizationStatistics, ModelStatistics, Statistics


def _today_key():
    return datetime.now().strftime("%Y-%m-%d")


DATABASE_FILE = "/home/jonna/src/huggingface-slack-app/database.json"  # os.environ.get("SLACK_HF_DATABASE")


class SubscriptionStore:
    def __init__(self):
        self.database_file = Path(DATABASE_FILE)
        self.lock = FileLock(str(self.database_file) + ".lock")

    def _load(self) -> dict:
        if not self.database_file.exists():
            return {}

        with open(self.database_file, "r") as f:
            return json.load(f)

    def _save(self, database: dict) -> None:
        with open(self.database_file, "w") as f:
            json.dump(database, f, indent=4)

    def save_statistics(self, channel_id: str, stats: Statistics) -> None:
        repo_id = stats.repo_id
        with self.lock:
            database = self._load()
            database.setdefault(channel_id, {})
            database[channel_id].setdefault(repo_id, {})
            database[channel_id][repo_id] = stats.to_dict()
            self._save(database)

    def unsubscribe(self, channel_id: str, repo_id: str) -> None:
        with self.lock:
            database = self._load()

            if channel_id in database:
                database[channel_id].pop(repo_id, None)
                if not database[channel_id]:
                    database.pop(channel_id)

            self._save(database)

    def get_subscriptions(self) -> dict[str, list[str]]:
        database = self._load()
        return {
            channel_id: list(sorted(database[channel_id].keys()))
            for channel_id in database.keys()
        }

    def get_statistics(self, channel_id: str, repo_id: str) -> Statistics:
        with self.lock:
            database = self._load()
            stats = database.get(channel_id, {}).get(repo_id, {})

            if "/" in repo_id:
                return ModelStatistics.from_dict(stats)
            else:
                return OrganizationStatistics.from_dict(stats)
