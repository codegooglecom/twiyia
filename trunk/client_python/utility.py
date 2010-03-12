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

import socket, ssl, re, twiyia, blowfish, json, random, globals
import string, cgi, urllib, time, sys, os, shutil, base64, traceback
from os import curdir, sep, path

def getAvailablePort(host):
    for port in [80,8080,8081,8082,8083,8084,8085,8086]:
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(1)
        try:
            sk.connect((host,port))
        except Exception:
            return port
        sk.close()
    return None

def urlfetch(uri, postData = None, headers = None, timeout = None):
    cache   = None
    pathUri = uri
    if postData == None:
        method = 'GET';
        postData = ''
        cache = hitCache(uri)
        if isinstance(cache, dict):
            return cache
        elif cache != None:
            pathUri = cache
    else:
        method = 'POST'
        
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if timeout != None:
        client_sock.settimeout(timeout)
        
    if globals.proxy_port == 443:
        client_sock = ssl.wrap_socket(client_sock)
        client_sock.connect((globals.proxy_ip, globals.proxy_port))
    else:
        client_sock.connect((globals.proxy_ip, globals.proxy_port))
    
    out =  method + ' ' + pathUri + ' HTTP/1.0\r\n'
    out += 'Host: ' + globals.proxy_name + '\r\n'
    if headers != None:
        for key in headers.keys():
            out += key + ': ' + headers[key] + '\r\n'
    out += 'User-Agent: TwiyiaProxy/' + str(globals.proxy_ver) +'\r\n'
    out += 'Content-type: application/x-www-form-urlencoded\r\n'
    out += 'Content-length: ' + str(len(postData)) + '\r\n'
    out += 'Connection: Close\r\n\r\n'
    out += postData
    
    client_sock.send(out)
    
    res = ''
    while 1:
        data = client_sock.recv(1024)
        if not data: break
        res = res + data
    
    client_sock.close()

    if res == '': return False

    responses = res.split('\r\n\r\n', 1)
    
    matches = re.search(r'Static-Version:\s*([0-9\.]+)', responses[0], re.I)
    if matches != None:
        newVersion = matches.group(1)
        newVersion = float(newVersion)
        if globals.static_ver < newVersion:
            verifyCache(newVersion)
            globals.static_ver = newVersion

    headers = responses[0].split('\r\n')
    if len(headers) < 2: return False

    if len(responses) == 2:
        body = responses[1]
    else:
        body = ''
        
    if cache and headers[0].find('200') != -1:
        saveCache(uri, body)

    dic = dict()
    dic['headers'] = headers
    dic['body'] = body
    
    return dic

def hitCache(uri, timeoutHour = 16):
    matches = re.search(r'(jpg|jpeg|gif|swf|png|js|htm|html|txt|css|pdf|zip)$', uri, re.I)
    if matches == None:
        return None
    
    type = matches.group(1).lower();
    if type == 'htm': type = 'html'
    if type == 'txt': type = 'plain'
    
    cacheFile = globals.cachePath + sep + urllib.quote_plus(uri)
    if timeoutHour == 0:
        return None;
    
    if path.isfile(cacheFile) != True:
        return uri + '?r=' + str(random.random())
    
    timestamp = path.getmtime(cacheFile);

    if (time.time() - timestamp) > timeoutHour * 3600:
        return uri + '?r=' + str(random.random())

    header = ''

    matches = re.match(r'(jpg|jpeg|png|gif)', type)
    if matches != None:
        header = "Content-Type: image/" + matches.group(1)
     
    if header == '':
        matches = re.match('(html|plain|css)', type)
        if matches != None:   
            header = "Content-Type: text/" + matches.group(1) + "; charset=utf-8" 
            
    if header == '' and 'js' == type:
        header = "Content-Type: application/x-javascript"
    
    if header == '':
        header = "Content-Type: application/octet-stream"

    f = open(cacheFile, 'rb')
    content = f.read()
    f.close()
    
    res = dict()
    res['headers'] = ['HTTP/1.0 200 OK', header]
    res['body'] = content
    
    return res

def saveCache(uri, content):
    cacheFile = globals.cachePath + sep + urllib.quote_plus(uri)
    f = open(cacheFile, 'wb')
    f.write(content)
    f.close()

def verifyCache(version):
    versionFile = globals.cachePath + sep + 'VERSION'
    if not path.exists(globals.cachePath):
        os.makedirs(globals.cachePath)
        f = open(versionFile, 'w')
        f.write(str(version))
        f.close()
        return
    if path.isfile(versionFile) == True:
        f = open(versionFile, 'r')
        ver = f.read()
        f.close()
        if ver == '': ver = '0'
        if float(ver) >= version:
            return
    shutil.rmtree(globals.cachePath)
    os.makedirs(globals.cachePath)
    f = open(versionFile, 'w')
    f.write(str(version))
    f.close()
    return
    
def blowfishDecode(str):
    key = 'K3H%UBDF%2U6E%77B'
    encoded_text = base64.b64decode(str)
    cipher = blowfish.Blowfish(key)
    cipher.initCTR()
    decode_text = cipher.decryptCTR(encoded_text)
    return decode_text
    
def blowfishEncode(str):
    key = 'K3H%UBDF%2U6E%77B'
    cipher = blowfish.Blowfish(key)
    cipher.initCTR()
    encode_text = cipher.encryptCTR(str)
    return base64.b64encode(encode_text)

def loadJson(jsonText):
    unidic = json.loads(jsonText) # <type 'unicode'> or int etc
    dic = {}
    for k, v in unidic.items():
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        dic[k] = v
    return dic
            
def getLocalInfo():
    info = {}
    if path.isfile(globals.keyFile) == True:
        f = open(globals.keyFile, 'r')
        encoded = f.read()
        f.close()
        jsonText = blowfishDecode(encoded)
        info = loadJson(jsonText)
    else:
        info['local_ip']   = globals.local_ip
        info['local_port'] = globals.local_port
        info['proxy_ver']  = globals.proxy_ver
        info['proxy_name'] = globals.proxy_name
        info['proxy_ip']   = globals.proxy_ip
        info['proxy_port'] = globals.proxy_port
    return info

def saveLocalInfo(info):
    jsonText = json.dumps(info)
    encode_text = blowfishEncode(jsonText)
    f = open(globals.keyFile, 'wb')
    content = f.write(encode_text)
    f.close()
    
def servicePing(info, withKey = False):
    localInfo = info.copy()
    if withKey == True:
        globals.ping_uri   += '?withKey=1' 
        globals.proxy_name = localInfo['proxy_name']
        globals.proxy_ip   = localInfo['proxy_ip']
        globals.proxy_port = localInfo['proxy_port']
    else:
        localInfo['proxy_name'] = globals.proxy_name
        localInfo['proxy_ip']   = globals.proxy_ip
        localInfo['proxy_port'] = globals.proxy_port
    data = urllib.urlencode(localInfo)
    
    try:
        res = urlfetch(globals.ping_uri, postData = data, timeout = 5)
    except Exception:
        #traceback.print_exc(file=sys.stdout)
        return False
    
    if isinstance(res, dict):
        jsonText = blowfishDecode(res['body'])
        remoteInfo = loadJson(jsonText)
        return remoteInfo
    else:
        return False

