EmacsTabstops
=============

Better tabstop support for Sublime Text. The whole idea is to enable tabstops to be something other than the indentation tab width. This is invaluable when editing files written in Emacs, where tabstops are 8 spaces, but the indentation tab width might be 2 or 4 spaces.

By default, this plugin will convert all tabs to spaces on load, and convert those regions back to tabs again on save. This behavior lets you edit files with spaces, but keeps the tabs on disk so that whitespace changes don't show up in diffs and the like. To get full emacs behavior where all sets of 8 spaces at the start of a line become tabs, set `emacs_tabstops_all_to_tabs` to true. Conversely, to keep the spaces on save, set `emacs_tabstops_convert_on_save` to "never".

Status
------

Currently beta quality. Things work well enough for the day-to-day, but don't be surprised by small hiccups.

Settings
--------

These settings should be in Prefereces or a project file.

  - `emacs_tabstops_tabstop`: integer number of spaces to substitute. (Default: 8)
  - `emacs_tabstops_convert_on_load`: {true, false} Convert tabs -> spaces on load. Note that no conversion is done if there are no tabs in the file. (Default: true)
  - `emacs_tabstops_convert_on_save`: {'always', 'auto', 'never'} (Default: 'auto')
    + always: always convert spaces -> tabs on save
    + auto: only convert if tabs -> spaces was previously run for this buffer
    + never: don't convert spaces -> tabs on save

    If conversion is done, the tabs are replaced with spaces again after the buffer is saved.
  - `emacs_tabstops_all_to_tabs`: {true, false} When converting to tabs, control whether or not all indentation spaces of tabstop width are converted to tabs. If false, only regions where tabs were converted to spaces are converted back. (Default: false)
  - `emacs_tabstops_skip_filetypes`: List of file types to ignore when loading/saving. You can still call this plugin by hand for these files. (Default: ['Python', 'Cython', 'Makefile', 'Makefile.am'])

Usage
-----

  - Use convert_on_{load,save} settings to do conversions automatically.
  - Commands are available in the pallette as "EmacsTabstops: *"
  - Toggling between tabs and spaces can also be done via the shortcut <`cmd` + `alt` + `tab`>
  - To go only tabs -> spaces, use <`cmd` + `alt` + `shift` + `tab`>

Issues
------

  - No keybindings for Linux/Windows. If you use these platforms and have a natural key combination, submit a pull request :)
  - If the file changes outside of SublimeText and it gets automatically reloaded, there appears to be no way to detect this and re-convert tabs -> spaces. To work around this you'll have to run <`cmd` + `alt` + `shift` + `tab`> by hand.
