from typing import Literal


def crossed_milestone(
    old: int, new: int, strategy: Literal["downloads", "likes"]
) -> int | None:
    """
    Returns the highest milestone crossed between old and new values.
    Only returns a milestone if it was crossed.
    """

    if new <= old:
        return None

    milestones = set()

    if strategy == "downloads":
        # Early milestones
        milestones.update([100, 500])
        # 1k steps up to 10k
        milestones.update(range(1000, 10001, 1000))
        # 250 steps between 10k–20k
        milestones.update(range(10000, 20001, 250))
        # 5k steps from 20k+
        milestones.update(range(20000, new + 5000, 5000))
    elif strategy == "likes":
        # Early milestones for likes
        milestones.update([5, 10, 50, 100, 250, 500])
        # 10 steps up to 100
        milestones.update(range(10, 101, 10))
        # 20 steps between 100 and 200
        milestones.update(range(100, 201, 20))
        # 50 steps from 200
        milestones.update(range(200, new + 50, 50))
    else:
        raise ValueError(f"Unknown milestone strategy: {strategy}")

    crossed = [m for m in milestones if old < m <= new]

    return max(crossed) if crossed else None
