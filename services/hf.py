from huggingface_hub import HfApi

from schemas.hf import ModelStatistics, OrganizationStatistics, User


class HFService:
    def __init__(self):
        self.api = HfApi(
            # fake token to ensure only public models get fetched
            token="hf_dnw"
        )

    def get_model_statistics(self, repo_id: str) -> ModelStatistics:
        model_info = self.api.model_info(repo_id)
        return ModelStatistics(
            repo_id=repo_id,
            downloads=model_info.downloads,
            likes=model_info.likes,
        )

    def get_new_models(self, repo_id: str, limit: int) -> list[ModelStatistics]:

        return [
            ModelStatistics(
                repo_id=model_info.id,
                downloads=model_info.downloads,
                likes=model_info.likes,
            )
            for model_info in self.api.list_models(
                author=repo_id, sort="last_modified", limit=limit
            )
        ]

    def get_organization_statistics(self, repo_id: str) -> OrganizationStatistics:
        organization_overview = self.api.get_organization_overview(repo_id)

        num_followers = organization_overview.num_followers
        num_models = organization_overview.num_models

        followers = (
            [
                User(
                    username=user.username,
                    fullname=user.fullname,
                    organizations=[
                        org.name
                        for org in self.api.get_user_overview(user.username).orgs
                    ],
                )
                for user in self.api.list_organization_followers(repo_id)
            ]
            if num_followers <= 50
            else []
        )

        top_three_models = [
            ModelStatistics(
                repo_id=model_info.id,
                downloads=model_info.downloads,
                likes=model_info.likes,
            )
            for model_info in self.api.list_models(
                author=repo_id, sort="downloads", limit=3, full=False
            )
        ]

        return OrganizationStatistics(
            repo_id=repo_id,
            followers=followers,
            num_followers=num_followers,
            num_models=num_models,
            top_three_models=top_three_models,
        )
