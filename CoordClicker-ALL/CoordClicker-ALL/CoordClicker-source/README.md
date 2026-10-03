# CoordClicker

<p align="center"><img src="logo.png" width="160" alt="CoordClicker logo"></p>

A small hotkey driven clicker for Windows. Save two spots in any window, then let it click or scroll them in a loop. Clicks are sent straight to the target window, so you can keep using your computer normally.

## Download

Go to the **Releases** page and download `CoordClicker.exe`. Nothing else needs to be installed. Just double click it.

## How to use

1. Put your mouse over the first spot and press **F1** to save the Right point.
2. Put your mouse over the second spot and press **F2** to save the Left point.
3. Choose an action for each point: Left click, Right click, Scroll Down or Scroll Up.
4. Set the **Amount** (how many times to repeat the Right action) and the **Delay** in milliseconds.
5. Press **F3** to start. Press **F3** again to stop.

The loop is: do the Right action Amount times, do the Left action once, then repeat.

The window under your mouse when you save a point becomes the target. You can also choose one by hand with the Pick button. All hotkeys can be changed with the keyboard button next to each one. Your settings are saved next to the exe.

## Tips

* If the hotkeys do not work while a game is focused, right click the exe and choose Run as administrator.
* Windows only.

## Build it yourself

You need Python installed (tick "Add Python to PATH" in the installer).

1. Download the files in this repository into one folder.
2. Double click `build_exe.bat`.
3. Your exe will appear in the `dist` folder.

You can also run it straight from the code: `pip install keyboard`, then `python coord_clicker.py`.

## Antivirus warnings

Some antivirus tools flag exes made with PyInstaller, especially ones that use global hotkeys. This is a known false positive. The full source code is in this repository, and you can build the exe yourself with the steps above. You can check your download against the SHA256 hash listed in the release notes with:

`certutil -hashfile CoordClicker.exe SHA256`

## Disclaimer

Many games do not allow automation tools. You are responsible for following the rules of any game or program you use this with. This software is provided as is, with no warranty.

## License

MIT License. See the LICENSE file.
