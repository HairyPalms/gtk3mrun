#!/usr/bin/python
from gi.repository import Gtk
from subprocess import Popen
import os, shlex, cairo

#color & alpha values
r = .19
g = .46
b = .75
a = 0.3

class Gmrun:
	def __init__(self):
		self.historyindex = 0
		self.configfile = os.path.join(os.path.expanduser('~'), '.gmrunhistory')

		builder = Gtk.Builder()
		builder.add_from_file('gmrun.glade')
		builder.connect_signals(self)

		window = builder.get_object('gmrunwin')
		self.autocomplete = builder.get_object('autocompletemodel')
		completion = builder.get_object('autocompletebuffer')

		self.temparray = []
		if os.path.exists(self.configfile):
			f = open(self.configfile, 'r')
			for line in f:
				self.temparray.append(line.strip())
			f.close()

			for key in self.temparray:
				self.autocomplete.append([key])

		usrbinarray = {}
		for filename in os.listdir("/usr/bin"):
			if os.path.isfile(os.path.join("/usr/bin",filename)):
				usrbinarray[filename] = 1

		for key in usrbinarray.iterkeys():
			self.autocomplete.append([key])

		completion.set_text_column(0)

		window.connect('key_press_event', self.check_key)
		window.connect("destroy",Gtk.main_quit)

		#sexy cairo goodness
		screen = window.get_screen()
		visual = screen.get_rgba_visual()
		if visual != None and screen.is_composited():
			window.set_visual(visual)
			window.set_app_paintable(True)
			window.connect("draw", self.area_draw)

		window.show_all()

	def check_key(self, widget, event):
		entry = widget.get_child()
		if event.keyval == 65362:# = up
			self.up_pressed(entry)
		elif event.keyval == 65364:# = down
			self.down_pressed(entry)
		elif event.keyval == 65293 and (entry.get_text().replace(' ', '') != ''):
			args = shlex.split(entry.get_text())
			try: 
				pid = Popen(args).pid
				f = open(self.configfile, 'w')
				for value in self.temparray:
					f.write(value + '\n')
				f.write(entry.get_text())
				f.close()
				Gtk.main_quit()
			except: 
				#try with bash incase its a shell script
				args.insert(0,"bash")
				pid = Popen(args).pid
				f = open(self.configfile, 'w')
				for value in self.temparray:
					f.write(value + '\n')
				f.write(entry.get_text())
				f.close()
				Gtk.main_quit()
		elif event.keyval == 65307:
			Gtk.main_quit()

	def up_pressed(self, entry):
		if len(self.temparray) != 0:
			if self.historyindex < len(self.temparray)-1:
				self.historyindex = self.historyindex + 1
			entry.set_text(self.temparray[self.historyindex])

	def down_pressed(self, entry):
		if len(self.temparray) != 0:
			if self.historyindex > 0:
				self.historyindex = self.historyindex - 1
			entry.set_text(self.temparray[self.historyindex])

	def area_draw(self, widget, cr):
		cr.set_source_rgba(r,g,b,a)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)

import sys
import fcntl
LOCK_PATH = os.path.join(os.path.expanduser('~'), '.pygmrun3lock')
fd = open(LOCK_PATH, 'w')
fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
Gmrun()
Gtk.main()

