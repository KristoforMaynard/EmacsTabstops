EmacsTabstops
=============

Work in Progress

SublimeText plugin for dealing with source files that use Emacs' silly 8 spaces becomes a tab "feature".

Features
--------

  - Convert between 8 spaces and tabs in the same way that emacs does

Settings
--------

These settings should be added to a set called "emacs_tabstops" in Prefereces, or a project file.

  - `tabstop`: integer number of spaces to substitute. (Default: 8)
  - `convert_on_load`: {true, false} Convert tabs to spaces on load. An unavoidable side-effect is that files always look dirty. (Default: false)
  - `convert_on_save`: {true, false} If the file had tabs on load, convert tabstop -> tabs just before saving. Then convert the tabs back to spaces so you can continue editing. (Default: false)
  - `skip_filetypes`: List of file types to ignore when loading/saving. You can still call this plugin by hand for these files. (Default: ['Python', 'Cython'])

  Example::
    "emacs_tabstops": {
      "tabstop": 8,
      "convert_on_load": true,
      "convert_on_save": true,
      "skip_filetypes": ["Python", "Cython"]
    }

Usage
-----

  - Use convert_on_{load,save} to do conversions automatically.
  - Available in the command pallette as "EmacsTabstops: Toggle Tabs/Spaces"
  - Toggling between tabs and spaces can also be done via the shortcut <`cmd` + `alt` + `tab`>
