# -*-coding: utf-8 -*-
# Created by samwell
import os
import time
import subprocess
from enum import Enum

import win32service

# if getattr(sys, 'frozen', False):
#     # we are running in a bundle
#     bundle_dir = sys._MEIPASS    C:\Users\atten\AppData\Local\Temp\_MEI1093962
#     sys.argv[0]                  qdir.exe
#     sys.executable               D:\ChruchProjects\regbook\regbsvr\qdir.exe
#     os.getcwd()                  D:\ChruchProjects\regbook\regbsvr
# else:
#     # we are running in a normal Python environment
#     bundle_dir = os.path.dirname(os.path.abspath(
#         __file__))               D:\ChruchProjects\regbook\regbsvr
#     sys.argv[0]                  qdir.py
#     sys.executable               D:\ChruchProjects\regbook\venv\Scripts\python.exe
#     os.getcwd()                  D:\ChruchProjects\regbook\regbsvr

mongo_dir = os.path.join(os.getcwd(), 'db')
mongo_exe = os.path.join(mongo_dir, 'mongod.exe')
mongo_data_dir = os.path.join(mongo_dir, 'data')
mongo_log_dir = os.path.join(mongo_dir, 'log')
mongo_log_file = os.path.join(mongo_log_dir, 'db.log')

serviceName = 'regbooksvc'
displayName = 'MongoDB Service For RegBook'
binaryPathName = f'"{mongo_exe}" --auth --bind_ip_all --dbpath "{mongo_data_dir}" --logpath "{mongo_log_file}" --service'

firewallName = 'MongoDB Service For RegBook'

pws_firewall_add = f"powershell New-NetFirewallRule -DisplayName '{firewallName}' -Direction Inbound -Program '{mongo_exe}' -Action Allow"
pws_firewall_del = f"powershell Remove-NetFirewallRule -DisplayName '{firewallName}'"


class SvcStatus(Enum):
    NO_EXIST = 1
    STOPPED = 2
    RUNNING = 3
    PAUSED = 4


class SvcEntity(object):
    @classmethod
    def GetSvcEntity(cls):
        if not os.path.isfile(mongo_exe):
            raise RuntimeError(f'File not exist: {mongo_exe}')
        if not os.path.isdir(mongo_data_dir):
            raise RuntimeError(f'Directory not exist: {mongo_data_dir}')
        if not os.path.isdir(mongo_log_dir):
            raise RuntimeError(f'Directory not exist: {mongo_log_dir}')
        return cls()

    def __init__(self):
        self.scmHandle = None
        self.scmHandle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)

    def __del__(self):
        if self.scmHandle:
            win32service.CloseServiceHandle(self.scmHandle)

    def _trans_txt(self, out):
        if not out:
            return ''
        try:
            return out.decode(encoding='utf8')
        except UnicodeDecodeError:
            try:
                return out.decode(encoding='utf16')
            except UnicodeDecodeError:
                return out.decode(encoding='gbk')

    def _run_pws(self, cmd):
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            outs = self._trans_txt(result.stdout)
            errs = self._trans_txt(result.stderr)
            raise RuntimeError(f"PowerShell: return {result.returncode}\nOut: {outs}\nErr: {errs}")

    def _add_firewall(self):
        self._del_firewall()
        self._run_pws(pws_firewall_add)

    def _del_firewall(self):
        try:
            self._run_pws(pws_firewall_del)
        except Exception:
            pass

    def _is_exist(self):
        scvs = win32service.EnumServicesStatus(self.scmHandle,
                                               win32service.SERVICE_WIN32,
                                               win32service.SERVICE_STATE_ALL)
        for sname, sdisname, status in scvs:
            if sname == serviceName:
                return True
        return False

    def _query(self, svcHandle):
        """
        waiting service stable, and query service status.
        """
        status = win32service.QueryServiceStatus(svcHandle)
        while status[1] in (win32service.SERVICE_START_PENDING,
                            win32service.SERVICE_STOP_PENDING,
                            win32service.SERVICE_PAUSE_PENDING,
                            win32service.SERVICE_CONTINUE_PENDING):
            time.sleep(0.01)
            status = win32service.QueryServiceStatus(svcHandle)
        return status[1]

    def _start(self, svcHandle):
        status_code = self._query(svcHandle)

        if status_code == win32service.SERVICE_STOPPED:
            win32service.StartService(svcHandle, None)
        elif status_code == win32service.SERVICE_PAUSED:
            win32service.ControlService(svcHandle, win32service.SERVICE_CONTROL_CONTINUE)
        else:  # SERVICE_RUNNING
            pass
        return self._query(svcHandle)

    def _stop(self, svcHandle):
        status_code = self._query(svcHandle)
        if status_code == win32service.SERVICE_PAUSED:
            status_code = self._start(svcHandle)
        if status_code == win32service.SERVICE_RUNNING:
            win32service.ControlService(svcHandle, win32service.SERVICE_CONTROL_STOP)
        return self._query(svcHandle)

    def start(self):
        svcHandle = None
        try:
            svcHandle = win32service.OpenService(
                self.scmHandle,
                serviceName,
                win32service.SERVICE_ALL_ACCESS)

            status_code = self._start(svcHandle)
            if status_code != win32service.SERVICE_RUNNING:
                raise RuntimeError(f'Start service failed, status{status_code}.')
        finally:
            if svcHandle:
                win32service.CloseServiceHandle(svcHandle)

    def stop(self):
        svcHandle = None
        try:
            svcHandle = win32service.OpenService(
                self.scmHandle,
                serviceName,
                win32service.SERVICE_ALL_ACCESS)

            status_code = self._stop(svcHandle)
            if status_code != win32service.SERVICE_STOPPED:
                raise RuntimeError(f'Start service failed, status{status_code}.')
        finally:
            if svcHandle:
                win32service.CloseServiceHandle(svcHandle)

    def query(self):
        svcHandle = None
        try:
            try:
                svcHandle = win32service.OpenService(
                    self.scmHandle,
                    serviceName,
                    win32service.SERVICE_ALL_ACCESS)
            except Exception:
                if not self._is_exist():
                    return SvcStatus.NO_EXIST
                raise
            status_code = self._query(svcHandle)
            if status_code == win32service.SERVICE_STOPPED:
                return SvcStatus.STOPPED
            elif status_code == win32service.SERVICE_RUNNING:
                return SvcStatus.RUNNING
            else:
                return SvcStatus.PAUSED
        finally:
            if svcHandle:
                win32service.CloseServiceHandle(svcHandle)

    def install(self):
        svcHandle = None
        try:
            svcHandle = win32service.CreateService(
                self.scmHandle,
                serviceName,
                displayName,
                win32service.SERVICE_ALL_ACCESS,  # desired access
                win32service.SERVICE_WIN32_OWN_PROCESS,
                win32service.SERVICE_DEMAND_START,
                win32service.SERVICE_ERROR_IGNORE,
                binaryPathName,
                None,
                0,
                None,
                "NT AUTHORITY\\NetworkService",
                None)
            win32service.CloseServiceHandle(svcHandle)
            # must reopen service or get error
            svcHandle = win32service.OpenService(
                self.scmHandle,
                serviceName,
                win32service.SERVICE_ALL_ACCESS)

            status_code = self._start(svcHandle)
            if status_code != win32service.SERVICE_RUNNING:
                raise RuntimeError(f'Start service failed, status{status_code}.')

            self._add_firewall()

        finally:
            if svcHandle:
                win32service.CloseServiceHandle(svcHandle)

    def remove(self):
        svcHandle = None
        try:
            svcHandle = win32service.OpenService(
                self.scmHandle,
                serviceName,
                win32service.SERVICE_ALL_ACCESS)

            self._stop(svcHandle)

            win32service.DeleteService(svcHandle)

            self._del_firewall()
        finally:
            if svcHandle:
                win32service.CloseServiceHandle(svcHandle)

