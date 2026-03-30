import json
from datetime import datetime, timedelta
from pathlib import Path

from filelock import FileLock

from schemas.hf import OrganizationStatistics, ModelStatistics, Statistics


def _today_key():
    return datetime.now().strftime("%Y-%m-%d")


def _week_key():
    return (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-W%W")


_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_DIR.mkdir(exist_ok=True)
DATABASE_FILE = _DATA_DIR / "database.json"
WEEKLY_STATS_FILE = _DATA_DIR / "weekly_stats.json"


class SubscriptionStore:
    def __init__(self):
        self.database_file = Path(DATABASE_FILE)
        self.lock = FileLock(str(self.database_file) + ".lock")
        if not self.database_file.exists():
            self._save({})

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
        return {channel_id: list(sorted(database[channel_id].keys())) for channel_id in database.keys()}

    def get_statistics(self, channel_id: str, repo_id: str) -> Statistics:
        with self.lock:
            database = self._load()
            stats = database.get(channel_id, {}).get(repo_id, {})

            if "/" in repo_id:
                return ModelStatistics.from_dict(stats)
            else:
                return OrganizationStatistics.from_dict(stats)

    def get_all_subscriptions_with_stats(self) -> dict[str, dict[str, Statistics]]:
        with self.lock:
            database = self._load()
            result = {}
            for channel_id, repos in database.items():
                result[channel_id] = {}
                for repo_id, stats in repos.items():
                    if "/" in repo_id:
                        result[channel_id][repo_id] = ModelStatistics.from_dict(stats)
                    else:
                        result[channel_id][repo_id] = OrganizationStatistics.from_dict(stats)
            return result


class WeeklyStatsStore:
    def __init__(self):
        self.database_file = Path(WEEKLY_STATS_FILE)
        self.lock = FileLock(str(self.database_file) + ".lock")
        if not self.database_file.exists():
            self._save({})

    def _load(self) -> dict:
        if not self.database_file.exists():
            return {}
        with open(self.database_file, "r") as f:
            return json.load(f)

    def _save(self, database: dict) -> None:
        with open(self.database_file, "w") as f:
            json.dump(database, f, indent=4)

    def record_downloads(self, repo_id: str, downloads: int) -> None:
        today = _today_key()
        with self.lock:
            database = self._load()
            database.setdefault(repo_id, {})
            database[repo_id].setdefault("downloads", {})
            if database[repo_id]["downloads"].get(today) == downloads:
                return
            database[repo_id]["downloads"][today] = downloads
            self._save(database)

    def record_followers(self, repo_id: str, followers: int) -> None:
        today = _today_key()
        with self.lock:
            database = self._load()
            database.setdefault(repo_id, {})
            database[repo_id].setdefault("followers", {})
            if database[repo_id]["followers"].get(today) == followers:
                return
            database[repo_id]["followers"][today] = followers
            self._save(database)

    def record_models(self, repo_id: str, models: int) -> None:
        today = _today_key()
        with self.lock:
            database = self._load()
            database.setdefault(repo_id, {})
            database[repo_id].setdefault("models", {})
            if database[repo_id]["models"].get(today) == models:
                return
            database[repo_id]["models"][today] = models
            self._save(database)

    def _get_daily_deltas(self, repo_id: str, stat_type: str, database: dict) -> list[tuple[str, int]]:
        repo_data = database.get(repo_id, {}).get(stat_type, {})
        if not repo_data:
            return []

        sorted_dates = sorted(repo_data.keys())
        deltas = []

        for i in range(1, len(sorted_dates)):
            prev_date = sorted_dates[i - 1]
            curr_date = sorted_dates[i]
            delta = repo_data[curr_date] - repo_data[prev_date]
            deltas.append((curr_date, delta))

        return deltas

    def _get_weekly_delta(self, repo_id: str, stat_type: str) -> int:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())

        with self.lock:
            database = self._load()
            deltas = self._get_daily_deltas(repo_id, stat_type, database)

            total = 0
            for date_str, delta in deltas:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                if date >= week_start:
                    total += delta

            return total

    def get_weekly_downloads(self, repo_id: str) -> int:
        return self._get_weekly_delta(repo_id, "downloads")

    def get_org_weekly_downloads(self, repo_id: str) -> int:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())

        with self.lock:
            database = self._load()

        total = 0
        for key in database.keys():
            if key.startswith(repo_id + "/") or key == repo_id:
                deltas = self._get_daily_deltas(key, "downloads", database)
                for date_str, delta in deltas:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    if date >= week_start:
                        total += max(0, delta)

        return total

    def get_weekly_followers(self, repo_id: str) -> int:
        return self._get_weekly_delta(repo_id, "followers")

    def get_weekly_models(self, repo_id: str) -> int:
        return self._get_weekly_delta(repo_id, "models")
