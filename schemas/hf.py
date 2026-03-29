from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ModelStatistics:
    repo_id: str

    downloads: int
    likes: int

    def __str__(self):
        return f"*Model:* {self.minimal_str()}"

    def minimal_str(self) -> str:
        return f"`{self.repo_id}` – {self.stats_str()}"

    def stats_str(self) -> str:
        return f"{self.downloads:,} downloads (30d), {self.likes} ❤️"


@dataclass_json
@dataclass
class User:
    username: str
    fullname: str
    organizations: list[str] = field(default_factory=list)

    def _name(self) -> str:
        if self.username.lower() == self.fullname.lower():
            return self.fullname
        return f"{self.username} ({self.fullname})"

    def __str__(self) -> str:
        if self.organizations:
            orgs = ", ".join(self.organizations)
            return f"{self._name()} @ {orgs}"
        return self._name()


@dataclass_json
@dataclass
class OrganizationStatistics:
    repo_id: str

    top_three_models: list[ModelStatistics]
    followers: list[User] = field(default_factory=list)
    num_followers: int = 0
    num_models: int = 0
    total_downloads: int = 0

    def __str__(self):
        followers_count = (
            f"{self.num_followers:,}" if self.num_followers is not None else "N/A"
        )
        models_count = f"{self.num_models:,}" if self.num_models is not None else "N/A"

        organization_str = f"*Organization:* `{self.repo_id}` - 👥 {followers_count} followers, 🛠 {models_count} models"

        if self.top_three_models:
            organization_str += "\n\n"
            organization_str += "*🏆 Top Models*"
            for idx, model in enumerate(self.top_three_models):
                organization_str += f"\n    {idx + 1}. {model.minimal_str()}️"

        return organization_str


Statistics = ModelStatistics | OrganizationStatistics
