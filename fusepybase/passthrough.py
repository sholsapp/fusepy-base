from __future__ import with_statement

import os
import sys
import errno

from fuse import FuseOSError, Operations


class Passthrough(Operations):
  """A simple passthrough interface.

  This class passes all file system operations through to the operating
  system.

  """
  def __init__(self, root):
    self.root = root

  def access(self, path, mode):
    full_path = os.path.abspath(path)
    if not os.access(full_path, mode):
      raise FuseOSError(errno.EACCES)

  def chmod(self, path, mode):
    full_path = os.path.abspath(path)
    return os.chmod(full_path, mode)

  def chown(self, path, uid, gid):
    full_path = os.path.abspath(path)
    return os.chown(full_path, uid, gid)

  def getattr(self, path, fh=None):
    full_path = os.path.abspath(path)
    st = os.lstat(full_path)
    return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
           'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

  def readdir(self, path, fh):
    full_path = os.path.abspath(path)

    dirents = ['.', '..']
    if os.path.isdir(full_path):
      dirents.extend(os.listdir(full_path))
    for r in dirents:
      yield r

  def readlink(self, path):
    pathname = os.readlink(os.path.abspath(path))
    if pathname.startswith("/"):
      # Path name is absolute, sanitize it.
      return os.path.relpath(pathname, self.root)
    else:
      return pathname

  def mknod(self, path, mode, dev):
    return os.mknod(os.path.abspath(path), mode, dev)

  def rmdir(self, path):
    full_path = os.path.abspath(path)
    return os.rmdir(full_path)

  def mkdir(self, path, mode):
    return os.mkdir(os.path.abspath(path), mode)

  def statfs(self, path):
    full_path = os.path.abspath(path)
    stv = os.statvfs(full_path)
    return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
      'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
      'f_frsize', 'f_namemax'))

  def unlink(self, path):
    return os.unlink(os.path.abspath(path))

  def symlink(self, target, name):
    return os.symlink(self._full_path(target), self._full_path(name))

  def rename(self, old, new):
    return os.rename(self._full_path(old), self._full_path(new))

  def link(self, target, name):
    return os.link(self._full_path(target), self._full_path(name))

  def utimens(self, path, times=None):
    return os.utime(os.path.abspath(path), times)

  def open(self, path, flags):
    full_path = os.path.abspath(path)
    return os.open(full_path, flags)

  def create(self, path, mode, fi=None):
    full_path = os.path.abspath(path)
    return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

  def read(self, path, length, offset, fh):
    os.lseek(fh, offset, os.SEEK_SET)
    return os.read(fh, length)

  def write(self, path, buf, offset, fh):
    os.lseek(fh, offset, os.SEEK_SET)
    return os.write(fh, buf)

  def truncate(self, path, length, fh=None):
    full_path = os.path.abspath(path)
    with open(full_path, 'r+') as f:
      f.truncate(length)

  def flush(self, path, fh):
    return os.fsync(fh)

  def release(self, path, fh):
    return os.close(fh)

  def fsync(self, path, fdatasync, fh):
    return self.flush(path, fh)
