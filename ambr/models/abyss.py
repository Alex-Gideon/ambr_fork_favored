import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from ..utils import remove_html_tags


class Blessing(BaseModel):
    """
    Blessing model.

    Attributes:
        description (str): Description of the blessing.
        level_config_name (str): Level configuration name.
        visible (bool): Visibility status.
    """

    description: str
    level_config_name: str = Field(..., alias="levelConfigName")
    visible: bool

    @field_validator("description", mode="before")
    def _format_description(cls, v) -> str:
        return remove_html_tags(v)


class ChallengeTarget(BaseModel):
    """
    ChallengeTarget model.

    Attributes:
        type (str): Type of the challenge target.
        values (List[int]): List of values.
        formatted (str): Formatted challenge target.
    """

    type: str
    values: List[int]

    @property
    def formatted(self) -> str:
        return self.type.format("/".join(str(v) for v in self.values))


class Chamber(BaseModel):
    """
    Chamber model.

    Attributes:
        id (int): ID of the chamber.
        challenge_target (ChallengeTarget): Challenge target.
        enemy_level (int): Enemy level.
        wave_one_enemies (List[int]): List of enemies in the first wave.
        wave_two_enemies (Optional[List[int]]): List of enemies in the second wave.
    """

    id: int
    challenge_target: ChallengeTarget = Field(..., alias="challengeTarget")
    enemy_level: int = Field(..., alias="monsterLevel")
    wave_one_enemies: List[int] = Field(..., alias="firstMonsterList")
    wave_two_enemies: Optional[List[int]] = Field(None, alias="secondMonsterList")


class LeyLineDisorder(BaseModel):
    """
    LeyLineDisorder model.

    Attributes:
        description (str): Description of the disorder.
        level_config_name (str): Level configuration name.
        visible (bool): Visibility status.
    """

    description: str
    level_config_name: str = Field(..., alias="levelConfigName")
    visible: bool

    @field_validator("description", mode="before")
    def _format_description(cls, v) -> str:
        return remove_html_tags(v)


class Floor(BaseModel):
    """
    Floor model.

    Attributes:
        id (int): ID of the floor.
        chambers (List[Chamber]): List of chambers.
        ley_line_disorders (List[LeyLineDisorder]): List of ley line disorders.
        override_enemy_level (int): Override enemy level.
        team_num (int): Number of teams.
    """

    id: int
    chambers: List[Chamber] = Field(..., alias="chamberList")
    ley_line_disorders: List[LeyLineDisorder] = Field(..., alias="leyLineDisorder")
    override_enemy_level: int = Field(..., alias="overrideMonsterLevel")
    team_num: int = Field(..., alias="teamNum")


class AbyssData(BaseModel):
    """
    AbyssData model.

    Attributes:
        open_time (Optional[datetime.datetime]): Opening time.
        floors (List[Floor]): List of floors.
    """

    open_time: Optional[datetime.datetime] = Field(None, alias="openTime")
    floors: List[Floor] = Field(..., alias="floorList")

    @field_validator("open_time", mode="before")
    def _format_open_time(cls, v) -> Optional[datetime.datetime]:
        return datetime.datetime.fromtimestamp(v) if v else None


class Abyss(BaseModel):
    """
    Abyss model.

    Attributes:
        id (int): ID of the abyss.
        close_time (datetime.datetime): Closing time.
        blessing (Blessing): Blessing.
        abyss_corridor (AbyssData): Abyss corridor.
        abyssal_moon_spire (AbyssData): Abyssal moon spire.
    """

    id: int
    close_time: datetime.datetime = Field(..., alias="closeTime")
    blessing: Blessing
    abyss_corridor: AbyssData = Field(..., alias="entrance")
    abyssal_moon_spire: AbyssData = Field(..., alias="schedule")

    @field_validator("close_time", mode="before")
    def _format_close_time(cls, v) -> datetime.datetime:
        # example: 1709258399
        return datetime.datetime.fromtimestamp(v)


class AbyssEnemy(BaseModel):
    """
    AbyssEnemy model.

    Attributes:
        icon (str): Icon URL.
        id (int): ID of the enemy.
        link (bool): Link status.
        name (str): Name of the enemy.
    """

    icon: str
    id: int
    link: bool
    name: str

    @field_validator("icon", mode="before")
    def _convert_icon_url(cls, v: str) -> str:
        return f"https://api.ambr.top/assets/UI{'/monster' if 'MonsterIcon' in v else ''}/{v}.png"  # noqa: E501


class AbyssResponse(BaseModel):
    """
    AbyssResponse model.

    Attributes:
        enemies (List[AbyssEnemy]): List of abyss enemies.
        abyss_items (List[Abyss]): List of abyss items.
    """

    enemies: List[AbyssEnemy] = Field(..., alias="monsterList")
    abyss_items: List[Abyss] = Field(..., alias="items")

    @field_validator("enemies", mode="before")
    def _convert_enemies(cls, v: Dict[str, Dict[str, Any]]) -> List[AbyssEnemy]:
        return [AbyssEnemy(**v[item_id]) for item_id in v]

    @field_validator("abyss_items", mode="before")
    def _convert_abyss_items(cls, v: Dict[str, Dict[str, Any]]) -> List[Abyss]:
        return [Abyss(**v[item_id]) for item_id in v]