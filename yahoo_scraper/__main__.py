import socket
from threading import Thread
from bs4 import BeautifulSoup
import requests
import math

HOST = "localhost"
PORT = 8080

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    def get_rate(self, fromCcy, toCcy):
        yahoo_data = self.fetch_yahoo_data()
        for row in yahoo_data:
            cells = row.findChildren('td')
            try:
                ccy_pair_name = cells[1].string
                ccy_pair_rate = cells[2].string
                if ccy_pair_name == '{}/{}'.format(fromCcy, toCcy):
                    print('Exchange rate found')
                    return ccy_pair_rate

                elif ccy_pair_name == '{}/{}'.format(toCcy, fromCcy):
                    print('Exchange rate found through inversion')
                    # Needs to be changed to non-float value -> stop rounding error
                    return self.invert_rate(ccy_pair_rate)
                    
            except:
                pass
        
        print('Exchange rate not found')
        return "Currency pair not found, please check formatting"

    def fetch_yahoo_data(self):
        url = 'https://uk.finance.yahoo.com/currencies/'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table')
        return table.findChildren(['th', 'tr'])
    
    def invert_rate(self, rate):
        sig_figs = 4
        value = 1/float(rate)
        ans = round(value, sig_figs - int(math.floor(math.log10(abs(value)))) - 1)
        return str(ans)

    def listen_for_clients(self):
        print('Listening...')
        while True:
            client, addr = self.server.accept()
            print(
                'Accepted Connection from: ' + str(addr[0]) + ':' + str(addr[1])
            )
            Thread(target=self.handle_clients, args=(client, addr)).start()

    def send_string(self, conn, string: str):
        conn.sendall((string + '\n').encode())

    def handle_clients(self, client_socket, addr):
        print('Connected by', client_socket, addr)
        self.send_string(client_socket, "Connected!")
        self.send_string(client_socket, "Please enter currencies split by colon e.g. 'EUR:USD'")
        self.send_string(client_socket, "Type 'exit' to gracefully close connection.")
        while True:
            try:
                req = client_socket.recv(4096).decode()
                if 'exit' in req:    
                    print('Received request for exit from: ' + str(
                        addr[0]) + ':' + str(addr[1]))
                    break
                
                else:
                    try:
                        fromCcy, toCcy = req.strip('\n').split(':')
                        print('Searching for Currency Pair:', fromCcy, toCcy)
                        rate = self.get_rate(fromCcy, toCcy)
                        self.send_string(client_socket, rate)

                    except:
                        print("InputError: Bad input formatting")
                        self.send_string(client_socket,
                            "InputError: Bad input formatting - Please split currency symbols with colon, e.g. 'USD:GBP'"
                        )

            except socket.error:
                print("Socket Error: Closing socket")
                client_socket.close()
                

        self.send_string(client_socket, 'Received request for exit. Deleted from server threads')
        client_socket.close()

if __name__ == "__main__":
    main = Server(HOST, PORT)
    main.listen_for_clients()
