# Copyright (C) 2020-2021 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest
from unittest.mock import patch

import re
from pathlib import Path
import subprocess
from argparse import Namespace

from pontos.updateheader.updateheader import (
    _get_modified_year as get_modified_year,
    _find_copyright as find_copyright,
    _add_header as add_header,
    _update_file as update_file,
)


class UpdateHeaderTestCase(unittest.TestCase):
    @patch('pontos.updateheader.updateheader.run')
    def test_get_modified_year(self, run_mock):
        test_file = Path(__file__).parent / "test.py"
        test_file.touch(exist_ok=True)

        run_mock.return_value = subprocess.CompletedProcess(
            args=[
                'git',
                'log',
                '-1',
                '--format=%ad',
                '--date=format:%Y',
                f'{test_file}',
            ],
            returncode=0,
            stdout='2020\n',
            stderr='',
        )

        year = get_modified_year(f=test_file)
        self.assertEqual(year, '2020')

        test_file.unlink()

    def test_get_modified_year_error(self):
        test_file = Path(__file__).parent / "test.py"
        if test_file.exists():
            test_file.unlink()

        with self.assertRaises(subprocess.CalledProcessError):
            get_modified_year(f=test_file)

    def test_find_copyright(self):
        test_line = "# Copyright (C) 1995-2021 Greenbone Networks GmbH"
        test2_line = "# Copyright (C) 1995 Greenbone Networks GmbH"
        invalid_line = (
            "# This program is free software: "
            "you can redistribute it and/or modify"
        )

        company = "Greenbone Networks GmbH"

        regex = re.compile(
            "[Cc]opyright.*?(19[0-9]{2}|20[0-9]{2}) "
            f"?-? ?(19[0-9]{{2}}|20[0-9]{{2}})? ({company})"
        )

        # Full match
        found, match = find_copyright(regex=regex, line=test_line)
        self.assertTrue(found)
        self.assertIsNotNone(match)
        self.assertEqual(match['creation_year'], "1995")
        self.assertEqual(match['modification_year'], "2021")
        self.assertEqual(match['company'], "Greenbone Networks GmbH")

        # No modification Date
        found, match = find_copyright(regex=regex, line=test2_line)
        self.assertTrue(found)
        self.assertIsNotNone(match)
        self.assertEqual(match['creation_year'], "1995")
        self.assertEqual(match['modification_year'], None)
        self.assertEqual(match['company'], "Greenbone Networks GmbH")

        # No match
        found, match = find_copyright(regex=regex, line=invalid_line)
        self.assertFalse(found)
        self.assertIsNone(match)

    def test_add_header(self):
        company = "Greenbone Networks GmbH"

        expected_header = """# -*- coding: utf-8 -*-
# Copyright (C) 2020 Greenbone Networks GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

        header = add_header(
            suffix=".py", licence='AGPL-3.0-or-later', company=company
        )

        self.assertEqual(header, expected_header)

    def test_update_file(self):
        args = Namespace()
        args.company = 'Greenbone Networks GmbH'
        args.year = ('2020',)
        args.changed = (False,)

        regex = re.compile(
            "[Cc]opyright.*?(19[0-9]{2}|20[0-9]{2}) "
            f"?-? ?(19[0-9]{{2}}|20[0-9]{{2}})? ({args.company})"
        )
        update_file(file=Path(__file__), regex=regex, args=args)