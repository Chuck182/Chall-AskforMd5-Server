import sys
import signal
import string
import random
import socket
import threading 

from newClientHandler import NewClientHandler

HOST = '127.0.0.1'
PORT = 22000

server_socket = None
client_connections = []
exit_flag = False

def sigint_handler(sig, frame):
  print ("SIGINT received. Closing server socket.")
  for conn in client_connections:
    conn.on_thread(conn.terminate)
  if server_socket is not None:
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
  sys.exit(0)

if __name__== "__main__":
  signal.signal(signal.SIGINT, sigint_handler)
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
      conn, addr = s.accept()
      client_connections.append(NewClientHandler(conn,addr))
      client_connections[-1].start()
