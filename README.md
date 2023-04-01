ocr_flask








20230401 updated:

Crontab -e
*/1 * * * * ps -ef |grep web.py | grep -v grep || /bin/sh /root/AI/ocr_flask/run_ocr.sh
00 17 * * * sudo shutdown -r


line#1 : 每分钟检查系统中是否有正在运行的名为"web.py"的进程，如果没有则执行run_ocr.sh。

        这是一个在Ubuntu 20.04系统中的Crontab记录，它包含了两个命令，通过逻辑运算符"||"连接在一起。下面逐一解释这个记录中的每个部分：

        */1 * * * * ps -ef |grep rock.py | grep -v grep：
        这部分的含义是在每分钟的每一秒都执行一次命令，该命令会列出当前系统上所有进程的详细信息，并通过管道符号"|"将它们传递给grep命令，进一步过滤出包含"rock.py"的行，最后再通过另一个grep命令过滤掉包含"grep"的行。这个命令的目的是查找正在运行的名为"rock.py"的进程。

        ||
        这个符号是逻辑或运算符，它的作用是将前一个命令和后一个命令连接在一起，如果前一个命令执行失败（返回非零状态码），则执行后一个命令。

        /bin/sh /root/AI/ocr_flask/run_ocr.sh：
        这是一个shell脚本命令，它的作用是启动一个名为"run_ocr.sh"的脚本，该脚本位于"/root/AI/ocr_flask/"目录下。这个脚本的作用可能是运行OCR识别程序，根据具体应用场景来决定。

        ***因此，这个Crontab记录的意义是：每分钟检查系统中是否有正在运行的名为"rock.py"的进程，如果没有则执行OCR识别程序。



line#2 : 它表示在每天的17点整（3AM(CST) -- 时区可能会根据系统设置而有所不同）重启系统。  daily.
        第1列 "00" 表示分，取值范围是0-59，这里是0，表示在每小时的0分执行命令。
        第2列 "17" 表示时，取值范围是0-23，这里是17，表示在下午5点整执行命令。
        第3列 "" 表示日，取值范围是1-31，这里是""，表示每天都要执行命令。
        第4列 "" 表示月，取值范围是1-12，这里是""，表示每个月都要执行命令。
        第5列 "" 表示周，取值范围是0-7，这里是""，表示每周都要执行命令。
        最后一列 "sudo shutdown -r" 是要执行的命令，这个命令的作用是以管理员权限重启系统。


run_ocr.sh
tmux new-session -d -s ocr \; send-keys "cd AI/ocr_flask" Enter \; send-keys "/usr/bin/python3 web.py" Enter

    1. tmux new-session -d -s ocr：使用tmux创建一个名为"ocr"的新会话，并将其作为后台进程运行。"-d"选项表示在创建会话后立即将其作为后台进程运行。
    2. ; send-keys "cd AI/ocr_flask" Enter：使用tmux会话中的send-keys命令将"cd AI/ocr_flask"字符串发送到会话的输入缓冲区，并模拟按下"Enter"键。这个命令的作用是切换到"AI/ocr_flask"目录。
    3. ; send-keys "/usr/bin/python3 web.py" Enter：使用tmux会话中的send-keys命令将"/usr/bin/python3 web.py"字符串发送到会话的输入缓冲区，并模拟按下"Enter"键。这个命令的作用是在"AI/ocr_flask"目录中运行"web.py"文件，启动一个Python Web应用程序。
    
综上所述，这个命令的作用是创建一个名为"ocr"的tmux会话，并在该会话中运行一个Python Web应用程序，这个程序位于"AI/ocr_flask"目录中的"web.py"文件中。
