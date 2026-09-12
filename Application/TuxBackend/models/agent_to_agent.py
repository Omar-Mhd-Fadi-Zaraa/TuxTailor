from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class BuildStage(Enum):
    CREATING_CONFIGURATION = "creating configuration"
    DEPLOYING_CONTAINER = "Deploying docker container"
    BUILDING_ISO = "building ISO"
    TESTING = "testing ISO"
    FINISHED = "ISO built without errors"


class AgentState(Enum):
    WAITING_FOR_RESPONSE = "waiting for response from chat agent"
    ERROR = "error while building, attempting fix."


class BuildError(Exception):
    def __init__(self, stage: BuildStage, logs: str) -> None:
        super().__init__(f"{stage.value}: {logs}")
        self.stage = stage
        self.logs = logs


class BuildResult(BaseModel):
    final_result: Literal["success", "failure"] = Field(
        description="Whether the ISO building succeeded or failed and unable to attempt a restart."
    )
    path: str | None = Field(
        description="Absolute path to the ISO, set to none if failure."
    )
    errors: dict[str, str] | None = Field(
        description="List of errors that occured while building, none if no errors occured."
    )


class RecoveryResult(BaseModel):
    result: Literal["User", "Fixed"] = Field(
        description="Determines whether the error was fixed by the agent or needs user intervention."
    )
    explanation: str = Field(
        description="Explanation for the fix the agent implemented or an explanation for why the error requires user intervention."
    )


class SystemBase(BaseModel):
    kernel: str = Field(description="Kernel name and version.", alias="kernel")
    bootloader: str = Field(
        description="Name of the bootloader to use with the system.", alias="bootloader"
    )
    filesystem: str = Field(
        description="Main filesystem of the configuration.", alias="filesystem"
    )
    compression: str = Field(
        description="Compression type for the filesystem.", alias="compression"
    )


class Desktop(BaseModel):
    environment: str = Field(
        description="Desktop environment or window manager.", alias="environment"
    )
    display_manager: str = Field(
        description="Display manager to use with the environment.",
        alias="displayManager",
    )
    theme: str | None = Field(
        description="Theme to apply to the desktop at first run, set to null to apply the base theme of the desktop environment.",
        alias="theme",
    )


class Locale(BaseModel):
    lang: str = Field(description="Language of choice for the system.", alias="lang")
    timezone: str = Field(
        description="Timezone for the system clock.", alias="timezone"
    )
    keymap: str = Field(description="Keyboard mapping.", alias="keymap")


class Networking(BaseModel):
    manager: str = Field(
        description="Which networking manager to use for the system.", alias="manager"
    )
    hostname: str = Field(
        description="Host name of the machine so show in networking.", alias="hostname"
    )


class User(BaseModel):
    name: str = Field(description="User name.", alias="name")
    shell: str = Field(description="Default shell or the user.", alias="shell")
    groups: list[str] = Field(
        description="List of group names the user should belong to.", alias="groups"
    )


class ISOSpec(BaseModel):
    distro: str = Field(
        description="The name of the distribution the configuration is based on.",
        alias="distro",
    )
    iso_name: str = Field(description="The name of the ISO file.", alias="isoName")
    packages: list[str] = Field(
        description="List of package names to be installed on the system.",
        alias="packages",
    )
    services: list[str] = Field(
        description="List of service names to be enabled on the system.",
        alias="services",
    )
    base: SystemBase = Field(
        description="The low-level base of the system", alias="base"
    )
    desktop: Desktop | None = Field(
        description="The desktop configuration, set to null to skip configuring a desktop.",
        alias="desktop",
    )
    locale: Locale = Field(description="Locale settings.", alias="locale")
    networking: Networking = Field(
        description="Network configuration.", alias="networking"
    )
    users: list[User] = Field(
        description="List of users for the system and their configuration.",
        alias="users",
    )
