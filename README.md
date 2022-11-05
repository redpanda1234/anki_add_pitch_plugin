# Overview
For use adding Japanese pitch accent and devoicing information to anki
cards

Forked from
[https://github.com/IllDepence/anki_add_pitch_plugin.git](https://github.com/IllDepence/anki_add_pitch_plugin.git)


# Usage
There is no real documentation for this because I am a mess

I am sorry

I think you probably need to git clone this repo into
`~/.local/share/Anki2/addons21/` or something. After you might have to
open `Tools` -> `Add-ons` and do something in the resulting menu but
to be honest I don't quite remember.

Anyways, once you do that, when you go to add anki cards, create
fields called `pitch_reading` and `pitch_pattern`. I think the names
are hard-coded to these but I have sort of forgotten how I wrote it.
Put a kana string like `ふつう` in for `pitch_reading`, and then to
generate the pitch pattern, input a string comprised of a subset of
the following characters:

- "H" (high pitch, voiced vowel)
- "h" (high pitch, devoiced vowel)
- "L" (low pitch, voiced vowel)
- "l" (low pitch, devoiced vowel)

You want to make the pitch string one character longer than the
reading --- depending on whether this extra character is an H/h or an
L/l you'll get a high/low open white circle that tells the reader what
the pitch should be for any following particles / words.

If you want to have things like "（〜が）じょうず（な）" be your
`pitch_reading` field, I unironically suggest you achieve this by
1) Typing "じょうず" in for `pitch_reading`
2) Adding the appropriate pitch string (e.g. "LHHL")
3) Pressing the button to add the pitch accent, and then
4) Amending `pitch_reading` to contain "（〜が）じょうず（な）" and
trying your very best to resist the temptation to click the "add
pitch" button a second time.

This is a bad solution, in the sense that it is not really much of a
solution at all.

# Save yourself
Please do not click any of the buttons listed under "Pitch Accent" in
the "Tools" menu. These are holdovers from the version of the project
I forked. I don't know if any of the changes I made will cause
problems with them because I have not tested them at all. You're welcome
