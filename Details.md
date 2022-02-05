## Drums configuration

Drums are configured in a text files (in [etc/drums/pop/](etc/drums/pop/drum_level2.json), etc/drums/rock/, ...) using
JSON format. Several popular drum patterns are pre-configured. Looper uses randomness to make it less repetitive,
patterns change every three bars. Drum ends (aka breaks) play when loop is switched or when a button is pushed. Drums
accompaniment is created after the first loop is recorded and BPM is defined by length of this loop. Drum volume and
swing may be changed on the run. Swing settings is same as Linn's LM-1, from 0.5 to 0.75.

## MIDI foot controller to use

Any MIDI controller sending notes may be configured to work with the looper. MIDI commands and looper actions are
configured in a text files (e.g. [etc/midi/playing.json](etc/midi/playing.json)) for Irig Blueboard foot controller.
There are 4 buttons on this pedal named A,B,C,D and 2 extra buttons attached to MIDI expression inputs named E1 and E2.

MIDI over Bluetooth needs manual pairing. You may use wired USB MIDI controller as well or even typing keyboard. Check
file [start.sh](start.sh) and [kbd_notes.json](etc/count/kbd_notes.json) for details.

## Looper modes - "direct" and "indirect"

There are two MIDI configurations that we may call "direct" and "indirect".

Direct has each song part/loop assigned a separate button like on a hardware looper. Direct configuration is clear and
fast but number of loops is limited by number of available buttons.

Indirect may have any number of parts/loops. Some buttons scroll and select a loop, others apply various actions. This
configuration takes more button pushes and is much slower.

Direct configuration is used to for song parts and indirect for loops in a part, exact details are below.

## Looper views - "all parts", "one part", "looper settings", "looper parameters"

Most often "all parts" view is used. It shows all song parts and allows switching between them.

To see what a song part is made of there is "one part" view. It shows all loops inside part and can scroll over them.
Some buttons overdub, delete, mute, reverse selected loop.

Looper parameters view has:

- drum volume and drum swing
- mixer volume for recording and playback

Settings view includes screens:

- save as new/load/delete song (song name is just a time stamp: mm-dd-hh-MM-ss)
- restart/update application (download the latest branch form GitHub)
- load drum style (e.g. pop/rock/....)

MIDI commands assigned to buttons are different for these views and are listed in [commands.md](etc/midi/commands.md)
located along with JSON files in [etc/midi/](etc/midi)

## Extending MIDI foot controller commands

Buttons are scarce resource for looper and there are much more commands than available buttons. To deal with it multi
tapping mode is used. If delay between taps is less than 0.6 seconds they belong to one series and produce different
MIDI command.

As an example button A sends note 60. Multiple tapping will send additional note 80 (aka mapped note) + number of taps +
5 if the last tap was long (hold after tap). Mapping 60->80 is needed to avoid conflicts with other buttons that may
send notes 61, 62, 63, ... For this example:

- single tap sends notes 60 and 80 + 1 = 81
- double tap sends notes 60 and 80 + 2 = 82
- single tap with hold sends notes 60 and 80 + 1 + 5 = 86
- double tap with hold sends notes 60 and 80 + 2 + 5 = 87

Using this method one button may send 6-7 times more MIDI notes.

Multi tapping mode needs a delay to decide if there will be next tap. Because of this it should not be used for time
critical commands e.g. start recording/playing. But for other commands like changing looper settings it is
indispensable. Midi count is configured in [mapped_notes.json](etc/count/mapped_notes.json)

### Notes about installation of LCD:

Connect LCD and run scripts coming with it. Without X11 on Raspberry Pi OS Lite there may be some errors reported but
after reboot you should see boot messages and command prompt. Check files [config.txt](etc/lcd/config.txt)
and [cmdline.txt](etc/lcd/cmdline.txt) - working for my version of LCD screen.


