EmacsTabstops
=============

SublimeText plugin for dealing with source files that use Emacs' silly '8 spaces becomes a tab' behavior when the indentation of a file is some other number.

By default, this plugin will convert tabs at the start of lines to `tabstop` number of spaces on load. Then, on save, `tabstop` number of spaces at the start of lines will be replaced with tab characters again. The idea being that the file will look right while you edit it, but the tabs -> spaces won't be saved back to the file. This keeps the war between tabs and spaces out of diffs.

This is not a replacement for tabstop support in Sublime Text since only tabs at the start of lines are converted. The reason for this is once tabs are converted to spaces, there's no straight forward way to keep track of 8 spaces in a line and 8 spaces that came from a tab character.

Settings
--------

These settings should be in Prefereces or a project file.

  - `emacs_tabstops_tabstop`: integer number of spaces to substitute. (Default: 8)
  - `emacs_tabstops_convert_on_load`: {true, false} Convert tabs -> spaces on load. Note that no conversion is done if there are no tabs in the file. (Default: true)
  - `emacs_tabstops_convert_on_save`: {'always', 'auto', 'never'}
    + always: always convert spaces -> tabs on save
    + auto: only convert if tabs -> spaces was previously run for this buffer
    + never: don't convert spaces -> tabs on save
    If conversion is done, the tabs are replaced with spaces again after the buffer is saved. (Default: 'never')
  - `emacs_tabstops_skip_filetypes`: List of file types to ignore when loading/saving. You can still call this plugin by hand for these files. (Default: ['Python', 'Cython'])

Usage
-----

  - Use convert_on_{load,save} to do conversions automatically.
  - Available in the command pallette as "EmacsTabstops: Toggle Tabs/Spaces"
  - Toggling between tabs and spaces can also be done via the shortcut <`cmd` + `alt` + `tab`>
  - To go only tabs -> spaces, use <`cmd` + `alt` + `shift` + `tab`>

Issues
------

  - If the file changes outside of SublimeText and it gets automatically reloaded, there appears to be no way to detect this and re-convert tabs -> spaces. To work around this you'll have to run <`cmd` + `alt` + `shift` + `tab`> by hand.
