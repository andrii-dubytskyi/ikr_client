from __future__ import unicode_literals
import functools
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.eventloop import run_in_executor
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.widgets import ProgressBar, Dialog, Button, Label, Box, TextArea, RadioList
from custom_widgets import SwitchButton



def form(title='', text='', cancel_text='Cancel', inputs=[], buttons=[], style=None, async_=False):
    """
    Display a text input box.
    Return the given text, or None when cancelled.
    """
    #def accept():
    #    get_app().layout.focus(ok_button)
    input_objects = []
    button_objects = []

    def create_submit_handler(callback_handler=None):
        def submit_handler():
            user_defined_handler = buttons
            data = {}
            for i in range(0, len(input_objects)):
                inp = input_objects[i]
                if str(inputs[i].get('type', 'text')).lower() == 'switch':
                    data[inp.children[0].content.text()] = str(input_objects[1].children[1].content.text()[1][1]).strip()
                elif str(inputs[i].get('type', 'text')).lower() in ['text', 'password']:
                    data[inp.children[0].content.text()] = inp.children[1].content.buffer.text

            if callback_handler is None:
                get_app().exit(result=data)
            else:
                callback_handler(data, get_app())
        return submit_handler

    def create_cancel_handler(callback_handler=None):
        pass

    def create_button(title, handler=None):
        return Button(text=title, handler=handler)

    if len(buttons) == 0:
        buttons = ['ok', 'cancel']

    for button in buttons:
        button_obj = None

        if isinstance(button, str) and button.lower() == 'ok':
            button_obj = create_button('OK', create_submit_handler())
        elif isinstance(button, dict) and button.get('type', None) is not None and button['type'].lower() == 'ok':
            button_obj = create_button(button.get('title', 'OK'), create_submit_handler(button.get('handler', None)))
        elif isinstance(button, str) and button.lower() == 'cancel':
            button_obj = create_button('Cancel', create_cancel_handler())
        elif isinstance(button, dict) and button.get('type', None) is not None and button['type'].lower() == 'cancel':
            button_obj = create_button(button.get('title', 'Cancel'), create_cancel_handler(button.get('handler', None)))
        else:
            if isinstance(button, dict):
                button_obj = create_button(button.get('title', ''), handler=button.get('handler', None))
            elif isinstance(button, Button):
                button_obj = button

        if button_obj is not None:
            button_objects.append(button_obj)

    for inp in inputs:
        group = [
            Label(text=inp['label'])
        ]
        if inp.get('type') in ['text', 'password']:
            group.append(TextArea(
                multiline=False,
                password=inp.get('type', 'text') == 'password',
                completer=inp.get('completer', None),
            ))
        elif inp.get('type') == 'switch':
            group.append(
                SwitchButton()
            )
        input_objects.append(
            VSplit(group, padding=D(preferred=inp.get('padding', False), max=inp.get('padding', 1)))
        )

    dialog = Dialog(
        title=title,
        body=HSplit([
                Label(text=text, dont_extend_height=True)
            ] + input_objects,
            padding=D(preferred=1, max=1)
        ),
        buttons=button_objects,
        with_background=True)

    return _run_dialog(dialog, style, async_=async_)

def _create_app(dialog, style):
    # Key bindings.
    bindings = KeyBindings()
    bindings.add('tab')(focus_next)
    bindings.add('s-tab')(focus_previous)

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([
            load_key_bindings(),
            bindings,
        ]),
        mouse_support=True,
        style=style,
        full_screen=True)

def _return_none():
    " Button handler that returns None. "
    get_app().exit()

def _run_dialog(dialog, style, async_=False):
    " Turn the `Dialog` into an `Application` and run it. "
    application = _create_app(dialog, style)
    if async_:
        return application.run_async()
    else:
        return application.run()
