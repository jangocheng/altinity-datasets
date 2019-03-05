#!/usr/bin/env python3

import argparse
import glob
import os
import re
import subprocess
import sys
import time

class ProcessPool:
    """Service for executing processes in parallel"""
    def __init__(self, size=5, dry_run=None):
        """Instantiate a new pool
        :param size: (int): Number of concurrent processes to run
        :param dry_run: (boolean): If true just show what we would run
        """
        self.size = size
        self.slots = []
        self.outputs = []
        if dry_run is None:
            self.dry_run = False
        else:
            self.dry_run = dry_run

    def exec(self, command):
        """Submit a command for execution, blocking if pool is full
        :param command: (str): Shell command to execute
        """
        if len(self.slots) >= self.size:
            self._wait()
        if self.dry_run:
            print("Dry run: " + command)
        else:
            print("Starting a new process: " + command)
            process = subprocess.Popen(command, shell=True)
            self.slots.append(process)

    def drain(self):
        """Wait for all pending commands to finish"""
        while len(self.slots) > 0:
            self._wait()

    def _wait(self):
        print("Waiting for command to finish")
        cur_len = len(self.slots)
        while cur_len > 0 and cur_len == len(self.slots):
            for p in self.slots:
                status = p.poll()
                if status is None:
                    time.sleep(1)
                elif status == 0:
                    print("Process completed: {}".format(p.args))
                    self.outputs.append(status)
                    self.slots.remove(p)
                    break
                else:
                    print("Process failed: {}".format(p.args))
                    self.outputs.append(status)
                    self.slots.remove(p)
                    break