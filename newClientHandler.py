import threading
import queue
import select
import socket
import hashlib
import string
import random
import time

class NewClientHandler(threading.Thread):

  TIMEOUT = 2
  INIT_STATE = "INIT_STATE"
  STARTED_STATE = "STARTED_STATE"
  FLAG = "RkxBR3toc2RmZ3NoZ2Y1NTY0NjU0c2Rmc2RmMXNkZg=="
  NB_OF_REQUESTS = 20
  MIN_RESPONSE_TIME = 1000
  MAX_RESPONSE_TIME = 2000

  def __init__(self, conn, addr):
    self._q = queue.Queue()
    self._conn = conn
    self._addr = addr
    self._thread_exit_flag = False
    self._state = NewClientHandler.INIT_STATE
    self._counter = NewClientHandler.NB_OF_REQUESTS
    self._last_string = "nothing"
    self._last_hash = "nothing"
    self._request_time = time.time() 
    super(NewClientHandler, self).__init__()

  def on_thread(self, function, *args, **kwargs):
    self._q.put((function, args, kwargs))

  def run(self):
    print ("New connection from ",self._addr)
    self._conn.setblocking(0)
    while not self._thread_exit_flag:
      try:
        function, args, kwargs = self._q.get(False)
        function(*args, **kwargs)
      except queue.Empty:
        self.process_algorithm()
    self.__close()

  def process_algorithm(self):
    ready = select.select([self._conn], [], [], NewClientHandler.TIMEOUT)
    if ready[0]:
      data = self._conn.recv(1024)
      if not data:
        self.terminate()
      else: 
        data = data.decode("utf-8").strip()
        if self._state == NewClientHandler.INIT_STATE:
          if data == "start":
            self._state = NewClientHandler.STARTED_STATE
            self.send_request()
          else:
            self.terminate()
        elif self._state == NewClientHandler.STARTED_STATE:
          delay = self.get_millis() - self._request_time
          if NewClientHandler.MIN_RESPONSE_TIME << delay << NewClientHandler.MAX_RESPONSE_TIME:
            if data == self._last_hash:
              if self._counter > 0:
                self._counter -= self._counter
                self.send_request()
              else:
                self.display_flag()
            else:
              self.terminate()
          else:
            self.terminate() 
  def terminate(self):
    self._thread_exit_flag = True

  def __close(self):
    print ("Closing connection with ", self._addr)
    self._conn.sendall(b"Closing connection."+b'\n')
    self._conn.shutdown(socket.SHUT_RDWR)
    self._conn.close()

  def send_request(self):
    request =  self.string_generator().encode()
    self._conn.sendall(b"MD5 of "+request+b" ?"+b'\n')
    self._request_time = self.get_millis()

  def display_flag(self):
    self._conn.sendall(NewClientHandler.FLAG.encode()+b'\n')
    self.terminate() 
       
  def string_generator(self, size=40, chars=string.ascii_uppercase + string.digits):
    request = ''.join(random.choice(chars) for _ in range(size))
    self._last_string = request
    self._last_hash = hashlib.md5(request.encode("utf-8")).hexdigest()
    print("MD5 of "+request+" is "+self._last_hash)
    return request

  def get_millis(self):
    return int(round(time.time() * 1000))
