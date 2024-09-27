import http.cookies
import socket
import logging
import chardet
import json
import gzip

class Server:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    def __init__(self, ip_address='192.168.1.13', port=8080):
        self.ip_address = ip_address
        self.port = port
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((ip_address, port))
        self._hooks: dict[str, callable] = {}
        self._session_cookies: list[http.cookies.SimpleCookie] = []
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
        logging.info(f"Server is binded")
        logging.info(f"Server ip: {self._server.getsockname()[0]}")
        logging.info(f"Server port: {self._server.getsockname()[1]}")
    
    def run(self):
        while True:
            self._server.listen(4)
            logging.info(f"Server is listening...")
            conn, addr = self._server.accept()
            if conn:
                self.handle_connection(conn, addr)
    def handle_connection(self, conn, addr):
        logging.info(f"Connection from {addr} has been established")
        data = self.get_request_data(conn)
        if data == '':
            logging.info(f"Empty request from {addr}")
            conn.close()
            return
        logging.info(f"Received request from {addr}")
        headers = data.split("\r\n")
        logging.info(f"Headers: {headers}")
        logging.info(f"Data: {data}")
        cookie_header = self.get_cookie_header(headers)
        cookies = self.get_cookies(cookie_header)
        filename, args = self.get_filename_and_args(headers, data)
        logging.info(f"Filename: {filename}")
        logging.info(f"Args: {args}")
        content, headers = self.get_content(filename, args, cookies)
        self.send_response(conn, addr, content, cookies, headers=headers)

    def send_response(self, conn, addr, content, cookies, headers=["HTTP/1.1 200 OK"]):
        header = f"{'\r\n'.join(headers)}\r\n\r\n".encode('utf8')
        logging.info(f"Header: {header}")
        logging.info(f"Sending response to {addr}: {content[:60]}...")
        conn.sendall(header + content)
        conn.close()
        logging.info(f"Connection from {addr} has been closed")

    def get_session_cookie_header(self):
        if len(self._session_cookies) == 0:
            return ""
        def check_valid_dict(_dict: str) -> bool:
            try:
                json.loads(_dict)
                return True
            except json.JSONDecodeError:
                return False
        def check_valid_list(_list: str) -> bool:
            try:
                json.loads(_list)
                return True
            except json.JSONDecodeError:
                return False
        logging.info(f"Session cookies: {self._session_cookies}")
        ret = ""
        for _index, _cookie in enumerate(self._session_cookies):
            _cookie_name = f"{_cookie['name'].output(header='').split('=')[1]}"
            header = "Set-Cookie: " + _cookie_name + "={"
            for key, value in _cookie.items():
                if key == 'name':
                    continue
                logging.info(f"Session cookie: {key} = {value}")
                value = _cookie[key]
                _key: str = f"\"{key}\""
                _value: str = f"{value.output(header='').split('=')[1]}"
                if not check_valid_dict(_value) and not check_valid_list(_value):
                    _value = _value.strip('"')
                    _value = f'"{_value}"'
                header += f"{_key}:{_value},"
            header = header.strip(',')
            header += "}\r\n"
            ret += header
        logging.info(f"Session cookie header: {ret}")
        return ret
    
    def clear_session_cookies(self):
        self._session_cookies = []

    def get_content(self, filename, args, cookies):
        content = ""
        headers = []
        _type = "text/html"
        for name, hook in self._hooks.items():
            if name == filename:
                try:
                    content = hook(args, cookies)
                except TypeError as e:
                    logging.info(f"Error occurred while executing hook {name}: {e}")
                    try:
                        content = hook(args)
                    except TypeError as e:
                        logging.info(f"Error occurred while executing hook {name}: {e}")
                        content = hook()
                break
        if content.count("\r\n") > 0:
            _headers = content.split("\r\n")[0:-1]
            headers = _headers
            content = content.split("\r\n")[-1]
        else:
            headers.append("HTTP /1.1 200 OK")
        if content == "":
            try:
                filename = filename.strip('/')
                with open(filename, 'rb') as file:
                    content = file.read()
                if filename.endswith(".html"):
                    _type = "text/html"
                elif filename.endswith(".css"):
                    _type = "style/css"
                elif filename.endswith(".js"):
                    _type = "application/javascript"
                elif filename.endswith(".jpg"):
                    _type = "image/jpeg"
                    with open(filename, 'rb') as file:
                        content = file.read()
                elif filename.endswith(".png"):
                    _type = "image/png"
                    headers.append("Content-Type: image/png")
                    with open(filename, 'rb') as file:
                        content = file.read()
                elif filename.endswith(".ico"):
                    _type = "image/x-icon"
            except FileNotFoundError:
                content = b"File Not Found"
        else:
            content = content.encode('utf8')
        # headers.append("Content-Type: " + _type)
        # headers.append("Content-Length: " + str(len(content)))
        headers.append(self.get_session_cookie_header())
        return content, headers

    def get_filename_and_args(self, headers, data):
        header = headers[0]
        if "GET" in header:
            filename = header.split("GET")[1].split('HTTP')[0].strip()
        elif "POST" in header:
            filename = header.split("POST")[1].split('HTTP')[0].strip()
        else:
            filename = header.split("HTTP")[0].strip()
        args = {}
        if '?' in filename:
            filename, _args = filename.split("?")[0], filename.split("?")[1]
            _splitted = _args.split("&")
            if len(_splitted) > 0:
                logging.info(f"Args: {_args}")
                logging.info(f"Splitted: {_splitted}")
                for s in _splitted:
                    if s == "":
                        continue
                    k, v = s.split('=')
                    args[k] = v
        return filename, args

    def get_request_data(self, conn):
        return conn.recv(1024).decode('utf8')
    
    def get_cookie_header(self, headers: list[str]):
        for header in headers:
            if header.startswith("Cookie:"):
                return header
        return None
    
    def get_cookies(self, cookie_header: str):
        if cookie_header is not None:
            logging.info(f"Cookie header: {cookie_header}")
            cookies = cookie_header.lstrip("Cookie:").split(";")
            cookies = [cookie.strip() for cookie in cookies]
            logging.info(f"Cookies: {cookies}")
            logging.info(f"Length: {len(cookies)}")
            ret = {}
            for cookie in cookies:
                key = cookie.split("=")[0]
                value = cookie.split("=")[1]
                value = value.replace("\\054", ",")
                logging.info(f"Cookie: {key} = {value}")
                ret[key] = http.cookies.SimpleCookie(json.loads(value))
            return ret
        return None
    
    def route(self, name):
        def wrapper(func):
            logging.info(f"Adding hook for {name}")
            self._hooks[name] = func
        return wrapper
    
    def redirect(self, url):
        response = f"HTTP/1.1 302 Found\r\nLocation: {url}\r\n\r\n"
        logging.info(f"Redirecting to {url}")
        return response
    
    def set_cookie(self, cookie: http.cookies.SimpleCookie):
        if not cookie in self._session_cookies:
            self._session_cookies.append(cookie)
        return cookie
    
    def check_cookie(self, cookie: http.cookies.SimpleCookie):
        if str(id(cookie)) in self._session_cookies.keys():
            return True
        else:
            return False
        