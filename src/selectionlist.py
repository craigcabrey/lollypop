#!/usr/bin/python
# Copyright (c) 2014 Cedric Bellegarde <gnumdk@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# Many code inspiration from gnome-music at the GNOME project

from gi.repository import Gtk, GObject, Pango

from lollypop.database import Database
from lollypop.utils import translate_artist_name

class SelectionList(GObject.GObject):

	__gsignals__ = {
		'item-selected': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
	}

	"""
		Init Selection list ui
	"""
	def __init__(self, title, width):
		GObject.GObject.__init__(self)
		
		self._model = Gtk.ListStore(int, str)

		self._view = Gtk.TreeView(self._model)
		self._view.connect('cursor-changed', self._new_item_selected)
		renderer = Gtk.CellRendererText()
		renderer.set_fixed_size(width, -1)
		renderer.set_property('ellipsize-set',True)
		renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
		self._view.append_column(Gtk.TreeViewColumn(title, renderer, text=1))
		self._view.set_headers_visible(False)
		self._view.show()

		self.widget = Gtk.ScrolledWindow()
		self.widget.set_vexpand(True)
		self.widget.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		self.widget.add(self._view)
	
	"""
		Populate view with values
		Translate string if is_artist = True
	"""	
	def populate(self, values, is_artist = False):
		self._model.clear()
		for (object_id, string) in values:
			if is_artist:
				string = translate_artist_name(string)
			self._model.append([object_id, string])
				
	
	"""
		Update view with values
		Translate string if is_artist = True
	"""	
	def update(self, values, is_artist = False):
		(path, column) = self._view.get_cursor()
		if path:
			rowiter = self._model.get_iter(path)
			selected_id = self._model.get_value(rowiter, 0)

		selected_iter = None
		for row in self._model:
			if row[0] != selected_id:
				self._model.remove(row.iter)
			else:
				selected_iter = row.iter
		
		before = True
		rowiter = selected_iter
		for object_id, string in values:
				if is_artist:
					string = translate_artist_name(string)
				if object_id == selected_id:
					rowiter = selected_iter
					before = False
					# Force string update if changed
					self._model.set_value(rowiter, 1, string)
					continue
				if before:
					self._model.insert_before(rowiter, [object_id, string])
				else:
					rowiter = self._model.insert_after(rowiter, [object_id, string])

		# Remove selected if unavailable
		if before:
			self._model.remove(selected_iter)

	"""
		Make treeview select first default item
	"""
	def select_first(self):
		iterator = self._model.get_iter("0")
		path = self._model.get_path(iterator)
		self._view.set_cursor(path, None, False)

#######################
# PRIVATE             #
#######################

	"""
		Forward "cursor-changed" as "item-selected" with item id as arg
	"""	
	def _new_item_selected(self, view):
		(path, column) = view.get_cursor()
		if path:
			iter = self._model.get_iter(path)
			if iter:
				self.emit('item-selected', self._model.get_value(iter, 0))

