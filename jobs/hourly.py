import logging
from apscheduler.schedulers.background import BackgroundScheduler

from persistence.subscription_store import SubscriptionStore
from schemas.icons import (
    TOP_3_MODELS_ICON,
    MODELS_ICON,
    FOLLOWER_ICON,
    BULLET_LIST_ICON,
)
from services.hf import HFService
from schemas.hf import OrganizationStatistics, ModelStatistics
from services.milestones import crossed_milestone


def model_updates(
    app, channel_id, old_stats: ModelStatistics, new_stats: ModelStatistics
) -> None:
    repo_id = old_stats.repo_id

    old_downloads = old_stats.downloads
    new_downloads = new_stats.downloads

    old_likes = old_stats.likes
    new_likes = new_stats.likes

    download_milestone = crossed_milestone(
        old_downloads, new_downloads, strategy="downloads"
    )
    likes_milestone = crossed_milestone(old_likes, new_likes, strategy="likes")

    message = ""

    if download_milestone and likes_milestone:
        message = (
            f":tada: `{repo_id}` crossed {download_milestone:,} downloads and {likes_milestone:,} likes! "
            f"({new_stats.stats_str()})"
        )
    elif download_milestone:
        message = f":tada: `{repo_id}` crossed {download_milestone:,} downloads! ({new_stats.stats_str()})"
    elif likes_milestone:
        message = f":heart: `{repo_id}` crossed {likes_milestone:,} likes! ({new_stats.stats_str()})"
    if message:
        app.client.chat_postMessage(channel=channel_id, text=message)


def _organization_followers_updates(
    app,
    channel_id: str,
    old_stats: OrganizationStatistics,
    new_stats: OrganizationStatistics,
) -> None:
    repo_id = old_stats.repo_id

    old_followers = old_stats.num_followers
    new_followers = new_stats.num_followers
    follower_increase = new_followers - old_followers

    if follower_increase > 0:

        added_followers = []
        if new_stats.followers and old_stats.followers:
            old_followers = {str(follower) for follower in old_stats.followers}

            for follower in new_stats.followers:
                if str(follower) not in old_followers:
                    added_followers.append(str(follower))

        message = (
            f":partying_face: `{repo_id}` gained *{follower_increase} new follower"
        )
        if follower_increase > 1:
            message += f"s*!\n{BULLET_LIST_ICON} "
            message += f"\n{BULLET_LIST_ICON} ".join(added_followers)
        else:
            message += f":* {added_followers[0]}"

        app.client.chat_postMessage(channel=channel_id, text=message)


def _organization_models_updates(
    app,
    channel_id: str,
    hf_service: HFService,
    old_stats: OrganizationStatistics,
    new_stats: OrganizationStatistics,
) -> None:
    repo_id = old_stats.repo_id

    old_num_models = old_stats.num_models
    new_num_models = new_stats.num_models

    model_count_diff = new_num_models - old_num_models

    if model_count_diff > 0:
        new_models = hf_service.get_new_models(repo_id, model_count_diff)

        message = f":tada: `{repo_id}` released *{model_count_diff} new model"
        if model_count_diff > 1:
            message += f"s*!\n{BULLET_LIST_ICON} "
            message += f"\n{BULLET_LIST_ICON} ".join(
                model.minimal_str() for model in new_models
            )
        else:
            message += f":* {new_models[0].minimal_str()}"

        if new_models:
            message += (
                "\nSubscribe to new models: ```\hf subscribe "
                + "\n\hf subscribe ".join(model.repo_id for model in new_models)
                + "\n```"
            )

        app.client.chat_postMessage(channel=channel_id, text=message)


def _organization_top_models_updates(
    app,
    channel_id: str,
    old_stats: OrganizationStatistics,
    new_stats: OrganizationStatistics,
) -> None:
    repo_id = old_stats.repo_id

    old_top = [model for model in old_stats.top_three_models]
    new_top = [model for model in new_stats.top_three_models]

    if old_top != new_top:
        message = f"🏆 `{repo_id}` *Top Models updated*"

        for idx, new_model in enumerate(new_top):
            if len(old_top) > idx:
                if old_top[idx].repo_id == new_model.repo_id:
                    message += f"\n    {idx+1}. {new_model.minimal_str()}"
                else:
                    message += f"\n    {idx+1}. ~`{old_top[idx].repo_id}`~ -> {new_model.minimal_str()}"
            else:
                message += f"\n    {idx+1}. {new_model.minimal_str()}"

        app.client.chat_postMessage(channel=channel_id, text=message)


def organization_updates(
    app,
    channel_id: str,
    hf_service: HFService,
    old_stats: OrganizationStatistics,
    new_stats: OrganizationStatistics,
) -> None:

    _organization_followers_updates(app, channel_id, old_stats, new_stats)

    _organization_models_updates(app, channel_id, hf_service, old_stats, new_stats)

    _organization_top_models_updates(app, channel_id, old_stats, new_stats)


def check_for_updates(app):
    store = SubscriptionStore()
    hf_service = HFService()

    with store.lock:

        subscriptions = store.get_subscriptions()

        for channel_id, repos in subscriptions.items():
            for repo_id in repos:

                old_stats = store.get_statistics(channel_id, repo_id)

                try:
                    if isinstance(old_stats, OrganizationStatistics):
                        new_stats = hf_service.get_organization_statistics(repo_id)
                        organization_updates(
                            app, channel_id, hf_service, old_stats, new_stats
                        )
                    else:
                        new_stats = hf_service.get_model_statistics(repo_id)
                        model_updates(app, channel_id, old_stats, new_stats)
                except Exception as e:
                    logging.error(f"Failed to check for updates for {repo_id}: {e}")
                    continue

                store.save_statistics(channel_id, new_stats)


def start_hourly_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: check_for_updates(app),
        trigger="interval",
        seconds=30,
    )
    scheduler.start()
    return scheduler


def start_hourly_scheduler_later(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: check_for_updates(app),
        trigger="cron",
        minute="0",
    )
    scheduler.start()
    return scheduler
