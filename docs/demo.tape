Output docs/pytest-demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 750
Set Theme "Dracula"
Set TypingSpeed 40ms
Set Padding 20
Set PlaybackSpeed 1.0

Type "source .venv/bin/activate"
Enter
Sleep 500ms

Type "pytest -v --color=yes"
Enter
Sleep 5s

Type "pytest -m smoke --color=yes"
Enter
Sleep 2500ms

Type "pytest -m regression --color=yes"
Enter
Sleep 2500ms
