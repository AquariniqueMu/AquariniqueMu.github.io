-- The installer substitutes @BLOG@, @ACTION@, and @LOG@ with quoted strings.
-- All user input is handled by Python + osascript argv, never interpolated into shell code.
on run
    set blogPath to @BLOG@
    set launchAction to @ACTION@
    set logPath to @LOG@
    do shell script (quoted form of blogPath & " gui " & quoted form of launchAction & " > " & quoted form of logPath & " 2>&1 &")
end run
