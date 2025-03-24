from dataclasses import dataclass
import pandas as pd
from core.config import DF_COLUMNS


class AdStatistics:
    def __init__(self):

        self.df = pd.DataFrame(columns=DF_COLUMNS)

    def add_row(self, row_data):

        new_row = pd.Series(row_data)
        self.df = self.df.append(new_row, ignore_index=True)

    def add_rows(self, rows_data):

        new_rows = pd.DataFrame(rows_data)
        self.df = pd.concat([self.df, new_rows], ignore_index=True)

    def get_dataframe(self):
        return self.df


@dataclass
class StatRow:
    ad_id: int = None
    compaign_id: int = None
    compaign_name: str = None
