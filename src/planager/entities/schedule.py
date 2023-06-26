from calendar import Calendar

# from datetime import date, time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from planager.utils.data.norg.norg_utils import Norg
from planager.utils.datetime_extensions import PDate, PDateInputType, PTime

# from planager.utils.scheduling_helpers import resolve_1_collision, resolve_2_collisions, resolve_n_collisions
from planager.utils.misc import tabularize

# from planager.utils.data.norg.norg_utils import make_norg_header
from planager.utils.scheduling_helpers import add_entry_default

from .adhoc import AdHoc
from .entry import FIRST_ENTRY, LAST_ENTRY, Empty, Entry
from .plan import Plan
from .roadmap import Roadmaps
from .routine import Routines
from .task import Tasks


class AdjustmentType(Enum):
    AUTO = 0  # methods figure it out, based on priority and properties
    CLIP = 1  # higher-priority entry takes precedence and lower-priority activity makes way
    SHIFT = 2  #
    COMPRESS = 3  #
    COMPROMISE = 4  #
    DISPLACE = 5  #


class Schedule:
    def __init__(
        self,
        year=PDate.today().year,
        month=PDate.today().month,
        day=PDate.today().day,
        schedule=None,
        width: int = 80,
    ) -> None:
        self.schedule = schedule or [
            FIRST_ENTRY,
            Empty(start=PTime(), end=PTime(24)),
            LAST_ENTRY,
        ]
        self.date: PDate = PDate(year, month, day)
        self.width: int = width
        self.AdjustmentType = AdjustmentType
        self.overflow: List[Entry] = []

    def ensure_bookends(self) -> None:
        if not self.schedule[0] == FIRST_ENTRY:
            self.schedule.insert(0, FIRST_ENTRY)
        if not self.schedule[-1] == LAST_ENTRY:
            self.schedule.append(LAST_ENTRY)

    @classmethod
    def from_norg(cls, path: Path) -> "Schedule":
        # dict = read_norg_day(path)
        schedule = cls()
        return schedule

    @classmethod
    def from_json(cls, path: Path) -> "Schedule":
        schedule = cls()
        return schedule

    # def to_norg(self, path: Path) -> None:
    # header = make_norg_header()
    # body = "\n\n".join(map(Entry.to_norg, self.schedule[1:-1]))
    # notes = make_norg_notes()
    # ...

    def to_json(self, path: Path) -> None:
        ...

    def copy(self):
        newschedule = Schedule()
        newschedule.__dict__.update(self.__dict__)
        return newschedule

    def add(self, entry: Entry, adjustment: AdjustmentType = AdjustmentType.AUTO):
        self.ensure_bookends()
        self.schedule.sort(key=lambda x: x.start)

        match adjustment:
            case AdjustmentType.AUTO:
                self.schedule = add_entry_default(entry, self.schedule)

                # TODO: integrate collision handling into before and after logic

            case AdjustmentType.CLIP:
                raise NotImplemented
            case AdjustmentType.SHIFT:
                raise NotImplemented
            case AdjustmentType.COMPRESS:
                raise NotImplemented
            case AdjustmentType.COMPROMISE:
                raise NotImplementedError
            case _:
                raise ValueError("Invalid adjustment type.")

        self.ensure_bookends()

    def remove(self, entry: Entry, adjustment: AdjustmentType = AdjustmentType.AUTO):
        before = filter(entry.after, self.schedule)
        after = filter(entry.before, self.schedule)
        overlaps = filter(entry.overlaps, self.schedule)

        match adjustment:
            case AdjustmentType.AUTO:
                ...
            case AdjustmentType.CLIP:
                raise NotImplemented
            case AdjustmentType.SHIFT:
                raise NotImplemented
            case AdjustmentType.COMPRESS:
                raise NotImplemented
            case AdjustmentType.COMPROMISE:
                raise NotImplemented
            case _:
                print("Invalid adjustment type.")

        self.schedule = ...

    def __repr__(self) -> str:
        topbeam = "┏" + (self.width - 2) * "━" + "┓"
        date = tabularize(self.date.pretty(), self.width)
        bottombeam = "┗" + (self.width - 2) * "━" + "┛"

        lines = []
        lines.append(topbeam)
        lines.append(date)
        for entry in self.schedule:
            if entry.priority >= 0:
                lines.append(entry.pretty())
        lines.append(bottombeam)
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.__repr__()

    def ispartitioned(self):
        if len(self.schedule) == 1:
            adjacency = True
        else:
            adjacency = all(
                map(
                    lambda x: x[0].end == x[1].start,
                    zip(self.schedule[:-1], self.schedule[1:]),
                )
            )
        return (
            adjacency
            and (self.schedule[0].start == PTime())
            and (self.schedule[-1].end == PTime(24))
        )

    def names(self) -> List[str]:
        return [x.name for x in self.schedule]

    def starts(self) -> List[PTime]:
        return [x.start for x in self.schedule]

    def starts_str(self) -> List[str]:
        return [str(x.start) for x in self.schedule]

    def add_routines(self, routines: Routines) -> None:
        for routine in routines:
            if routine.valid_on(self.date):
                self.add(routine.as_entry(None))

    def add_from_plan(self, plan: Plan, tasks: Tasks) -> None:
        for task_id in plan[self.date]:
            self.add(tasks[task_id].as_entry(None))

    def add_adhoc(self, adhoc: AdHoc) -> None:
        for entry in adhoc[self.date]:
            self.add(entry)


# d = Schedule(2023, 5, 23)
# d.schedule = [
#     Entry(name="Entry 1", start=PTime(4,30), end=PTime(5,45)),
#     Entry(name="Entry 2", start=PTime(7,10), end=PTime(7,30), priority=56),
#     Entry(name="R & R", start=PTime(9,15), end=PTime(9,50)),
#     Entry(name="Last Entry for the schedule: reading at my own discretion", start=PTime(17,30), end=PTime(19,15), priority=10)
# ]


class Schedules:
    def __init__(self, schedules: Dict[PDate, Schedule] = {}) -> None:
        self._schedules = schedules

    def __getitem__(self, __key: PDateInputType) -> Schedule:
        __key = PDate.ensure_is_pdate(__key)
        return self._schedules[__key]

    def __setitem__(self, __key: PDateInputType, __value: Any) -> None:
        assert isinstance(__value, Schedule)
        __key = PDate.ensure_is_pdate(__key)
        self._schedules.update({__key: __value})

    @classmethod
    def from_norg_workspace(cls, workspace_dir: Path) -> "Schedules":
        file = workspace_dir / "roadmaps.norg"
        parsed: Norg = Norg.from_path(file)
        ...  # TODO
        return cls()

    def __str__(self) -> str:
        return "\n".join(map(str, self._schedules.values()))

    def __repr__(self) -> str:
        return self.__str__()


"""
t = PDate.today()
scheds = {t: "today's schedule}
s = Schedules(schedules={})
"""


# def __getattr__(self, __name: str) -> Any:
#     if __name in self.__dict__:
#         return self.__dict__[__name]
#     elif __name in self._schedules:
#         return self._schedules[__name]
#     else:
#         raise ValueError("Invalid attribute.")

# def __setattr__(self, __name: str, __value: Any) -> None:
#     pass


class SchedulePatch:
    def __init__(self) -> None:
        ...


class SchedulePatches:
    def __init__(self, schedule_patches: Dict[PDate, SchedulePatch] = {}) -> None:
        self._patches: Dict[PDate, SchedulePatch] = schedule_patches

    def __getitem__(self, __key: PDateInputType) -> SchedulePatch:
        key = PDate.ensure_is_pdate(__key)
        return self._patches.get(__key, SchedulePatch())

    # def __setitem__(self, __key: PDateInputType, __value: Any) -> None:
    #     ...

    @classmethod
    def from_norg_workspace(cls, workspace_dir: Path) -> "SchedulePatches":
        # file = workspace_dir / "roadmaps.norg"
        # parsed = Norg.from_path(file)
        # ...
        # return cls()
        return cls()

    @property
    def end_date(self) -> PDate:
        if not self._patches:
            return PDate.tomorrow()
        return max(self._patches)

    @property
    def start_date(self) -> PDate:
        if not self._patches:
            return PDate.tomorrow()
        return min(self._patches)
