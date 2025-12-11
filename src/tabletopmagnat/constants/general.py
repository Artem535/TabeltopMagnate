from enum import StrEnum


class Prompts(StrEnum):
    SECURITY = "security"
    TASK_SPLITTER = "task_splitter"
    TASK_CLASSIFIER = "task_classifier"
    EXPERT_1 = "expert_1"
    EXPERT_2 = "expert_2"
    EXPERT_3 = "expert_3"
    SUMMARY = "summary"


class NodeNames(StrEnum):
    SECURITY = "security"
    ECHO = "echo"
    TASK_SPLITTER = "task_splitter"
    TASK_CLASSIFIER = "task_classifier"
    EXPERT_PARALLEL_COORDINATOR = "expert_parallel_coordinator"
    JOIN = "join"
    SUMMARY = "summary"
    SWITCH = "switch"
    EXPERT_1 = "expert_1"
    EXPERT_2 = "expert_2"
    EXPERT_3 = "expert_3"
