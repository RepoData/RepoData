#!/usr/bin/env python3

"""
This utility finds likely duplicates in the base dataset and tries to remediate
them with help from the user. Duplicates are considered entries that share the
same name (repository_name_unauthorized), city (st_city) and state.

If you are checking some new records from a particular user you can use the
--entry-recorded-by option to only report duplicates involving records created
by that person.
"""

import re
import pandas
import argparse
import rich.box

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel
from rich.style import Style

from os.path import abspath, dirname, join

# source data
source_path = join(abspath(dirname(__file__)), '..', 'data.csv')

def main():
    parser = argparse.ArgumentParser(
        prog='dedupe',
        description='A utility to help de-duplicate source CSV data'
    )
    parser.add_argument('--entry-recorded-by', help='Name of the person who entered the record')
    parser.add_argument('--no-pobox', action='store_true', help='Ignore duplicates involving PO Box addresses')
    parser.add_argument('--min', type=int, default=0, help='Only display duplicates with >= n')
    args = parser.parse_args()

    analyzer = DupeAnalyzer(args.entry_recorded_by, args.no_pobox, args.min)
    dupes = analyzer.get_dupes()
    mediator = DupeMediator(dupes)
    mediator.run()


class DupeAnalyzer:
    """
    This class is responsible for searching the dataset and reporting on
    duplicates. It basically makes it a bit easier to not pass around some of
    the options all over the place.
    """

    def __init__(self, entry_recorded_by=None, no_pobox=False, dupe_min=0):
        self.entry_recorded_by = entry_recorded_by
        self.no_pobox = no_pobox
        self.dupe_min = dupe_min
        self.df = pandas.read_csv(source_path)

    def get_dupes(self):
        dupes_found = []

        # records with overlapping name, city and state are potential dupes
        dupes = self.df.set_index(['repository_name_unauthorized', 'st_city', 'state']).copy()
        dupes = dupes.dropna(axis=0, subset='street_address_1')
        dupes = dupes.sort_index()

        # filter out pobox addresses if we want to ignore them. 
        # note: previous discussion has identified a need to retain both records
        # when one is a PO Box
        if self.no_pobox:
            dupes = dupes[~dupes.street_address_1.str.match(r'(PO Box)|(P.? ?O.? Box)|(Box)', case=False)]

        for index_val in dupes.index.unique():
            records = dupes.loc[index_val]

            if self.entry_recorded_by:
                if len(records[records.entry_recorded_by == self.entry_recorded_by]) == 0:
                    continue

            if len(records) > 1 and len(records) > self.dupe_min:
                dupes_found.append([rec.id for rec in records.itertuples()])

        return dupes_found


class DupeMediator:

    columns = [
        ("id",                               "ignore"), 
        ("repository_name_unauthorized",     "merge"),
        ("name_notes",                       "merge"),
        ("parent_org_unauthorized",          "merge"),
        ("repository_name_authorized",       "merge"),
        ("repository_identifier_authorized", "merge"),
        ("repository_type",                  "merge"),
        ("location_type",                    "merge"),
        ("street_address_1",                 "merge"),
        ("street_address_2",                 "merge"),
        ("st_city",                          "merge"),
        ("st_zip_code_5_numbers",            "merge"),
        ("st_zip_code_4_following_numbers",  "merge"),
        ("street_address_county",            "merge"),
        ("state",                            "merge"),
        ("url",                              "merge"),
        ("latitude",                         "merge"),
        ("longitude",                        "merge"),
        ("language_of_entry",                "merge"),
        ("date_entry_recorded",              "ignore"),
        ("entry_recorded_by",                "add"),
        ("source_of_repository_data",        "add"),
        ("url_of_source_of_repository_data", "merge"),
        ("geocode_confidence",               "merge"),
        ("notes",                            "append"),
    ]

    def __init__(self, dupes):
        self.dupes = dupes
        self.pos = 0
        self.edits = []
        self.df = pandas.read_csv(source_path, index_col='id')
        self.console = Console()

    @property
    def current_dupe(self):
        return self.dupes[self.pos]
    
    def run(self):
        while self.pos < len(self.dupes):
            # hydrate the record ids back into records
            self.console.clear()
            self.console.print(self.make_table())
            self.prompt()

    def prompt(self):
        text = Text(f"[{self.pos + 1}/{len(self.dupes)}]  ", style="italic")

        text.append("N)", style="bold")
        text.append("ext  ")

        text.append("P)", style="bold")
        text.append("revious  ")

        text.append("D)", style="bold")
        text.append("elete  ")

        if len(self.edits) > 0:
            text.append("U)", style="bold")
            text.append("ndo  ")

        text.append("M)", style="bold")
        text.append("ove prop from,to  ")

        text.append("S)", style="bold")
        text.append("ave  ")

        text.append("Q)", style="bold")
        text.append("uit  ")

        text.append("H)", style="bold")
        text.append("elp")

        # calculate spaces needed for centering the prompt
        spaces = " " * int((self.console.size[0] - len(text)) / 2)

        cmd = Prompt.ask(Text(spaces) + text).lower()

        if m := re.match(r"^m (\d+) (\d+),(\d+)$", cmd):
            prop, from_rec, to_rec = map(int, m.groups())
            prop = self.columns[prop - 1]
            from_rec = self.current_dupe[from_rec - 1]
            to_rec = self.current_dupe[to_rec - 1]
            self.edit_property(prop, from_rec, to_rec)
        elif m := re.match(r"^d (\d+)", cmd):
            rec = int(m.group(1)) - 1
            rec = self.current_dupe[rec]
            self.delete(rec)
        elif cmd == "u":
            self.undo()
        elif cmd == "q":
            self.quit()
        elif cmd == "p" and self.pos > 0:
            self.previous()
        elif cmd == "s":
            self.save()
        elif cmd == "n" or cmd == "":
            self.next()
        elif cmd == "h":
            self.help()

    def previous(self):
        self.pos -= 1
        self.edits = []

    def next(self):
        self.pos += 1
        self.edits = []

    def undo(self):
        if len(self.edits) == 0:
            return

        edit = self.edits.pop()

        if type(edit) == tuple:
            rec_id, prop_name, old_val = edit
            self.df.at[rec_id, prop_name] = old_val
        else:
            # add the old record back by concatenating to the end of the dataframe
            self.df = pandas.concat([self.df, pandas.DataFrame([edit])])

    def quit(self):
        self.pos = len(self.dupes)

    def save(self):
        self.df = self.df.sort_index()
        self.df.to_csv('data.csv', lineterminator='\r\n')

    def edit_property(self, prop, from_rec_id, to_rec_id):
        prop_name, prop_spec = prop
        old_val = self.df.at[to_rec_id, prop_name]
        self.edits.append((to_rec_id, prop_name, old_val))
        self.df.at[to_rec_id, prop_name] = self.df.loc[from_rec_id][prop_name]

    def delete(self, rec_id):
        rec = self.df.loc[rec_id].copy()
        self.edits.append(rec)
        self.df = self.df.drop(rec_id)

    def help(self):
        self.console.clear()
        help_text = Markdown(
"""
Here are the available commands:

**N**
: Move to the *next* set of duplicate records.

**P**
: Move to the *previous* set of duplicate records.

**D**
: *Delete* a record identified by its number. For example `D 2`.

**U**
: *Undo* the last change.

**M** 
: *Move* a property value from one record to another using the number of the property, and a comma separated list of of the record number to copy from and to. For example to move the value of property 8 from record 2 to record 1: `M 8 2,1`.

**S**
: *Save* the state of the dataset as *data.csv*.

**Q**
: *Quit* without saving changes.

**H**
: View this *help* documentation!

Press *ENTER* to return to editing.
"""
        )
        self.console.print(
            Panel(
                help_text,
                padding=(2, 10),
                title="Dedupe Help",
                highlight=True
            )
        )
        Prompt.ask()

    def make_table(self):
        recs = []
        for rec_id in self.current_dupe:
            if rec_id in self.df.index:
                recs.append(self.df.loc[rec_id])
        table = Table(box=rich.box.ROUNDED, width=self.console.size[0])
        table.add_column('Property', width=40)
        col_width = int((self.console.size[0] - 40) / len(recs))
        for i in range(1, len(recs) + 1):
            table.add_column(Text.assemble("Record ", (str(i), "italic")), width=col_width)
      
        # get the last edit if we have edits and the last edit moved a value (not a delete)
        last_edit = self.edits[-1] if len(self.edits) > 0 and type(self.edits[-1]) == tuple else None

        count = 0
        for col, col_spec in self.columns:
            count += 1
            prop = Text.assemble((f"{count:2d}", "italic"), f" {col}")

            if col == "id":
                table.add_row(prop, *[rec.name for rec in recs])
            else:
                row = [prop]
                for rec in recs:

                    # highlight the cell if it was the last edit
                    if last_edit is not None and last_edit[0] == rec.name and last_edit[1] == col:
                        reverse = True
                    else:
                        reverse = False

                    # make into a clickable link if it looks like a URL
                    text = str(rec[col])
                    link = text if text.startswith('http') else None

                    row.append(Text(text, style=Style(reverse=reverse, link=link)))
                table.add_row(*row)

        return table


if __name__ == "__main__":
    main()
