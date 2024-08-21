import sys

import sgtk

PROJECT_ID = '87'


def main(project_id=PROJECT_ID):
    user = login_user()

    print('Start engine for project', project_id)
    engine = load_engine(user, int(project_id))

    # start publish app
    if 'Publish...' in engine.commands:
        engine.execute_command('Publish...', [])
    engine.destroy()


def login_user():
    sgtk.LogManager().initialize_custom_handler()
    # Set debugging to true so that we get more verbose output, (should only be used for testing).
    #sgtk.LogManager().global_debug = True

    auth = sgtk.authentication.ShotgunAuthenticator()
    user = auth.get_user()
    sgtk.set_authenticated_user(user)

    return user

def load_engine(user, project_id):
    mgr = sgtk.bootstrap.ToolkitManager(user)
    mgr.plugin_id = 'basic.shell'
    
    # maybe required if booting sth else than a project entity
    #mgr.pre_engine_start_callback = _pre_engine_start_callback

    project = {'type': 'Project', 'id': project_id}
   
    return mgr.bootstrap_engine('tk-shell', entity=project)


def _pre_engine_start_callback(ctx):
    '''
    Called before the engine is started.

    :param :class:"~sgtk.Context" ctx: Context into
        which the engine will be launched. This can also be used
        to access the Toolkit instance.
    '''
    ctx.sgtk.synchronize_filesystem_structure()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
    else:
        project_id = PROJECT_ID
    main(project_id)