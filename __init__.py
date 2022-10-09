""" Anki plugin to add pitch accent indicators to cards.

    This plugin makes use of data from Wadoku by Ulrich Apel.
    (See file wadoku_parse.py for more details.)
    Wadoku license information is available on the web:

    http://www.wadoku.de/wiki/display/WAD/Wörterbuch+Lizenz
    http://www.wadoku.de/wiki/display/WAD/%28Vorschlag%29+Neue+Wadoku-Daten+Lizenz
"""

import json
import os
import re
import time
from aqt import mw, gui_hooks
from aqt.utils import showInfo, chooseList, getText
from aqt.qt import *
from anki.storage import Collection
from .util import *
from .draw_pitch import pitch_svg


def add_pitch_dialog():
    # environment
    collection_path = mw.col.path
    plugin_dir_name = __name__

    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, "addons21", plugin_dir_name)

    # load pitch dict
    pitch_csv_path = os.path.join(plugin_dir_path, "wadoku_pitchdb.csv")
    acc_dict = get_accent_dict(pitch_csv_path)

    # load user pitch dict if present
    user_pitch_csv_path = os.path.join(plugin_dir_path, "user_pitchdb.csv")
    if os.path.isfile(user_pitch_csv_path):
        acc_dict.update(get_user_accent_dict(user_pitch_csv_path))

    # figure out collection structure
    deck_id = select_deck_id("Which deck would you like to extend?")
    if deck_id == None:
        return
    note_type_ids = get_note_type_ids(deck_id)
    if len(note_type_ids) > 1:
        note_type_id = select_note_type(note_type_ids)
    elif len(note_type_ids) < 1:
        showInfo("No cards found.")
        return
    else:
        note_type_id = note_type_ids[0]
    if note_type_id == None:
        return
    note_ids = get_note_ids(deck_id, note_type_id)
    if len(note_ids) == 0:
        showInfo("No cards found.")
        return
    expr_idx, rdng_idx, out_idx = select_note_fields_all(note_ids[0])
    if None in [expr_idx, rdng_idx, out_idx]:
        return

    # extend notes
    nf_lst, n_updt, n_adone, n_sfail = add_pitch(
        acc_dict, plugin_dir_name, note_ids, expr_idx, rdng_idx, out_idx
    )
    showInfo(
        (
            "done :)\n"
            "skipped {} already annotated notes\n"
            "updated {} notes\n"
            "failed to generate {} annotations\n"
            "could not find {} expressions"
        ).format(n_adone, n_updt, n_sfail, len(nf_lst))
    )


def add_pitch_dialog_user():
    showInfo(
        (
            "You can manually set pitch accent annotations when adding or"
            " editing cards by clicking on the 'set pitch accent' icon"
            " located on the right hand side next to the text formatting"
            " options."
        )
    )


def show_custom_db_path_dialog():
    collection_path = mw.col.path
    plugin_dir_name = __name__
    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, "addons21", plugin_dir_name)
    user_pitch_csv_path = os.path.join(plugin_dir_path, "user_pitchdb.csv")

    showInfo(
        (
            "You can extend and overwrite pitch accent patterns using the"
            ' file "{}". The file has to be three columns (expression,'
            " reading, pitch accent pattern) separated by TAB characters."
            "".format(user_pitch_csv_path)
        )
    )


def remove_pitch_dialog_user():
    return remove_pitch_dialog(user_set=True)


def remove_pitch_dialog(user_set=False):
    # environment
    collection_path = mw.col.path
    plugin_dir_name = __name__

    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, "addons21", plugin_dir_name)

    # figure out collection structure
    deck_id = select_deck_id("From which deck would you like to remove?")
    if deck_id == None:
        return
    note_type_ids = get_note_type_ids(deck_id)
    if len(note_type_ids) > 1:
        note_type_id = select_note_type(note_type_ids)
    elif len(note_type_ids) < 1:
        showInfo("No cards found.")
        return
    else:
        note_type_id = note_type_ids[0]
    if note_type_id == None:
        return
    note_ids = get_note_ids(deck_id, note_type_id)
    if len(note_ids) == 0:
        showInfo("No cards found.")
        return
    del_idx = select_note_fields_del(note_ids[0])
    if del_idx == None:
        return

    # remove from notes
    n_adone, n_updt = remove_pitch(note_ids, del_idx, user_set)
    showInfo(
        (
            "done :)\n" "skipped {} notes w/o accent annotation\n" "updated {} notes"
        ).format(n_adone, n_updt)
    )


def set_pitch_dialog(editor):
    # get user input from card
    pitch_reading = editor.note["pitch_reading"]
    pitch_pattern = editor.note["pitch_pattern"]

    # get note data as a list of tuples of the form (field name, contents)
    note_data = [
        (fld, editor.mw.col.media.escapeImages(val)) for fld, val in editor.note.items()
    ]

    # Figure out the index of the field named "pitch_image"
    pitch_image_ind = 0
    for (i, datum) in enumerate(note_data):
        if datum[0] == "pitch_image":
            pitch_image_ind = i
            break

    # remove existing accent pattern
    acc_patt = re.compile(
        r"<!-- (user_)?accent_start -->.+<!-- (user_)?accent_end -->", re.S
    )
    old_field_val = note_data[pitch_image_ind][1]
    old_field_val_clean = re.sub(acc_patt, "", old_field_val)

    # generate SVG
    svg = pitch_svg(pitch_reading, pitch_pattern)
    if len(old_field_val_clean) > 0:
        separator = "<br><hr><br>"
    else:
        separator = ""
    new_field_val = ("{}<!-- user_accent_start -->{}{}<!-- user_accent_end -->").format(
        old_field_val_clean, separator, svg
    )
    if pitch_reading == "" and pitch_pattern == "":
        new_field_val = old_field_val_clean

    # add new patt
    note_data[pitch_image_ind] = (
        note_data[pitch_image_ind][0],  # leave field name as is
        new_field_val,  # update field value
    )
    js = "setFields(%s); setFonts(%s); focusField(%s); setNoteId(%s)" % (
        json.dumps(note_data),
        json.dumps(editor.fonts()),
        json.dumps(pitch_image_ind),
        json.dumps(editor.note.id),
    )
    js = gui_hooks.editor_will_load_note(js, editor.note, editor)
    editor.web.eval(js)


def addPitchButton(buttons, editor):
    # environment
    collection_path = mw.col.path
    plugin_dir_name = __name__

    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, "addons21", plugin_dir_name)
    icon_path = os.path.join(plugin_dir_path, "icon.png")

    btn = editor.addButton(icon_path, "foo", set_pitch_dialog, tip="set pitch accent")
    buttons.append(btn)


# add menu items
pa_menu = QMenu("Pitch Accent", mw)
pa_menu_add = pa_menu.addAction("bulk add")
pa_menu_remove = pa_menu.addAction("bulk remove")
pa_menu_add_user = pa_menu.addAction("manually add/edit/remove")
pa_menu_remove_user = pa_menu.addAction("remove all manually set")
pa_menu_custom_db_path = pa_menu.addAction("show custom DB path")
# add triggers
pa_menu_add.triggered.connect(add_pitch_dialog)
pa_menu_remove.triggered.connect(remove_pitch_dialog)
pa_menu_add_user.triggered.connect(add_pitch_dialog_user)
pa_menu_remove_user.triggered.connect(remove_pitch_dialog_user)
pa_menu_custom_db_path.triggered.connect(show_custom_db_path_dialog)
# and add it to the tools menu
mw.form.menuTools.addMenu(pa_menu)
# add editor button
gui_hooks.editor_did_init_buttons.append(addPitchButton)
