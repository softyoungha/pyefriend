# Configuration file for jupyter-notebook.
# ~/.jupyter/jupyter_nootbook_config.py 에 위치시키세요

c = get_config()
c.NotebookApp.password = u'argon2:$argon2id$v=19$m=10240,t=10,p=8$PXZsBHjbmOOtNta5FS0eHw$B27O0Fke2XQtcFo52A6kjw'
c.NotebookApp.open_browser = False
# c.NotebookApp.notebook_dir = u'C:/Users/youngha/PycharmProjects/rebalancing'
c.NotebookApp.ip = '*'
c.NotebookApp.port_retries = 8888