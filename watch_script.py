import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

try:
  import pathspec
except ImportError:
  pathspec = None


def load_gitignore_patterns(gitignore_path=".gitignore"):
  if not pathspec or not os.path.exists(gitignore_path):
    return None
  with open(gitignore_path, "r") as f:
    patterns = f.read().splitlines()
  return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


class RestartOnChangeHandler(PatternMatchingEventHandler):
  def __init__(self, command, ignore_spec=None):
    super().__init__(patterns=["*.py"], ignore_directories=True)
    self.command = command
    self.process = None
    self.ignore_spec = ignore_spec
    self.start_process()

  def should_ignore(self, path):
    # Ignore if in common folders
    ignored_dirs = ["__pycache__", ".venv", "venv", ".git"]
    for d in ignored_dirs:
      if f"{os.sep}{d}{os.sep}" in path or path.endswith(f"{os.sep}{d}"):
        return True

    # Check .gitignore patterns if loaded
    if self.ignore_spec and self.ignore_spec.match_file(path):
      return True

    return False

  def start_process(self):
    print("Starting process:", self.command)
    self.process = subprocess.Popen(self.command, shell=True)

  def restart_process(self):
    print("Restarting process...")
    if self.process:
      self.process.terminate()
      self.process.wait()
    self.start_process()

  def on_modified(self, event):
    if self.should_ignore(event.src_path):
      return
    print(f"Detected change in {event.src_path}")
    self.restart_process()


if __name__ == "__main__":
  command = "python main.py"

  ignore_spec = load_gitignore_patterns()

  event_handler = RestartOnChangeHandler(command, ignore_spec=ignore_spec)
  observer = Observer()
  observer.schedule(event_handler, path=".", recursive=True)
  observer.start()

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()
