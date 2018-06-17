from __future__ import unicode_literals
from functools import partial
import six

from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import to_filter
from prompt_toolkit.formatted_text import to_formatted_text, Template, is_formatted_text
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.containers import Window, VSplit, HSplit, FloatContainer, Float, WindowAlign, is_container
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.dimension import is_dimension, to_dimension
from prompt_toolkit.layout.margins import ScrollbarMargin, NumberedMargin
from prompt_toolkit.layout.processors import PasswordProcessor, ConditionalProcessor, BeforeInput
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.utils import get_cwidth




class SwitchButton(object):
    """
    Clickable button.

    :param text: The caption for the button.
    :param handler: `None` or callable. Called when the button is clicked.
    :param width: Width of the button.
    """
    def __init__(self, states=[], width=12):
        assert isinstance(width, int)

        if len(states) == 0:
            states = ["On", "Off"]

        self.current_state = 0
        self.text = states[0]
        self.states = states
        self.width = width
        self.control = FormattedTextControl(
            self._get_text_fragments,
            key_bindings=self._get_key_bindings(),
            focusable=True)

        def get_style():
            if get_app().layout.has_focus(self):
                return 'class:button.focused'
            else:
                return 'class:button'

        self.window = Window(
            self.control,
            align=WindowAlign.CENTER,
            height=1,
            width=width,
            style=get_style,
            dont_extend_width=True,
            dont_extend_height=True)

    def handler(self):
        if self.current_state == len(self.states) - 1:
            self.text = self.states[0]
            self.current_state = 0
        else:
            self.text = self.states[self.current_state + 1]
            self.current_state += 1

    def _get_text_fragments(self):
        text = ('{:^%s}' % (self.width - 2)).format(self.text)

        def handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                self.handler()

        return [
            ('class:button.arrow', '<', handler),
            ('class:button.text', text, handler),
            ('class:button.arrow', '>', handler),
        ]

    def _get_key_bindings(self):
        " Key bindings for the Button. "
        kb = KeyBindings()

        @kb.add(' ')
        @kb.add('enter')
        def _(event):
            if self.handler is not None:
                self.handler()

        return kb

    def __pt_container__(self):
        return self.window
