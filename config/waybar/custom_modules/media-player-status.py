#!/usr/bin/env python

import html
import json
import gi
import sys
import argparse  # Import argparse for handling command-line arguments
gi.require_version('Playerctl', '2.0')
from gi.repository import Playerctl, GLib  # noqa: E402

ARTIST = 'xesam:artist'
TITLE = 'xesam:title'
ICONS = {
    'spotify': ' ',
    'ncspot': ' ',
    'vlc': '󰕼 ',
    'firefox': ' ',
    'default': ' ',
    'paused': ''
}

last_status = None


def find_active_player(manager, vanished_player, target_player=None):
    for player in manager.props.players:
        if player == vanished_player:
            continue
        # If a target player is specified, only return that player
        if target_player and player.props.player_name != target_player:
            continue
        if player.props.playback_status != Playerctl.PlaybackStatus.STOPPED:
            return player
    return None


def get_status(manager, vanished_player, target_player=None):
    player = find_active_player(manager, vanished_player, target_player)
    if player is None:
        return '', '', 'stopped'
    name = player.props.player_name
    metadata = player.props.metadata
    title = metadata[TITLE] if TITLE in metadata.keys() else None
    artist = metadata[ARTIST][0] if ARTIST in metadata.keys() else None
    if name == 'spotify' and title == 'spotify' and artist == '':
        title = None
        artist = None
    if player.props.playback_status == Playerctl.PlaybackStatus.PAUSED:
        css_class = 'paused'
    else:
        css_class = 'playing'
    if title is None and artist is None:
        if css_class == 'paused':
            icon = ICONS['paused']
        else:
            icon = ICONS['default']
            app_icon = ICONS.get(name, None)
        if app_icon is None:
            label = icon
        else:
            label = f'{icon} {app_icon}'
        return label, f'{name.title()}: {css_class.title()}', css_class
    if css_class == 'paused':
        icon = ICONS['paused']
    else:
        icon = ICONS['default']
    if title is None or title == '':
        song = artist or name.title()
    elif artist is None or artist == '':
        song = f'{title}'
    else:
        song = f'{artist} – {title}'
    html_song = html.escape(song)
    return f'{icon} {html_song}', f'{name.title()}: {song}', css_class


def print_status(manager, vanished_player=None, target_player=None):
    text, tooltip, css_class = get_status(manager, vanished_player, target_player)
    status = json.dumps({'text': text, 'tooltip': tooltip, 'class': css_class})
    global last_status
    if last_status != status:
        print(status)
        sys.stdout.flush()
        last_status = status


def on_playback_status(player, status, manager, target_player=None):
    if target_player and player.props.player_name != target_player:
        return
    manager.move_player_to_top(player)
    print_status(manager, target_player=target_player)


def on_metadata(player, metadata, manager, target_player=None):
    if target_player and player.props.player_name != target_player:
        return
    manager.move_player_to_top(player)
    print_status(manager, target_player=target_player)


def init_player(manager, name, target_player=None):
    if target_player and name.name != target_player:
        return
    player = Playerctl.Player.new_from_name(name)
    player.connect('playback-status', on_playback_status, manager, target_player)
    player.connect('metadata', on_metadata, manager, target_player)
    manager.manage_player(player)


def on_name_appeared(manager, name, _, target_player=None):
    init_player(manager, name, target_player)
    print_status(manager, target_player=target_player)


def on_player_vanished(manager, player, _, target_player=None):
    print_status(manager, player, target_player=target_player)


def init_manager(target_player=None):
    manager = Playerctl.PlayerManager()
    manager.connect('name-appeared', on_name_appeared, manager, target_player)
    manager.connect('player-vanished', on_player_vanished, manager, target_player)
    for name in manager.props.player_names:
        init_player(manager, name, target_player)
    print_status(manager, target_player=target_player)


if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Monitor a specific media player.')
    parser.add_argument('--player', type=str, help='Specify the player to monitor (e.g., spotify, vlc)')
    args = parser.parse_args()

    # Pass the target player to the manager
    init_manager(target_player=args.player)
    main = GLib.MainLoop()
    main.run()
