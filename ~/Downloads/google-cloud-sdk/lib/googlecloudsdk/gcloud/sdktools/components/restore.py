# Copyright 2013 Google Inc. All Rights Reserved.

"""The command to restore a backup of a Cloud SDK installation."""

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import config
from googlecloudsdk.core.updater import update_manager


class Restore(base.Command):
  """Command to restore a backup of a Cloud SDK installation.

  Restore the state of the Cloud SDK as it was before the most recent components
  update, or removal. Can only backtrack one step.
  """

  @staticmethod
  def Args(_):
    pass

  def Run(self, unused_args):
    """Runs the list command."""

    manager = self.context[config.CLOUDSDK_UPDATE_MANAGER_KEY]
    try:
      manager.Restore()
    except update_manager.Error:
      raise exceptions.ToolException.FromCurrent()
