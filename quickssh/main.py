
import os
import json
from Tkinter import *
from ttk import *


CFG = os.path.join(os.environ["HOME"], ".quick_ssh.json")
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 40


class Hosts(Treeview):
  def __init__(self, parent, **kwargs):
    Treeview.__init__(self, parent, selectmode="browse", show="tree", **kwargs)
    self.bind('<Double-Button-1>', self.call)
    self.bind('<KeyRelease>', self.call)
    self.column("#0", width=390)

  def call(self, event=None):
    if not event or event.type == "4" or event.keysym in ["Return", "KP_Enter"]:
      print self.focus()

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
    title = obj["title"] if "title" in obj else obj["host"]
    self.insert('', 'end', "%s@%s" % (obj["user"], obj["host"]), text="%s as user '%s'" % (title, obj["user"]))
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

    self.search = Entry(frame, width=48)
    self.search.grid(row=0)
    self.search.focus_force()
    self.search.bind('<KeyRelease>', self.search_callback)

    self.result = Hosts(frame)
    self.result.grid(row=1)
    self.result.grid_remove()

    fcfg = open(CFG, "r")
    self.hosts = json.load(fcfg)
    fcfg.close()

  def search_callback(self, event=None):
    if event.keysym == "Down":
      self.result.select_next()
    elif event.keysym == "Up":
      self.result.select_prev()
    elif event.keysym in ["Return", "KP_Enter"]:
      self.result.call()
    else:
      self.result.clear()
      self.result.grid_remove()

      if not self.search.get():
        center_window(self.parent)
        return

      for host in self.hosts:
        self.result.grid()

        field = host["host"]

        if "title" in host:
          field = host["title"]

        if field.find(self.search.get()) > -1:
          self.result.add(host)

      self.result.add({
        "host": self.search.get(),
        "title": self.search.get(),
        "user": "root",
      })

      # resize main window
      window_height = WINDOW_HEIGHT + len(self.result.get_children()) * 20
      if window_height > 230:
        window_height = 230
      center_window(self.parent, height=window_height)


def center_window(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
  screen_width = root.winfo_screenwidth()
  screen_height = root.winfo_screenheight()
  # center the window
  x = int(screen_width / 2 - width / 2)
  y = int(screen_height / 2 - height / 2)
  root.geometry('%dx%d+%d+%d' % (width, height, x, y))


if __name__ == '__main__':
  root = Tk()
  root.title('QuickSSH')
  root.resizable(0, 0)
  #root.overrideredirect(True)
  center_window(root)
  app = App(root)
  root.mainloop()
