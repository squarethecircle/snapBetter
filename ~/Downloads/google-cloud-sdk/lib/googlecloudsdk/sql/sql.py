# Copyright 2013 Google Inc. All Rights Reserved.

"""This file can be executed directly to run the CLI or loaded as a module.
"""
import os

from googlecloudsdk.core import cli

_loader = cli.CLIFromConfig(
    os.path.join(cli.GoogleCloudSDKPackageRoot(), 'sql', 'sql.yaml'))

sql = _loader.EntryPoint()


def main():
  _loader.Execute()

if __name__ == '__main__':
  main()
