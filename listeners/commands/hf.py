from persistence.subscription_store import SubscriptionStore, DATABASE_FILE, WEEKLY_STATS_FILE
from services.hf import HFService


def hf_callback(command, ack, respond, client, logger):
    try:
        ack()
        text = command.get("text", "").strip()
        channel_id = command["channel_id"]

        if text == "data":
            files = []
            for path in [DATABASE_FILE, WEEKLY_STATS_FILE]:
                if path.exists():
                    files.append({"file": str(path), "title": path.name})
            if not files:
                respond("No data files found.")
                return
            client.files_upload_v2(
                channel=channel_id,
                file_uploads=files,
                initial_comment="📊 Here are the current data files:",
            )
            return

        if text.startswith("subscribe"):
            _, repo_id = text.split(maxsplit=1)
            if "/" in repo_id:
                statistics = HFService().get_model_statistics(repo_id)
            else:
                statistics = HFService().get_organization_statistics(repo_id)
            SubscriptionStore().save_statistics(channel_id, statistics)
            respond(f"✅ This channel is now subscribed to\n\n{str(statistics)}")
            return

        if text.startswith("unsubscribe"):
            _, repo_id = text.split(maxsplit=1)
            SubscriptionStore().unsubscribe(channel_id, repo_id)
            respond(f"🛑 This channel has unsubscribed from `{repo_id}`.")
            return

        if text == "now":
            subscriptions = (
                SubscriptionStore().get_subscriptions().get(channel_id, None)
            )
            if not subscriptions:
                respond(
                    "This channel is not subscribed to a model or organization yet. "
                    "Subscribe with `/hf subscribe <model/organization>`."
                )
                return

            hf_service = HFService()
            response = ""
            for repo_id in subscriptions:
                if "/" in repo_id:
                    statistics = hf_service.get_model_statistics(repo_id)
                else:
                    statistics = hf_service.get_organization_statistics(repo_id)
                response += str(statistics) + "\n\n"
            respond(response)
            return

        respond(
            "Usage:\n"
            " • `/hf now`\n"
            " • `/hf subscribe <model/organization id>`\n"
            " • `/hf unsubscribe <model/organization id>`\n"
            " • `/hf data`"
        )

    except Exception as e:
        logger.error(e)
        respond("Something went wrong.", e)
