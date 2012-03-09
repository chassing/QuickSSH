
import os
import json
from Tkinter import *
from ttk import *
from subprocess import Popen, PIPE

VERSION = "0.1"


class AppScript(object):
  MAIN_SCRIPT = """
  tell application "%(app)s"
    %(prog)s
  end tell
  """

  def __init__(self, app):
    self._app = app

  def _call(self, prog):
    cmd = Popen(["osascript"], stdin=PIPE)
    cmd.communicate(self.MAIN_SCRIPT % dict(
      app=self._app,
      prog=prog
    ))


class Terminal(AppScript):
  MAC_TERMINAL_SCRIPT = """
    do script "%(sshbin)s %(host)s"
    activate
  """
  MAC_ITERM_SCRIPT = """
    activate
    set newterm to (make new terminal)
    tell newterm
      set newsession to (make new session)
      tell newsession
        exec command "%(sshbin)s %(host)s"
      end tell
    end tell
  """

  def __init__(self):
    super(Terminal, self).__init__(app=CONFIG["settings"]["terminal"])

  def ssh(self, host):
    if self._app == "Terminal":
      SCRIPT = self.MAC_TERMINAL_SCRIPT
    elif self._app == "iTerm":
      SCRIPT = self.MAC_ITERM_SCRIPT
    else:
      raise Exception("unknown terminal")
    self._call(SCRIPT % dict(sshbin=CONFIG["settings"]["sshbin"], host=host))


class Hosts(Treeview):
  def __init__(self, parent, **kwargs):
    Treeview.__init__(self, parent, selectmode="browse", show="tree", **kwargs)
    self.bind('<Double-Button-1>', self.call)
    self.bind('<KeyRelease>', self.call)
    self.column("#0", width=CONFIG["settings"]["window_width"] - 10)

  def call(self, event=None):
    """ execute the highlighted item
    """
    if not event or event.type == "4" or event.keysym in ["Return", "KP_Enter"]:
      host = self.focus()
      Terminal().ssh(host)

  def _select(self, direction):
    select_item = self.focus() if self.focus() else self.get_children()[0]
    i = self.index(select_item)
    childs = self.get_children()
    new_selected_item = childs[(i + direction) % len(childs)]
    self.focus(new_selected_item)
    self.selection_set(new_selected_item)
    self.see(new_selected_item)

  def select_next(self):
    self._select(direction=1)

  def select_prev(self):
    self._select(direction=-1)

  def add(self, obj):
    """ add host item and select the first one
    """
    title = obj["title"] if "title" in obj else obj["host"]
    self.insert('', 'end', "%s@%s" % (obj["user"], obj["host"]), text=CONFIG["settings"]["item_display"] % dict(host=title, user=obj["user"]))
    self.focus(self.get_children()[0])
    self.selection_set(self.get_children()[0])
    self["height"] = len(self.get_children()) if len(self.get_children()) <= 10 else 10

  def clear(self):
    for item in self.get_children():
      self.delete(item)


class App(object):

  def __init__(self, parent):
    self.parent = parent
    frame = Frame(parent)
    frame.pack(padx=0, pady=5)

    self.search = Entry(frame, width=int(CONFIG["settings"]["window_width"] / 8.3))
    self.search.grid(row=0)
    self.search.focus_force()
    self.search.bind('<KeyRelease>', self.search_callback)

    self.result = Hosts(frame)
    self.result.grid(row=1)
    self.result.grid_remove()

    self.hosts = CONFIG["hosts"]

  def quit(self):
    sys.exit(0)

  def search_callback(self, event=None):
    if event.keysym == "Down":
      self.result.select_next()

    elif event.keysym == "Up":
      self.result.select_prev()

    elif event.keysym in ["Return", "KP_Enter"]:
      self.result.call()
      self.quit()

    elif event.keysym == "Escape":
      self.quit()

    else:
      # remove results
      self.result.clear()
      self.result.grid_remove()

      # parse input
      query = self.search.get().strip().split()

      if not query:
        # search is empty
        center_window(self.parent)
        return

      # layout results
      self.result.grid()

      # search for query
      for host in self.hosts:
        field = host["host"]

        if "title" in host:
          field = host["title"]

        if field.find(query[0]) > -1:
          self.result.add(host)

      # split query; first is host, second is use
      host = query[0]
      user = "root"
      if len(query) > 1:
        user = query[1]

      # add query as host too
      self.result.add({
        "host": host,
        "title": host,
        "user": user,
      })

      # resize main window
      window_height = CONFIG["settings"]["window_height"] + len(self.result.get_children()) * 20
      if window_height > 230:
        window_height = 230
      center_window(self.parent, height=window_height)


def center_window(root, width=None, height=None):
  if not width:
    width = CONFIG["settings"]["window_width"]
  if not height:
    height = CONFIG["settings"]["window_height"]
  screen_width = root.winfo_screenwidth()
  screen_height = root.winfo_screenheight()
  # center the window
  x = int(screen_width / 2 - width / 2)
  y = int(screen_height / 4)
  root.geometry('%dx%d+%d+%d' % (width, height, x, y))


if __name__ == '__main__':

  CFG = os.path.join(os.environ["HOME"], ".quick_ssh.json")

  try:
    CONFIG = json.loads(open(CFG).read())
  except:
    # read config failed; get default config and write config file
    CONFIG = dict(
      settings=dict(
        terminal="Terminal",
        sshbin="/usr/bin/ssh",
        window_width=400,
        window_height=40,
        item_display="%(host)s as user %(user)s"
      ),
      hosts=[
        dict(
          host="host.example.com",
          user="root",
          title="use title instead of host; optional"
        ),
        dict(
          host="host2.example.com",
          user="other_user",
        ),
      ]
    )
    open(CFG, "w").write(json.dumps(CONFIG, indent=2))

  root = Tk()
  root.title('QuickSSH')
  root.resizable(0, 0)
  center_window(root)
  app = App(root)
  root.mainloop()
