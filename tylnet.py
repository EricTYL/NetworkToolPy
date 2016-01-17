#!/etc/python2.7

import sys
import socket
import getopt
import threading
import subprocess

# Global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print "TYL Net Tool"
    print
    print "SYNOPSIS:"
    print "tylnet.py -t target_host -p port [options]"
    print
    print "OPTIONS:"
    print "-l --listen"
    print "-e --execute-file_to_run"
    print "-c --command"
    print "-u --upload=destination"
    print
    print "examples:"
    print "tylnet.py -t 192.168.0.1 -p 4343 -l -c"
    print "tylnet.py -t 192.168.0.1 -p 4343 -l -u=c:\\target.exe"
    print "tylnet.py -t 192.168.0.1 -p 4343 -l -e=\"cat /etc/passwd\""
    print "echo 'wtf is this' | ./tylnet.py -t 192.168.11.12 -p 7654"
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # Read input from command line
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])

    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Invalid input"

    # Listen or send something from stdin
    if not listen and len(target) and port > 0:

        # Read buffer from command line
        # It will block
        # Press Ctrl-D if not send something via stdin
        buffer = sys.stdin.read()

        # Send data in buffer
        client_sender(buffer)

    # Listen and do options
    if listen:
        server_loop()

def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to target host
        client.connect((target,port))

        if len(buffer):
            client.send(buffer)

        while True:

            # Wait for data
            recv_len = 1
            response = ""

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response

            # Wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # Send buffer
            client.send(buffer)

    except:
        print "[*] Exception! Exiting."

        # Disconnect client
        client.close()

def server_loop():
    global target
    global port

    # Listen all interface if target is not selected
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Open client thread
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):

    # Trim the new line
    command = command.rstrip()

    # Run the command and get output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

    except:
        output = "Failed to run the command.\r\n"

    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    # Upload data
    if len(upload_destination):

        file_buffer = ""

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)

        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    # Execute cmd
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    # Open shell
    if command:

        while True:
            # Show a cmd interface
            client_socket.send("<sh:#> ")

            # Wait for input until receive LF (Enter)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Get cmd output and send back
            response = run_command(cmd_buffer)
            client_socket.send(response)

main()
