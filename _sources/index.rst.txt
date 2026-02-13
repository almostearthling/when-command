The When Automation Tool
========================

This document describes the new version of **When**, a Python-based automation tool for desktop
environments. This version, instead of incorporating the scheduler, relies on the
`whenever <https://github.com/almostearthling/whenever>`_ core, which focuses on reliability and
lightweightness, while trying to achieve a good performance even when running at low priority.
In this sense, **When** acts as a *wrapper* for **whenever**, both providing a simple interface
for configuration and an easy way to control the scheduler via an icon sitting in the tray area
of your desktop. This version of **When** aims at being cross-platform, dynamically providing
access to the features of **whenever** that are supported on the host environment.

`When <https://github.com/almostearthling/when-command>`_ development is hosted on GitHub.


.. image:: graphics/when-application.png


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   main
   install
   tutorial
   cli
   cfgform
   tray
   tasks
   tasks_extra_session
   conditions
   cond_timerelated
   cond_actionrelated
   cond_eventrelated
   cond_extra01
   events
   events_extra01
   history
   i18n
   appdata
   configfile
   lua_considerations
   credits
   when_history
   license
