import sys
import os
import json
from distutils.sysconfig import get_python_lib


state = {'form': None, 'parameters': {'error': None}}
def configure():
    global state
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.application.current import get_app, set_app
    from prompt_toolkit.shortcuts.dialogs import message_dialog
    from prompt_toolkit.styles import Style
    from prompt_toolkit.layout.containers import VSplit
    from prompt_toolkit.widgets import Label, TextArea
    from prompt_toolkit.shortcuts.dialogs import yes_no_dialog, button_dialog, progress_dialog
    from prompt_toolkit.layout.dimension import Dimension as D
    from prompt_toolkit.widgets import MenuContainer, MenuItem
    import time
    from custom_prompts import form

    config = {
        'server_url': "https://ikr.iipcc.org",
        'directories': [],
        'sqlitepath': 'ikr_log.db',
        'logpath': 'client.log',
    }

    def refresh_token(userid, password):
        import requests
        from requests.adapters import HTTPAdapter
        session = requests.Session()
        session.mount(config['server_url'], HTTPAdapter(max_retries=3))
        TOKEN_REFRESH_URL = "%s/sync/api/v1.0/token/refresh" % config['server_url']

        # refresh token
        try:
            response = session.get(TOKEN_REFRESH_URL,
                             auth=(userid, password),
                             verify=False)
        except requests.exceptions.ConnectionError:
            return None

        # If all fine return token
        if response.status_code == 201:
            return response.json()['token']
        else:
            return None

    def show_ikr_login_form(error=None):
        form(
            title=HTML(u'<style bg="black" fg="white">IKR Python Client Setup</style>'),
            text=HTML(u'<style fg="red">' + str(error if error is not None else '') + '</style>\nProvide your IKR user ID and password below:'),
            inputs=[
                {'label': u'User ID', 'padding': 2, 'type': 'text'},
                {'label': u'Password', 'padding': 1, 'type': 'password'},
            ],
            buttons=[
                {'type': 'ok', 'handler': login}
            ]
        )

    def show_directory_setup_form(error=None):
        form(
            title=HTML(u'<style bg="black" fg="white">IKR Python Client Setup</style>'),
            text=u'Add a file/directory to the registry:',
            inputs=[
                {'label': u'Directory', 'padding': 2, 'type': 'text'},
                {'label': u'Recursive', 'padding': 2, 'type': 'switch'},
            ],
            buttons=[
                {
                    'title': u'Add another',
                    'type': 'ok',
                    'handler': add_next_directory
                },
                {
                    'title': u'Finish',
                    'type': 'ok',
                    'handler': add_last_directory
                },
                'cancel'
            ]
        )

    def show_dbpath_setup_form():
        pass

    def show_logpath_setup_form():
        pass

    def show_complete_dialog():
        pass

    def login(form_data, app):
        global state
        result = refresh_token(form_data['User ID'], form_data['Password'])
        if result is None:
            state['form'] = show_ikr_login_form
            state['parameters'] = {'error': 'Credentials provided are incorrect'}
            app.exit()
        else:
            config['userid'] = form_data['User ID']
            config['password'] = form_data['Password']

            state['form'] = show_directory_setup_form
            state['parameters'] = {'error': None}
            app.exit()

    def add_next_directory(form_data, app):
        global state
        config['directories'].append({
            'type': form_data['Directory'],
            'dirpath': 'R' if form_data['Recursive'] == 'On' else 'O'
        })
        state['form'] = show_directory_setup_form
        state['parameters'] = {'error': None}
        app.exit()

    def add_last_directory(form_data, app):
        global state
        config['directories'].append({
            'dirpath': form_data['Directory'],
            'type': 'R' if form_data['Recursive'] == 'On' else 'O'
        })
        state = None
        app.exit()

    def set_db_path():
        pass

    def set_log_path():
        pass

    def save_config():
        pass

    state['form'] = show_ikr_login_form
    while (state is not None):
        state['form'](**state['parameters'])

    dir_path = get_python_lib() + '/ikr_client'
    config_file = dir_path + '/client_config.json'

    with open(config_file, 'w') as outfile:
        json.dump(config, outfile)


if __name__ == '__main__':
    configure()
