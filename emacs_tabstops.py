# -*- coding: utf-8 -*-
"""Plugin for dealing with Emacs-style tabstops"""

import sublime
import sublime_plugin


_scratch_listener = None  # will be an instance of EmacsTabstopsScratchListener
_reset_listener = None  # will be an instance of EmacsTabstopsResetListener

PREFIX = "_emacs_tabstops"
S_SCRATCH_HACK = PREFIX + "_scratch_hack"
S_RESET_HACK = PREFIX + "_reset_hack"
S_CONVERTED_TO = PREFIX + "_converted_to"  # {'tabs', 'spaces'}
S_INLINE_TABS = PREFIX + "_inline_tabs"  # {'tabs', 'spaces'}
S_TTS_ON_PS = PREFIX + "_tts_on_ps"  # tabs to spaces on post save flag
S_TTS_ON_ACTIVATE = PREFIX + "_tts_on_activate"  # run tabs to spaces next activate

_defaults = {'emacs_tabstops_tabstop': 8,
             'emacs_tabstops_convert_on_save': 'auto',
             'emacs_tabstops_convert_on_load': True,
             'emacs_tabstops_skip_filetypes': ["Python", "Cython"]}


def plugin_loaded():
    global _scratch_listener, _reset_listener  # pylint: disable=global-statement

    for p in plugins:  # pylint: disable=undefined-variable
        if isinstance(p, EmacsTabstopsScratchListener):
            _scratch_listener = p
        elif isinstance(p, EmacsTabstopsResetListener):
            _reset_listener = p
    if _scratch_listener is None or _reset_listener is None:
        raise RuntimeError("ST API changed in a way that breaks "
                           "EmacsTabstops plugin")
    _scratch_listener.try_to_remove_handler(S_SCRATCH_HACK, "on_modified")
    _reset_listener.try_to_remove_handler(S_RESET_HACK, "on_modified")

def erase_all_state():
    for window in sublime.windows():
        for view in window.views():
            erase_state(view.settings())

def erase_state(settings):
    settings.erase(S_SCRATCH_HACK)
    settings.erase(S_RESET_HACK)
    settings.erase(S_CONVERTED_TO)
    settings.erase(S_INLINE_TABS)
    settings.erase(S_TTS_ON_PS)
    settings.erase(S_TTS_ON_ACTIVATE)

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
    setting = view.settings().get(key, None)
    if setting is None:
        setting = _defaults[key]
    return setting

def set_scratch_hack(view):
    view.settings().set(S_SCRATCH_HACK, True)
    view.set_scratch(True)
    # print("set scratch hack")
    _scratch_listener.add_handler("on_modified")

def find_iter(view, search_txt, skip=None, advance=True):
    last_find = 0
    while True:
        reg = view.find(search_txt, last_find)
        if reg:
            if advance == True:
                last_find = reg.b
            elif advance == False:
                last_find = reg.a
            else:
                last_find = reg.a + advance

            if skip is not None and skip(view, reg.a):
                # print("skipping on: ", view.substr(view.line(reg)))
                # always advance, lest we get stuck in an infinite loop
                last_find = reg.b
                continue
            else:
                yield reg
        else:
            break

def skip_inline(view, point):
    """Return True si il y a text between start of line and point"""
    line_reg = view.line(point)
    line = view.substr(sublime.Region(line_reg.a, point)).strip()
    if line == "":
        return False
    else:
        return True

def iter_indentation_tabs(view, advance=True):
    return find_iter(view, r"\t", skip=skip_inline, advance=advance)

def iter_indentation_spaces(view, tabstop, advance=True):
    s = " " * tabstop
    return find_iter(view, s, skip=skip_inline, advance=advance)

def any_indentation_tabs_exist(view):
    try:
        next(iter_indentation_tabs(view))
        return True
    except StopIteration:
        return False

def any_indentation_spaces_exist(view, tabstop):
    try:
        next(iter_indentation_spaces(view, tabstop))
        return True
    except StopIteration:
        return False


class FriendlyTextCommand(sublime_plugin.TextCommand):
    _success_msg = ""
    _failed_msg = "EmacsTabstops command failed :-( See console for details."

    def run(self, edit, *args, **kwargs):
        try:
            ret = self._friendly_run(edit, *args, **kwargs)
            if self._success_message:
                sublime.status_message(self._success_msg)
            return ret
        except:
            sublime.status_message(self._failed_msg)
            raise

class EmacsTabstopsToSpaces(FriendlyTextCommand):
    def _friendly_run(self, edit, tabstop=None):
        settings = self.view.settings()
        was_clean = not self.view.is_dirty()

        if tabstop is None:
            tabstop = get_setting(self.view, "emacs_tabstops_tabstop")
        s = " " * tabstop

        n_found = 0
        for reg in iter_indentation_tabs(self.view, False):
            self.view.replace(edit, reg, s)
            n_found += 1

        if n_found:
            settings.set(S_CONVERTED_TO, "spaces")
            if was_clean:
                sublime.set_timeout(lambda: set_scratch_hack(self.view), 0)
        # print("to spaces done")


class EmacsTabstopsToTabs(FriendlyTextCommand):
    def _friendly_run(self, edit, tabstop=None):
        settings = self.view.settings()
        was_clean = not self.view.is_dirty()
        ttts = "translate_tabs_to_spaces"
        prev_ttts = settings.get(ttts)
        self.view.settings().set(ttts, False)

        tabstop = get_setting(self.view, "emacs_tabstops_tabstop")
        n_found = 0
        for reg in iter_indentation_spaces(self.view, tabstop, False):
            self.view.replace(edit, reg, '\t')
            n_found += 1

        if n_found:
            settings.set(S_CONVERTED_TO, "tabs")
            if was_clean:
                sublime.set_timeout(lambda: set_scratch_hack(self.view), 0)
        if prev_ttts:
            self.view.settings().set(ttts, True)
        # print("to tabs done")


class EmacsTabstopsToggle(sublime_plugin.TextCommand):
    def run(self, edit):
        tabstop = get_setting(self.view, "emacs_tabstops_tabstop")

        if any_indentation_tabs_exist(self.view):
            # print("to spaces")
            self.view.run_command("emacs_tabstops_to_spaces",
                                  {"tabstop": tabstop})
        elif any_indentation_spaces_exist(self.view, tabstop):
            # print("to tabs")
            self.view.run_command("emacs_tabstops_to_tabs",
                                  {"tabstop": tabstop})
        else:
            # print("no indendation tabstops found")
            pass

        return None


class DynamicListener(sublime_plugin.EventListener):
    def add_handler(self, action):
        if not self in sublime_plugin.all_callbacks[action]:
            sublime_plugin.all_callbacks[action].append(self)
        else:
            # print("handler already there")
            pass

    def remove_handler(self, action):
        for i, c in enumerate(sublime_plugin.all_callbacks[action]):
            if c is self:
                sublime_plugin.all_callbacks[action].pop(i)
                return True
        # print("warning: overusing try_to_remove_handler:", self, action)
        return False

    def try_to_remove_handler(self, setting_name, action):
        # do any views have a setting_name?
        for window in sublime.windows():
            for view in window.views():
                if view.settings().get(setting_name, None):
                    # print("still needed by view:", view.id())
                    return False
        # if we're here, remove the handler
        # nobody else has setting, so nobody needs the listener, but the
        # listener wasn't in all_callbacks anyway
        return self.remove_handler(action)


class EmacsTabstopsScratchListener(DynamicListener):
    def on_modified(self, view):
        # print("@modified (scratch hack)", view.id(), view.buffer_id())
        # if buffer_id in _scratch_hack:
        if view.settings().get(S_SCRATCH_HACK, None):
            # print("unsetting scratch hack")
            view.set_scratch(False)
            view.settings().erase(S_SCRATCH_HACK)
            self.try_to_remove_handler(S_SCRATCH_HACK, "on_modified")

    def on_close(self, view):
        # print("@close (scratch hack)", view.id(), view.buffer_id())
        if view.settings().get(S_SCRATCH_HACK, None):
            def _callback():
                self.try_to_remove_handler(S_SCRATCH_HACK, "on_modified")
            sublime.set_timeout(_callback, 0)


class EmacsTabstopsResetListener(DynamicListener):
    def on_modified(self, view):
        # print("@modified (reset hack)", view.id(), view.buffer_id())
        if view.settings().get(S_RESET_HACK, None):
            view.settings().erase(S_RESET_HACK)
            view.run_command("emacs_tabstops_to_spaces")
            self.remove_handler("on_modified")

    def on_text_command(self, view, command_name, args):  # pylint: disable=unused-argument
        # print("@text command (reset hack)", view.id(), view.buffer_id())
        if command_name == "revert":
            # print("...revert...")
            erase_state(view.settings())
            if get_setting(view, "emacs_tabstops_convert_on_load"):
                def run_tts_callback():
                    # print("tts_callback")
                    view.settings().set(S_RESET_HACK, True)
                    self.add_handler("on_modified")
                sublime.set_timeout(run_tts_callback, 0)

    def on_close(self, view):
        # print("@close (reset hack)", view.id(), view.buffer_id())
        if view.settings().get(S_RESET_HACK, None):
            def _callback():
                self.try_to_remove_handler(S_RESET_HACK, "on_modified")
            sublime.set_timeout(_callback, 0)


class EmacsTabstopsListener(DynamicListener):
    @staticmethod
    def on_pre_save(view):
        # print("@pre_save", view.buffer_id())
        settings = view.settings()

        syntax = view.settings().get('syntax').lower()
        for skip_ft in get_setting(view, "emacs_tabstops_skip_filetypes"):
            if syntax in skip_ft.lower():
                return

        # decide if we should convert spaces- > tabs before saving
        cos = get_setting(view, "emacs_tabstops_convert_on_save")
        do = ((cos == "always") or
              (cos == "auto" and settings.get(S_CONVERTED_TO) == "spaces"))
        if do:
            # print("EmacsTabstops says covnerting on pre save")
            view.run_command("emacs_tabstops_to_tabs")
            settings.set(S_TTS_ON_PS, True)

    @staticmethod
    def on_post_save(view):
        # print("@post_save", view.buffer_id())
        if view.settings().get(S_TTS_ON_PS, None):
            # print("EmacsTabstops says covnerting on post save")
            view.settings().erase(S_TTS_ON_PS)
            view.run_command("emacs_tabstops_to_spaces")

    @staticmethod
    def on_load(view):
        # print("@load", view.buffer_id())
        syntax = view.settings().get('syntax').lower()
        for skip_ft in get_setting(view, "emacs_tabstops_skip_filetypes"):
            if syntax in skip_ft.lower():
                return

        if get_setting(view, "emacs_tabstops_convert_on_load"):
            # print("EmacsTabstops says delay conversion to activated")
            view.settings().set(S_TTS_ON_ACTIVATE, True)

    @staticmethod
    def on_activated(view):
        # print("@activated", view.buffer_id())
        if view.settings().get(S_TTS_ON_ACTIVATE, False):
            # print("EmacsTabstops says tabstops->spaces")
            view.run_command("emacs_tabstops_to_spaces")
            view.settings().erase(S_TTS_ON_ACTIVATE)

##
## EOF
##
