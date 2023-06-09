from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from ...util import ConfigType, Norg, PDate, PTime, tabularize
from ..base.task import Task


class Tasks:
    def __init__(self) -> None:
        self._tasks: Dict[Tuple[str, str, str], Task] = {}

    def add(self, task: Task) -> None:
        self._tasks.update({task.id: task})

    def __iter__(self) -> Iterator[Task]:
        return iter(self._tasks.values())

    def __getitem__(self, __key: Tuple[str, str, str]) -> Task:
        return self._tasks[__key]

    @classmethod
    def from_norg_path(
        cls,
        norg_path: Path,
        project_id: Tuple[str, str],
        project_name: str,  # **kwargs
    ) -> "Tasks":
        assert project_name != "/"
        tasks = cls()
        norg_obj = Norg.from_path(norg_path)
        for id, item in enumerate(norg_obj.items, start=1):
            parse = norg_obj.parse_item_with_attributes(item)
            tasks.add(
                Task(
                    parse["title"],
                    (*project_id, str(id)),
                    project_name=project_name,
                    **parse["attributes"],
                )
            )
        return tasks

    @classmethod
    def from_string_iterable(
        cls,
        task_list: List[str],
        project_id: Tuple[str, str],
        project_name: str,
        priority: Optional[int] = None,
    ) -> "Tasks":
        tasks = cls()
        for task_id, name in enumerate(task_list, start=1):
            # name = name if isinstance(name, str) else name.name
            id = (*project_id, str(task_id))
            task = (
                Task(name, id, priority)
                if priority is not None
                else Task(name, id, project_name=project_name)
            )
            tasks.add(task)
        return tasks

    def __str__(self) -> str:
        return self.pretty()

    def __repr__(self) -> str:
        return self.__str__()

    def pretty(self, width: int = 80) -> str:
        topbeam = "┏" + (width - 2) * "━" + "┓"
        bottombeam = "\n┗" + (width - 2) * "━" + "┛"
        # thickbeam = "┣" + (width - 2) * "━" + "┫"
        thinbeam = "┠" + (width - 2) * "─" + "┨"
        format_number = lambda s: (len(str(s)) == 1) * " " + f" {s} │ "
        top = tabularize("Tasks", width, pad=1)
        empty = tabularize("", width)
        names = "\n".join(
            map(
                lambda x: tabularize(
                    f"{format_number(x[0])}{x[1].name} (ID {x[1].id})", width
                ),
                self._tasks.items(),
            )
        )
        return (
            "\n".join(("", topbeam, empty, top, empty, thinbeam, empty, ""))
            + names
            + "\n"
            + empty
            + bottombeam
        )

    def ids(self) -> List[Tuple[str, str, str]]:
        return list(self._tasks)

    @classmethod
    def from_roadmaps(cls, roadmaps: Iterable[Iterable[Iterable["Task"]]]) -> "Tasks":
        new_tasks = Tasks()
        for roadmap in roadmaps:
            for project in roadmap:
                for task in project:
                    new_tasks._tasks.update({task.id: task})
        return new_tasks
