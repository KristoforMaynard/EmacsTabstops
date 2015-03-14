# -*- coding: utf-8 -*-
"""Plugin for dealing with Emacs-style tabstops"""

# import sublime
import sublime_plugin

_convert_on_activate = {}
_converted_buffers = {}
_scratch_hack = {}

# expand_tabs {"set_translate_tabs": true}
# unexpand_tabs {"set_translate_tabs": true}
# set_setting {'setting': 'tab_size', 'value': 2}

# def prep_scratch_hack(view):
#     pass

_defaults = {'tabstop': 8,
             'convert_on_save': False,
             'convert_on_load': False,
             'skip_filetypes': ["Python", "Cython"]}

def get_setting(view, key):
    """Get setting from view Prefernces, and fall back on _defaults

    Args:
        view (View): ST View
        key (str): name of setting

    Raises:
        KeyError: if key not in Preferences or _defaults

    Returns:
        Value
    """
    settings = view.settings().get("emacs_tabstops", dict())
    try:
        return settings[key]
    except KeyError:
        return _defaults[key]


class EmacsTabstopsToSpaces(sublime_plugin.TextCommand):
    def run(self, edit, tabstop=None):  # pylint: disable=arguments-differ
        print("to spaces start")
        if tabstop is None:
            tabstop = get_setting(self.view, "tabstop")

        s = " " * tabstop
        last_find = 0
        while True:
            reg = self.view.find('\t', last_find)
            if reg:
                last_find = reg.a
                # print("replacing", reg, reg.a, reg.b)
                self.view.replace(edit, reg, s)
            else:
                break
        print("to spaces done")


class EmacsTabstopsToTabs(sublime_plugin.TextCommand):
    def run(self, edit, tabstop=None):  # pylint: disable=arguments-differ
        ttts = "translate_tabs_to_spaces"
        prev_ttts = self.view.settings().get(ttts)
        self.view.settings().set(ttts, False)

        if tabstop is None:
            tabstop = get_setting(self.view, "tabstop")
        s = " " * tabstop
        last_find = 0
        while True:
            reg = self.view.find(s, last_find)
            if reg:
                last_find = reg.a
                # print("replacing", reg, reg.a, reg.b)
                self.view.replace(edit, reg, '\t')
            else:
                break

        if prev_ttts:
            self.view.settings().set(ttts, True)
        print("to tabs done")


class EmacsTabstopsToggle(sublime_plugin.TextCommand):
    def run(self, edit):
        tabstop = get_setting(self.view, "tabstop")

        print("running with tabstop:", tabstop)

        if self.view.find("\t", 0):
            print("to spaces")
            self.view.run_command("emacs_tabstops_to_spaces",
                                  {"tabstop": tabstop})
        elif self.view.find(" " * tabstop, 0):
            print("to tabs")
            self.view.run_command("emacs_tabstops_to_tabs",
                                  {"tabstop": tabstop})
        else:
            print("no tabstops found")
        return None


class EmacsTabstopsListener(sublime_plugin.EventListener):
    @staticmethod
    def on_pre_save(view):
        buffer_id = view.buffer_id()
        print("@pre_save", buffer_id)
        if get_setting(view, "convert_on_save"):
            print("EmacsTabstops says covnerting on pre save")
            view.run_command("emacs_tabstops_to_tabs")
            # if view.buffer_id() in _converted_buffers:
            #     print("file found:", view.file_name())

    @staticmethod
    def on_post_save(view):
        buffer_id = view.buffer_id()
        print("@post_save", buffer_id)
        if get_setting(view, "convert_on_save"):
            print("EmacsTabstops says covnerting on post save")
            view.run_command("emacs_tabstops_to_spaces")
            # if view.buffer_id() in _converted_buffers:
            #     print("file found:", view.file_name())

    @staticmethod
    def on_load(view):
        buffer_id = view.buffer_id()
        print("@load", buffer_id)
        settings = view.settings().get("emacs_tabstops", dict())
        if settings.get("convert_on_load", False):
            print("EmacsTabstops says covnerting on load")
            _converted_buffers[buffer_id] = True
            if not view.set_scratch():
                view.set_scratch(True)
                _scratch_hack[buffer_id] = True

    # @staticmethod
    # def on_new(view):
    #     print("@new", view.buffer_id())

    # @staticmethod
    # def on_modified(view):
    #     if view.buffer_id() in _scratch_hack:
    #         view.set_scratch(False)
    #         del _scratch_hack[view.buffer_id()]

    @staticmethod
    def on_clone(view):
        buffer_id = view.buffer_id()
        print("@clone", buffer_id)
        if buffer_id in _converted_buffers:
            _converted_buffers[buffer_id] += 1

    @staticmethod
    def on_close(view):
        buffer_id = view.buffer_id()
        print("@close", buffer_id)
        if buffer_id in _convert_on_activate:
            del _convert_on_activate[buffer_id]
        if buffer_id in _converted_buffers:
            _converted_buffers[buffer_id] -= 1
            if _converted_buffers[buffer_id] <= 0:
                del _converted_buffers[buffer_id]

    @staticmethod
    def on_activated(view):
        buffer_id = view.buffer_id()
        print("@activated", buffer_id)
        if buffer_id in _convert_on_activate:
            view.run_command("emacs_tabstops_to_spaces")
            del _convert_on_activate[buffer_id]

##
## EOF
##
