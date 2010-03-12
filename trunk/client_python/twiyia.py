# coding=utf-8
"""
 This software is open source; you can redistribute it and/or modify it 
 under the terms of the GNU General Public License. The license is available
 at http://www.gnu.org/licenses/gpl.html

 This software must be used and distributed in accordance
 with the law. The author claims no liability for its
 misuse.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 
 More information please refer to https://code.google.com/p/twiyia/
"""

import string, cgi, urllib, time, sys, os, webbrowser, globals
import socket, ssl, base64, traceback, utility, ConfigParser
from os import curdir, sep, path
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

class TwiyiaHandler(BaseHTTPRequestHandler):
  
    def init(self, method):
        self.httpEnviron = {}
        self.httpHeaders = {}
        
        self.httpEnviron['REQUEST_METHOD'] = method
        if self.headers.getheader('content-type'):
            self.httpHeaders['content-type'] = self.headers.getheader('content-type')
        if self.headers.getheader('content-length'):
            self.httpHeaders['content-length'] = self.headers.getheader('content-length')
        if self.headers.getheader('content-disposition'):
            self.httpHeaders['content-disposition'] = self.headers.getheader('content-disposition')
            
        if self.headers.getheader('cookie'):
            self.httpHeaders['cookie'] = self.headers.getheader('cookie')
        else:
            self.httpHeaders['cookie'] = ''
        
    def address_string(self):
        return 'localhost'
    
    def sendResponse(self, data):
        for line in data['headers']:
            self.wfile.write(line + '\r\n')
        self.wfile.write('\r\n')
        self.wfile.write(data['body'])

    def do_GET(self):
        try:
            self.init('GET')
            res = utility.urlfetch(self.path, headers={'Cookie': self.httpHeaders['cookie']})
            self.sendResponse(res)
        except Exception:
            self.raiseErr()
     
    def do_POST(self):
        try:
            self.init('POST')
            POST = cgi.FieldStorage(self.rfile, self.httpHeaders, '', self.httpEnviron)
            
            postData = dict()
            for key in POST.keys():
                if key == 'image' and POST[key].filename:
                    postData[key] = base64.b64encode(POST[key].value)
                    postData['image_filename'] = POST[key].filename
                else:
                    postData[key] = POST[key].value
            postData = urllib.urlencode(postData)
            res = utility.urlfetch(self.path, postData = postData, headers={'Cookie': self.httpHeaders['cookie']});
            self.sendResponse(res)
        except Exception:
            self.raiseErr()
        
    def raiseErr(self, msg = "超时或未知错误, 你的更新可能已完成  (如为上传图片，需等待几个小时以使服务器完成同步)"):
        self.send_response(500, 'error')
        self.wfile.write('Content-Type:  text/html; charset=utf-8\r\n\r\n')
        self.close_connection = 1
        self.end_headers()
        
        self.wfile.write(msg)
        #traceback.print_exc(file=sys.stdout)
    def log_error(self):
        pass
    def log_request(self, code='-', size='-'):
        pass

class TwiyiaServer(ThreadingMixIn, HTTPServer):
    
    def handle_error(self, request, client_address):
        pass

def main():
    if path.isfile(globals.settingFile) == True:
        config = ConfigParser.SafeConfigParser()
        config.read(globals.settingFile)
        globals.proxy_name = config.get('HTTP', 'domain')
        globals.proxy_ip   = config.get('HTTP', 'ip')
        globals.proxy_port = config.getint('HTTP', 'port')
        
    print 'Twiyia Web Accelerator v' + str(globals.proxy_ver)
    print '\n服务起动...'.decode('utf-8')
    socket.setdefaulttimeout(20)
    globals.local_port = utility.getAvailablePort(globals.local_ip)
    if globals.local_port == None:
        print '\n没有可用的网络端口...'.decode('utf-8')
        time.sleep(60)
        return
    
    localInfo = utility.getLocalInfo()
    remoteInfo = utility.servicePing(localInfo)
    if remoteInfo == False:
        remoteInfo = utility.servicePing(localInfo, withKey = True)
        
    if remoteInfo == False:
        print '\n网络不通，请稍后再试'.decode('utf-8')
        print '\n如长时间无法连接, 可能所用代理节点无法使用, 请发邮件至 twiyia@gmail.com, 邮件主题 proxy, 以获取最新信息'.decode('utf-8')
        time.sleep(60)
        return
    else:
        print ''
        print '+' * 35
        if remoteInfo['proxy_ver'] > globals.proxy_ver:
            print remoteInfo['update_message'].decode('utf-8')
            time.sleep(60)
            return
        else:
            print remoteInfo['welcome_message'].decode('utf-8')
        print '+' * 35
        print ''
            
        globals.static_ver = remoteInfo['static_ver']
        utility.verifyCache(remoteInfo['static_ver'])
            
        if remoteInfo['load_balance'] == 1:
            globals.proxy_name = remoteInfo['proxy_name']
            globals.proxy_ip   = remoteInfo['proxy_ip']
            globals.proxy_port = remoteInfo['proxy_port']
    
    try:
        server = TwiyiaServer((globals.local_ip, globals.local_port), TwiyiaHandler)
        if globals.local_port != 80:
            portStr = ':' + str(globals.local_port)
        else:
            portStr = ''
        print '请稍后, 正在用你的缺省浏览器打开网址 http://'.decode('utf-8') + globals.local_ip + portStr
        print ''
        time.sleep(5)
        webbrowser.open_new('http://' + globals.local_ip + portStr)
        
        server.serve_forever()
    except KeyboardInterrupt:
        print '\n收到命令 Ctrl + C, 正在关闭服务\n'.decode('utf-8')
        server.socket.close()
        
if __name__ == '__main__':
    main()

