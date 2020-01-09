# -- coding: utf-8 --

import os
import time
import zipfile

from subprocess import Popen, PIPE

DEFAULT_CONFIG_FILE = 'config.json'


class MysqlDump(object):
    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = password
        for key, value in kwargs.items():
            setattr(self, key, value)

    def exec_cmd(self, commands):
        p = Popen(commands, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        ret = p.communicate()
        if p.returncode == 0:
            return ret[0]
        else:
            raise ValueError(str(ret[0] + ret[1] + b'backup error'))

    def make_cmd(self):
        commands = list()
        commands.append('mysqldump.exe')
        commands.append('--user={0}'.format(self.username))
        commands.append('--host={0}'.format(getattr(self, 'hostname', 'localhost')))
        commands.append('--port={0}'.format(getattr(self, 'port', '3306')))
        commands.append('--protocol={0}'.format(getattr(self, 'protocol', 'tcp')))
        commands.append('--password={0}'.format(self.password))
        defaults_file = getattr(self, 'defaults_file', None)
        if defaults_file is not None:
            print(defaults_file)
            commands.append('--defaults-file={0}'.format(defaults_file))
        commands.append('--default-character-set={0}'.format(getattr(self, 'default_character_set', 'utf8')))
        commands.append('--skip-triggers')
        commands.append('{0}'.format(getattr(self, 'schemas', '')))
        return commands

    @staticmethod
    def _save_data(sql_data):
        localtime = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        filename = '{0}.sql'.format(localtime)
        backup_path = os.path.join(os.path.abspath(os.path.curdir), 'backup')
        if not os.path.isdir(backup_path):
            os.mkdir(backup_path)
        _file = os.path.join(backup_path, filename)
        with open(_file, 'wb+') as f:
            f.write(sql_data)
        zip_file = '{0}.zip'.format(_file)
        old_dir = os.getcwd()
        os.chdir(backup_path)
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_LZMA) as z:
            z.write(filename)
        os.remove(_file)
        os.chdir(old_dir)

    def backup(self):
        commands = self.make_cmd()
        sql_data = self.exec_cmd(commands)
        self._save_data(sql_data)


def backup(*args, **kwargs):
    mysql_dump = MysqlDump(**kwargs)
    try:
        mysql_dump.backup()
        print('backup successed')
    except ValueError as e:
        print(str(e))
