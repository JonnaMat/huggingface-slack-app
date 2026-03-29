import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from persistence.subscription_store import (
    SubscriptionStore,
    WeeklyStatsStore,
)
from schemas.hf import OrganizationStatistics
from schemas.icons import DOWNLOAD_ICON, FOLLOWER_ICON, MODELS_ICON


def get_week_number() -> str:
    return datetime.now().strftime("Week %W, %b %d")


def generate_digest(app):
    store = SubscriptionStore()
    weekly_store = WeeklyStatsStore()

    subscriptions = store.get_all_subscriptions_with_stats()
    org_digests = {}

    for channel_id, repos in subscriptions.items():
        for repo_id, old_stats in repos.items():
            try:
                if isinstance(old_stats, OrganizationStatistics):
                    weekly_downloads = weekly_store.get_org_weekly_downloads(repo_id)
                    added_followers = weekly_store.get_weekly_followers(repo_id)
                    released_models = weekly_store.get_weekly_models(repo_id)

                    if repo_id not in org_digests:
                        org_digests[repo_id] = {
                            "channel_id": channel_id,
                            "weekly_downloads": weekly_downloads,
                            "added_followers": added_followers,
                            "released_models": released_models,
                        }
                    else:
                        org_digests[repo_id]["weekly_downloads"] += weekly_downloads
                        org_digests[repo_id]["added_followers"] += added_followers
                        org_digests[repo_id]["released_models"] += released_models
            except Exception as e:
                logging.error(f"Failed to process digest for {repo_id}: {e}")
                continue

    for repo_id, data in org_digests.items():
        message = f"*Weekly Digest for* `{repo_id}` ({get_week_number()})\n\n"
        message += f"{DOWNLOAD_ICON} Downloads this week: {data['weekly_downloads']:,}\n"
        message += f"{FOLLOWER_ICON} New Followers: +{data['added_followers']:,}\n"
        message += f"{MODELS_ICON} New Models: +{data['released_models']:,}"
        app.client.chat_postMessage(channel=data["channel_id"], text=message)


def start_weekly_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: generate_digest(app),
        trigger="cron",
        day_of_week="fri",
        hour=9,
        minute=0,
    )
    scheduler.start()
    return scheduler
