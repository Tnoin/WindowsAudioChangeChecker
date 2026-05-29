# WindowsAudioChangeChecker
just a cute script to compare an old registry export to a new one to see if anything changed. mostly because changed settings after updates annoyed me.

Usage so far:  
Step 1 is to get an export of the relevant registry section. Windows gives us a command for that. The target folder is freely changeable (altough i reccomend not using the user folder as that caused access issues on my machine)

reg export HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices "D:\\dokumente\\AudioExport.reg"


Step 2  
run the code, it should automatically populate the list of ID's on first run.


Step 3 (optional)   
add "24dbb0fc-9311-4b3d-9cf0-18ff155639d4=Default Audio Output" at the end of the id lookup text. im not 100% sure that is what it is, but it *seems* to be, and makes it more readable in my opinion.



Thats it. it should automatically end if it cannot find any changes, or pause and wait for the enter key if it does.
With the idea of if its called in autoruns, so from boot, that it lets me know if a windows updated messed with my audio settings (and which ones)
