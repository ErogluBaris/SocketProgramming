import socket
import json
import requests

class SocketSC():
    def __init__(self, data, st_ssid, plug_name):
        self.data = data
        self.st_ssid = st_ssid
        self.plug_name = plug_name
        self.plug_info = {}

    def filterRssi(self, dic):
        available_plugs = {}
        for i in dic:
            if i.find("Plug") != -1:
                available_plugs[i] = dic[i]

        return available_plugs

    def serverOrClient(self, dic):
        if self.st_ssid in dic:
            if dic[self.st_ssid] > -70:
                return "server"
            else:
                return "client"
        else:
            return "client"

    def APIrequest(self, data, route, method):
        print("Request is inializing")
        if method == "POST":
            control = False
            while control == False:
                try:
                    response = requests.post("localhost:8080"+route, data)
                    control = True
                except:
                    print("I couldn't request it")
                print(response)
            return response
        elif method == "GET":
            response = "WAIT"
            while response == "WAIT":
                try:
                    response = requests.get("localhost:8080" + route)
                except:
                    print("I couldn't request it")
                print(response)
            return response
        else:
            print("There is no such sending method in that function")
            return

    def socketServer(self):
        print("Socket server is starting....")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', 4040))
        server.listen(5)
        server_response = "Data is recieved.."
        control = False
        plug_count = 0
        while control == False:
            try:
                server.timeout(10)
                clientsocket, address = server.accept()
                print("Connection from {} has been established.".format(address))
                if plug_count > 2:
                    clientsocket.send(bytes("FALURE", "utf-8"))
                    print("Server is full!!!")
                    clientsocket.close()
                    break
                else:
                    data = clientsocket.recv(700)
                    data = json.loads(data.decode("utf-8"))
                    print(data)
                    self.plug_info.update(data)
                    clientsocket.send(bytes(server_response, "utf-8"))
                    clientsocket.close()
                    plug_count += 1
            except:
                if plug_count == 0:
                    control = True
                else:
                    clientsocket.close()
                    control = True
            response_1 = self.APIrequest(self.plug_info, "/mapping")
            if response_1 == "SUCCESS":
                response_new = self.APIrequest("", "/missingPlug")
                if response_new == "SUCCESS":
                    print("Mission Complete")
                else:
                    print("These plugs are missing: "+str(response_new))


    def socketClient(self, dic, data):
        print("Socket client is starting....")
        rssi_plugs = self.filterRssi(dic)
        control = False
        data = {self.plug_name:"15V-12I-1200P"}
        while control == False:
            for i in rssi_plugs:
                if int(rssi_plugs[i]) > -70:
                    print("trying the connect {}".format(i))
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect(("127.0.0.1", 4040))
                    data = json.dumps(data)
                    client.send(bytes(data, "utf-8"))
                    response = client.recv(500)
                    print(str(response))
                    if response.decode("utf-8") == "FAILURE":
                        pass
                    else:
                        control = True
                        print("Connected to {}".format(i))
                        break

#LIFECYCLE
