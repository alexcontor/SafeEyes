#!/usr/bin/env python
# Safe Eyes is a utility to remind you to take break frequently
# to protect your eyes from eye strain.

# Copyright (C) 2017  Gobinath

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Show health statistics on the break screen.
"""

import datetime
import logging

context = None
no_of_skipped_breaks = 0
no_of_breaks = 0
no_of_cycles = -1
session = None
safe_eyes_start_time = datetime.datetime.now()
total_idle_time = 0


def init(ctx, safeeyes_config, plugin_config):
    """
    Initialize the plugin.
    """
    global context
    global session
    global no_of_skipped_breaks
    global no_of_breaks
    global no_of_cycles
    logging.debug('Initialize Health Stats plugin')
    context = ctx
    if session is None:
        session = context['session']['plugin'].get('healthstats', None)
        if session is None:
            session = {'no_of_skipped_breaks': 0,
                       'no_of_breaks': 0, 'no_of_cycles': -1}
            context['session']['plugin']['healthstats'] = session
        no_of_skipped_breaks = session.get('no_of_skipped_breaks', 0)
        no_of_breaks = session.get('no_of_breaks', 0)
        no_of_cycles = session.get('no_of_cycles', -1)


def on_stop_break():
    """
    After the break, play the alert sound
    """
    global no_of_skipped_breaks
    if context['skipped']:
        no_of_skipped_breaks += 1
        session['no_of_skipped_breaks'] = no_of_skipped_breaks


def get_widget_title(break_obj):
    """
    Return the widget title.
    """
    global no_of_breaks
    global no_of_cycles
    no_of_breaks += 1
    if context['new_cycle']:
        no_of_cycles += 1
    session['no_of_breaks'] = no_of_breaks
    session['no_of_cycles'] = no_of_cycles
    return _('Health Statistics')


def get_widget_content(break_obj):
    """
    Return the statistics.
    """
    screen_time = round(((datetime.datetime.now() - safe_eyes_start_time).total_seconds() - total_idle_time) / 60)
    hours, minutes = divmod(screen_time, 60)
    time_format = '{:02d}:{:02d}'.format(hours, minutes)
    if hours > 6 or round((no_of_skipped_breaks / no_of_breaks), 1) >= 0.2:
        # Unhealthy behavior -> Red broken heart
        heart = '💔️'
    else:
        # Healthy behavior -> Green heart
        heart = '💚'
    return "{}\tBREAKS: {}\tSKIPPED: {}\tCYCLES: {}\tSCREEN TIME: {}".format(heart, no_of_breaks, no_of_skipped_breaks, no_of_cycles, time_format)


def on_start():
    """
    Add the idle period to the total idle time.
    """
    global total_idle_time
    # idle_period is provided by Smart Pause plugin
    total_idle_time += context.get('idle_period', 0)
