#  Copyright (C) 2016 - Yevgen Muntyan
#  Copyright (C) 2016 - Ignacio Casal Quinteiro
#  Copyright (C) 2016 - Arnavion
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.

#import argparse
#import glob
#import os
#import re
#import shutil
#import subprocess
#import sys
#import traceback
#import hashlib
#import zipfile
#import stat

# Options parser
from gvsbuild.utils.parser import create_parser
# options/printing
import gvsbuild.utils.simple_ui as ui
# All default tools ...
import gvsbuild.tools
# .. and projects
import gvsbuild.projects

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    ui.handle_global_options(args)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()