#!/bin/sh
#cd /home/nl/test/ && nohup /usr/bin/python3 /home/nl/test/test.py > /home/nl/smzd_push/test.out 2>&1



tmux new-session -d -s ocr \; send-keys "cd AI/ocr_flask" Enter \; send-keys "/usr/bin/python3 web.py" Enter
