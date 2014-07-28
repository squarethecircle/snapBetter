# Copyright 2013 Google Inc. All Rights Reserved.

"""Helper action to create initial contents for .help files.
"""

import argparse
import os
import os.path
import StringIO
import subprocess
import sys
import tempfile
import textwrap


def WriteBashScript(prefix, prompt, subcommands, buf):
  """Write the . file for a bash subshell.

  Args:
    prefix: str, The command line prefix for each of the subcommands.
    prompt: str, The prompt that should appear for the shell.
    subcommands: [str], The different subcommands that should be available.
    buf: writeable, Buffer to store the . file in.
  """

  actual_gcloud = os.path.abspath(sys.argv[0])

  sourcefile = textwrap.dedent("""\
      if [[ -e "$HOME/.bashrc" ]]; then
        source $HOME/.bashrc
      fi
      """)
  buf.write(textwrap.dedent("""\
      # Running bash subshell with the following rcfile...
      {sourcefile}
      """).format(
          sourcefile=sourcefile))

  buf.write(textwrap.dedent("""\
      _python_argcomplete() {{
          local IFS=''
          COMPREPLY=( $(IFS="$IFS" COMP_LINE="$COMP_LINE" COMP_POINT="$COMP_POINT" _ARGCOMPLETE_COMP_WORDBREAKS="$COMP_WORDBREAKS" _ARGCOMPLETE=1 "$1" 8>&1 9>&2 1>/dev/null 2>/dev/null) )
          if [[ $? != 0 ]]; then
              unset COMPREPLY
          fi
      }}
      _prefix_shell='{prefix}'
      _gcloud_shell_argcomplete() {{
          COMP_LINE="$_prefix_shell $COMP_LINE"
          shift
          COMP_POINT=$[$COMP_POINT+${{#_prefix_shell}}]
          _python_argcomplete $_prefix_shell "$@"
      }}
  """).format(prefix=prefix))
  buf.write(textwrap.dedent("""\
      PYTHONPATH={pythonpath}

      function python {{
        {python} "$@"
      }}
      function gcloud {{
        python "{actual_gcloud}" "$@"
      }}
      """).format(
          python=sys.executable,
          pythonpath=':'.join(sys.path),
          actual_gcloud=actual_gcloud))

  for subcommand in subcommands + ['-h', '--help']:
    cmd_func = textwrap.dedent(
        "alias -- '{command}={prefix} {command}'").format(
            command=subcommand, prefix=prefix)
    print cmd_func
    buf.write(cmd_func+'\n')
    if not subcommand.startswith('-'):
      buf.write(textwrap.dedent("""\
          complete -o default -F _gcloud_shell_argcomplete "{command}"
          """).format(command=subcommand,
                      prefix=prefix))
  buf.write("PS1='{prompt} $ '\n".format(prompt=prompt))
  buf.write(textwrap.dedent("""\

      # Type 'exit' or ctrl-d to exit this subshell.
      """))


def ShellAction(subcommands, loader):
  """Get an argparse action that launches a bash subshell.

  Args:
    subcommands: [str], List of the commands and subgroups that will be turned
        into aliases in the subshell.
    loader: calliope.CommandLoader, the CommandLoader hosting this calliope
        session.

  Returns:
    argparse.Action, the action to use.
  """

  class Action(argparse.Action):

    def __init__(self, **kwargs):
      super(Action, self).__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
      alias_args = ['gcloud']

      shell = values or os.environ.get('SHELL', '/bin/bash')
      base_shell = os.path.basename(shell)

      for arg in loader.argv:
        if arg == '--shell' or arg.startswith('--shell='):
          # Only things up to, and not including, the first --shell.
          # TODO(user): This search can have false positives. eg,
          # $ gcloud --project --shell auth --shell
          # If someone somehow had a project "--shell", or if some other flag
          # flag value was legitimately "--shell". For now, we'll let this be
          # a problematic, but rare, corner case.
          break

        # TODO(user): Make this quoting more robust.
        if ' ' in arg:
          arg = '"{arg}"'.format(arg=arg)

        alias_args.append(arg)

      alias_prefix = ' '.join(alias_args)
      prompt = ' '.join(['gcloud']+alias_args[1:])

      buf = StringIO.StringIO()

      with tempfile.NamedTemporaryFile() as f:
        print '# Writing rc file to [{file}].'.format(file=f.name)

        if base_shell == 'bash':
          WriteBashScript(alias_prefix, prompt, subcommands, buf)
        else:
          print ('ERROR: Unknown shell [{shell}]. Known choices are '
                 '[bash].').format(shell=shell)
          sys.exit(1)

        f.write(buf.getvalue())
        f.flush()
        try:
          if base_shell == 'bash':
            print '# Running an interactive bash shell.'
            print '$ {shell} --rcfile "{file}" -i'.format(
                shell=shell, file=f.name)
            print '# Type "exit" or ctrl-d to exit this subshell.'
            subprocess.call([shell, '--rcfile', f.name, '-i'])
          else:
            # This exception should be unreachable.
            raise Exception('UNREACHABLE: unknown shell')
        except OSError as e:
          print e
          print """\
There was a problem running the desired shell. To use this feature, make sure
that [{shell}] is installed and available in your system PATH, or that the
$SHELL environment variable points to the correct program.
""".format(shell=shell)
          sys.exit(1)

      sys.exit(0)

  return Action
