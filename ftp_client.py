#
#   FTP Client
#
#   Usage: start - python ftp_client.py
#
#   Libraries used:
#   Socket library
#   Sys library
#   Regular expression library
#
#   References:
#   https://tools.ietf.org/html/rfc959
#

import socket, sys, re

MAX_BYTES = 1024

#
#   client() connects the client to the server
#   Output: Socket object
#
def client():
    # Ask user for the host and port
    hostName = raw_input("FTP | Enter host name > ")
    port = int(raw_input("FTP | Enter port number > "))

    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_address = socket.gethostbyname(hostName)
    s.connect((ip_address, port))

    # Print the response and continue if successful
    response = s.recv(MAX_BYTES)
    print(response)
    if response.decode()[:3] != "220":
        print("FTP > Connection failed, please restart and try again")
        s.close()
        sys.exit()
    return s


#
#   listDir(s) prints the current working directory in passive mode
#   Input: Socket object
#
def listDir(s):
    # Send passive mode command
    s.send(b"PASV\r\n")

    # Print the response until status code 227 is received
    response = s.recv(MAX_BYTES)
    print(response)
    while response.decode()[:3] != "227":
        response = s.recv(MAX_BYTES)
        print(response)

    # Get the ip and port for the data from the response
    data_response = re.findall('\((.*\))', response.decode())[0].split(")")[0]
    data_port = int(data_response.split(',')[4]) * 256 + int(data_response.split(',')[5])
    data_ip = ".".join(data_response.split(",")[0:4])

    # Connect to the ip and port received
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((data_ip, data_port))

    # Send list command
    s.send(b"LIST *\r\n")

    # Print the received data
    data = r.recv(MAX_BYTES)
    print(" Perms    Links Owner    Group        Size Date         Name")
    print(data)

    r.close()


#
#   changeWorkingDir(s, directory) changes the current working directory to the given one
#   Input: Socket object, String
#
def changeWorkingDir(s, directory):
    # Send the command to server
    s.send(b"CWD " + bytes(directory) + b"\r\n")

    # Check if sucessful and print the outcome
    response = s.recv(MAX_BYTES)
    print(response)
    while response.decode()[:3] != "250":
        # Stop if status code 550, failure
        if response.decode()[:3] == "550":
            break
        response = s.recv(MAX_BYTES)
        print(response)


#
#   makeDir(s, directory) adds the 
#   Input: Socket object, String
#
def makeDir(s, directory):
    # Send the command to server
    s.send(b"MKD " + bytes(directory) + b"\r\n")

    # Check if sucessful and print the outcome
    response = s.recv(MAX_BYTES)
    print(response)
    while response.decode()[:3] != "257":
        # Stop if status code 550, failure
        if response.decode()[:3] == "550":
            break
        response = s.recv(MAX_BYTES)
        print(response)


#
#   removeDir(s, directory) deletes the given directory if it is in the current directory
#   Input: Socket object, String
#
def removeDir(s, directory):
    # Send the command to server
    s.send(b"RMD " + bytes(directory) + b"\r\n")

    # Check if sucessful and print the outcome
    response = s.recv(MAX_BYTES)
    print(response)
    while response.decode()[:3] != "250":
        # Stop if status code 550, failure
        if response.decode()[:3] == "550":
            break
        response = s.recv(MAX_BYTES)
        print(response)


#
#   getFile(s, file) downloads the given file if it is in the current directory
#   Input: Socket object, String
#
def getFile(s, file):
    # Send passive mode command
    s.send(b"PASV\r\n")

    # Print the response until status code 227 is received
    response = s.recv(MAX_BYTES)
    print(response)
    while response.decode()[:3] != "227":
        response = s.recv(MAX_BYTES)
        print(response)
    
    # Get the ip and port for the data from the response
    data_response = re.search("\((.*?)\)", response.decode()).group(1)
    data_ip = ".".join(data_response.split(",")[0:4])
    data_port = int(data_response.split(',')[4]) * 256 + int(data_response.split(',')[5])

    # Connect to the ip and port received
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((data_ip, data_port))

    # Send RETR command
    s.send(b"RETR " + bytes(file) + b"\r\n")

    # Print the response
    response = s.recv(MAX_BYTES)
    print(response)

    # Continue if the response was successful
    if response.decode()[:3] != "550":
        # Prompt user to enter file save name
        outputFile = raw_input("Enter file name to save as: ")

        # Download and save the file
        output_file = open(outputFile, "wb")
        print("This might take a moment...")
        while True:
            buffer = r.recv(1024)
            if buffer == b"":
                break
            output_file.write(buffer)
        response = s.recv(MAX_BYTES)
        print(response)


#
#   uploadFile(s, file) uploads the given file to the server, the file needs to be in the same folder as the client
#   Input: Socket object, String
#
def uploadFile(s, file):
    # Send passive mode command
    s.send(b"PASV\r\n")

    # Print the response until status code 227 is received
    response = s.recv(MAX_BYTES)
    print(response)
    while response.decode()[:3] != "227":
        response = s.recv(MAX_BYTES)
        print(response)
    
    # Get the ip and port for the data from the response
    data_response = re.search("\((.*?)\)", response.decode()).group(1)
    data_ip = ".".join(data_response.split(",")[0:4])
    data_port = int(data_response.split(',')[4]) * 256 + int(data_response.split(',')[5])

    # Connect to the ip and port received
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((data_ip, data_port))

    # Send STOR command
    s.send(b"STOR " + file + b"\r\n")

    # Open the file and send it to server
    output_file = open(file, "r")
    while True:
        buffer = output_file.read(MAX_BYTES)
        r.sendall(bytes(buffer))
        if buffer == "":
            break
    print("File sent")

#
#   deleteFile(s, file) deletes the given file if it is in the current directory
#   Input: Socket object, String
#
def deleteFile(s, file):
    # Send passive mode command
    s.send(b"PASV\r\n")

    # Print the response until status code 227 is received
    response = s.recv(MAX_BYTES)
    print(response)
    while response.decode()[:3] != "227":
        response = s.recv(MAX_BYTES)
        print(response)

    # Get the ip and port for the data from the response
    data_response = re.search("\((.*?)\)", response.decode()).group(1)
    data_ip = ".".join(data_response.split(",")[0:4])
    data_port = int(data_response.split(',')[4]) * 256 + int(data_response.split(',')[5])

    # Connect to the ip and port received
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((data_ip, data_port))
 
    # Send DELE command
    s.send(b"DELE " + bytes(file) + b"\r\n")
    print("File deleted")


# Initialize connection
s = client()

# Login to the server
user = raw_input("FTP | Enter username > ")
pwd = raw_input("FTP | Enter password > ")

userParam = b"USER " + user + b"\n"
pwdParam = b"PASS " + pwd + b"\n"

s.send(userParam)
print(s.recv(MAX_BYTES))
s.send(pwdParam)
res = s.recv(MAX_BYTES)
print(res)

# Run main application loop if successful
if str(res[:3]) == "230":
    print("FTP > Type 'help' for help")
    while True:
        command = raw_input("FTP > ")

        if str(command) == "list":
            # List working directory
            listDir(s)

        elif str(command[:4]) == "cwd ":
            # Change working directory
            dir = command[4:]
            changeWorkingDir(s, dir)

        elif str(command[:6]) == "mkdir ":
            # Create directory
            dir = command[6:]
            makeDir(s, dir)

        elif str(command[:6]) == "rmdir ":
            # Remove directory
            dir = command[6:]
            removeDir(s, dir)

        elif str(command[:4]) == "get ":
            # Get file
            file = command[4:]
            getFile(s, file)

        elif str(command[:4]) == "del ":
            # Delete file
            file = command[4:]
            deleteFile(s, file)

        elif str(command[:6]) == "store ":
            # Upload file
            file = command[6:]
            uploadFile(s, file)

        elif str(command) == "quit":
            # Quit
            s.close()
            sys.exit()

        elif str(command) == "help":
            # Print possible commands
            print("Possible Commands:")
            print("list                   | displays the current working directory")
            print("cwd <directory name>   | changes the working directory, type / to go to root directory")
            print("mkdir <directory name> | creates a new directory")
            print("rmdir <directory name> | removes the given directory")
            print("get <file name>        | gets the specified file from the server")
            print("del <file name>        | deletes the specified file from the server")
            print("store <file name>      | stores a local file on the server")
            print("quit                   | closes the client")

        else:
            print("FTP > Invalid command, type 'help' for help")

else:
    print("FTP > Login failed, please restart and try again")
    s.close()
