import logging
from flask import Flask,request, jsonify
import sys
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import os
import socket
from dotenv import load_dotenv





def connect_to_relay_server():
    load_dotenv()
    RELAY_HOST = os.getenv("RELAY_HOST")
    RELAY_PORT = 8002

    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender_socket.connect((RELAY_HOST, RELAY_PORT))
    return sender_socket



def request_file(files):

    '''
    This function takes a specific file path, sends a request to the relay server notifying the relay
    server that it is requesting a file, waiting for a response from the relay server, and then downloads
    the specific file from the relay server
     

     
    
    Parameters: 


    Returns: print statement confirming that the file has been downloaded 

    '''




    file_path = files




    file_name = os.path.basename(f"~/BCloud/{file_path}")


    sender_socket = connect_to_relay_server()

    print(f"File Name: {file_name}")
    file_header = f"FILE_REQUEST:{file_name}:"
    sender_socket.send(file_header.encode())
    sender_socket.send(b"END_OF_HEADER") # delimiter to notify the server that the header is done

    end_of_header = b"END_OF_HEADER"
    buffer = b""
    header = None
    job_completed = False
    while job_completed == False:
        data = sender_socket.recv(4096)
        if not data:
            break
        buffer += data
        file_type = "Unknown"
        if end_of_header in buffer and header is None:
            header_part, content = buffer.split(end_of_header, 1)
            header = header_part.decode() 
            print(f"header: {header}")
            split_header = header.split(":")
            file_type = split_header[0]
            file_name = split_header[1]
            file_size = split_header[2]
            print(f"file type: {file_type}")
            print(f"file size: {file_size}")
            print(f"file name: {file_name}")
            buffer = content 

        if file_type == "FILE_REQUEST_RESPONSE":
            # It's a file; process the file header to get file info

            print("entering the file request response logic")
            directory_name = "BCloudFILEREQUEST"
            directory_path = os.path.expanduser(f"~/{directory_name}")
            file_save_path = os.path.join(directory_path, file_name)

            # Check if the directory exists, create if it does not and create a welcome text file
            if not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
                welcome_file_path = os.path.join(directory_path, "welcome.txt")
                with open(welcome_file_path, 'w') as welcome_file:
                    welcome_file.write("Welcome to Banbury Cloud! This is the directory that will contain all of the files "
                                       "that you would like to have in the cloud and streamed throughout all of your devices. "
                                       "You may place as many files in here as you would like, and they will appear on all of "
                                       "your other devices.")

            print("Receiving file...")
            # Send acknowledgment (optional)
            #self.client_socket.send("ACK".encode())
                # Open the file and start writing the content received so far



            with open(file_save_path, 'wb') as file:
                file.write(buffer)  # Write already received part of the file
                bytes_received = len(buffer)  # Update the count of received bytes
                # Continue receiving the rest of the file
                while bytes_received < int(file_size):
                    data = sender_socket.recv(4096)
                    if not data:
                        break  # Connection is closed or error occurred
                    file.write(data)
                    bytes_received += len(data)

            print(f"Received {file_name}.")
            job_completed = True 


    job_completed = True 
    return


def request_file_test():
    # Log a debug message

    # Get the JSON data sent with the POST request
    data = request.get_json()

    # You can now access `files` sent in the request body
    files = data.get('files', [])

    # Perform your logic here with the received files list
    # For example, prepare the requested files for download

    # Respond back with a message or relevant data
    response = jsonify({'message': 'Requesting file...', 'receivedFiles': files})
    return response


def main():

    if len(sys.argv) > 1:
        files = sys.argv[1]
        print(f"Argument received: {files}")
    else:
        print("No argument received.")
        files = "chamonix.mp4"

    request_file(files)

if __name__ == '__main__':
    main()

