from dataclasses import dataclass
from typing import Any, Union, List, Dict
import pandas as pd
from core.config import FIELD_TYPE_MAPPING


class AdStatistics:
    def __init__(self):

        self.df = pd.DataFrame(columns=list(FIELD_TYPE_MAPPING.keys()))

    def add_rows(self, rows_data: Union[List[Dict], Dict]):
        if isinstance(rows_data, dict):
            rows_data = [rows_data]
        new_rows = pd.DataFrame(rows_data)
        self.df = pd.concat([self.df, new_rows], ignore_index=True)

    def get_dataframe(self) -> pd.DataFrame:
        return self.df


@dataclass
class StatRow:
    """Инициализация полей из конфига"""

    def __init__(self, **kwargs: Any):
        for field_name, field_type in FIELD_TYPE_MAPPING.items():
            value = kwargs.get(field_name, None)
            if value is not None and not isinstance(value, field_type):
                raise TypeError(
                    f"Field '{field_name}' must be of type {field_type.__name__} or None"
                )
            setattr(self, field_name, value)
