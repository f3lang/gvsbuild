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

"""
Various downloader / unpacker (tar, git, hg, ...)
"""

import os
import shutil
import zipfile
import tarfile

from .simple_ui import print_log
from .simple_ui import print_debug

def extract_exec(src, dest_dir, dir_part=None, strip_one=False, check_file=None):
    """
    Extract (or copy, in case of an exe file) from src to dest_dir, 
    handling the strip of the first part of the path in case of the tarbombs.

    dir_part is a piece, present in the tar/zip file, added to the desst_dir for
    the checks 

    if check_file is passed and is present in the filesystem the extract is
    skipped (tool alreay installed)
    """

    # Support function
    def __get_stripped_tar_members(tar):
        for tarinfo in tar.getmembers():
            path = tarinfo.name.split('/')
            if len(path) == 1:
                if tarinfo.isdir():
                    continue
                else:
                    raise Exception('Cannot strip directory prefix from tar with top level files')
            tarinfo.name = '/'.join(path[1:])
            if tarinfo.issym() or tarinfo.islnk():
                tarinfo.linkname = '/'.join(tarinfo.linkname.split('/')[1:])
            yield tarinfo

    if check_file and os.path.isfile(check_file):
        print_debug('Skipping %s handling, %s present' % (src, check_file, ))
        return

    if dir_part:
        full_dest = os.path.join(dest_dir, dir_part)
    else:
        full_dest = dest_dir

    print_log('Extracting %s to %s' % (src, full_dest, ))        
    os.makedirs(full_dest, exist_ok=True)

    _n, ext = os.path.splitext(src.lower())
    if ext == '.exe':
        # Exe file, copy directly 
        shutil.copy2(src, dest_dir)
    elif ext == '.zip':
        # Zip file
        with zipfile.ZipFile(src) as zf:
            zf.extractall(path=dest_dir)
    else:
        # Ok, hoping it's a tarfile we can handle :) 
        with tarfile.open(src) as tar:
            tar.extractall(dest_dir, __get_stripped_tar_members(tar) if strip_one else tar.getmembers())

class Tarball(object):
    def unpack(self):
        extract_exec(self.archive_file, self.build_dir, strip_one=not self.tarbomb)
        print_log('Extracted %s' % (self.archive_file,))

class MercurialRepo(object):
    def unpack(self):
        print_log('Cloning %s to %s' % (self.repo_url, self.build_dir))
        self.exec_cmd('hg clone %s %s-tmp' % (self.repo_url, self.build_dir))
        shutil.move(self.build_dir + '-tmp', self.build_dir)
        print_log('Cloned %s to %s' % (self.repo_url, self.build_dir))

    def update_build_dir(self):
        print_log('Updating directory %s' % (self.build_dir,))
        self.exec_cmd('hg pull -u', working_dir=self.build_dir)

class GitRepo(object):
    def unpack(self):
        print_log('Cloning %s to %s' % (self.repo_url, self.build_dir))

        self.builder.exec_msys('git clone %s %s-tmp' % (self.repo_url, self.build_dir))
        shutil.move(self.build_dir + '-tmp', self.build_dir)

        if self.fetch_submodules:
            self.builder.exec_msys('git submodule update --init',  working_dir=self.build_dir)

        if self.tag:
            self.builder.exec_msys('git checkout -f %s' % self.tag, working_dir=self.build_dir)

        print_log('Cloned %s to %s' % (self.repo_url, self.build_dir))

    def update_build_dir(self):
        print_log('Updating directory %s' % (self.build_dir,))

        # I don't like too much this, but at least we ensured it is properly cleaned up
        self.builder.exec_msys('git clean -xdf', working_dir=self.build_dir)

        if self.tag:
            self.builder.exec_msys('git fetch origin', working_dir=self.build_dir)
            self.builder.exec_msys('git checkout -f %s' % self.tag, working_dir=self.build_dir)
        else:
            self.builder.exec_msys('git checkout -f', working_dir=self.build_dir)
            self.builder.exec_msys('git pull --rebase', working_dir=self.build_dir)

        if self.fetch_submodules:
            self.builder.exec_msys('git submodule update --init', working_dir=self.build_dir)

        if os.path.exists(self.patch_dir):
            print_log("Copying files from %s to %s" % (self.patch_dir, self.build_dir))
            self.builder.copy_all(self.patch_dir, self.build_dir)
