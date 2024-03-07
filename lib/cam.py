import socket, pickle, struct
from v4l2py import Device, VideoCapture
from v4l2py.device import BufferType

class CAM():
    def __init__(self, DEBUG, host, port, ID):
        self.DEBUG = DEBUG        
        self.ID = ID
        
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(5)
            
    def run(self):
        with Device.from_id(self.ID) as cam:
            cap = VideoCapture(cam)
            cap.set_format(320, 240, "YUYV")
            while True:
                client_socket, addr = self.socket.accept()
                if client_socket:
                    with Device.from_id(self.ID) as cam:
                        cap = VideoCapture(cam)
                        cap.set_format(320, 240, "MJPG")
                        cap.set_fps(30)
            
                        for frame in cam:
                            a = pickle.dumps(frame.array)
                            message = struct.pack("Q", len(a)) + a
                            client_socket.sendall(message)

# self.socket.close()