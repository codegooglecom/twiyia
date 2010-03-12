<?php
/*
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
*/
$proxy_name = 'twiyia.com';
$proxy_ip   = 'twiyia.com';
$proxy_port = '443';

$protect   = true;
$username  = 'twiyia';
$password  = 'twiyia';
$prompt    = 'Protected: username and password are twiyia';
$isLog     = true;
$cacheTime = 16; // hours
$cachePath = dirname(__FILE__) . '/cache';

if (!$protect && isset($_SERVER["HTTP_ACCEPT"])) {
    die('Err');
}

if (isset($_SERVER["HTTP_COOKIE"]))
    $cookierawdata = $_SERVER["HTTP_COOKIE"];
else
    $cookierawdata = '';

if ($protect === true) {
    authenticate();
}

$uri = $_SERVER["REQUEST_URI"];

if ($_SERVER["REQUEST_METHOD"] == 'GET') {
    $res = urlfetch($uri, null, array('Cookie:' => $cookierawdata));
    if (!$res)
    raiseErr();
} else if ($_SERVER["REQUEST_METHOD"] == 'POST') {
    $postdata = array();
    foreach ($_POST as $key => $val) {
        $postdata[$key] = urlencode($val);
    }
    if (isset($_FILES['image']) && $_FILES['image']['size'] > 0) {
        $postdata['image_filename'] = urlencode($_FILES['image']['name']);
        $imgdata = file_get_contents($_FILES['image']['tmp_name']);
        $postdata['image']          = urlencode(base64_decode($imgdata));
    }
    $res = urlfetch($uri, $postdata, array('Cookie:' => $cookierawdata), 30);
    if (!$res)
    raiseErr();
} else {
    raiseErr('Only support GET or POST method');
}

foreach($res['headers'] as $header) {
    header($header, false);
}
echo $res['body'];
exit;

function urlfetch($uri, $postdata = null, $headers =null, $timeout = 15) {
    global $proxy_name, $proxy_ip, $proxy_port, $cacheTime;

    $cacheIt = false;
    if(empty($postdata)) {
        $method = 'GET';
        $cacheIt = hitCache($uri, $cacheTime);
    } else {
        $method = 'POST';
        $data = '';
        foreach($postdata as $key=> $val) {
            if ($data != '') $data .= '&';
            $data .= "$key=$val";
        }
    }
    logf($method . ': ' . $uri);

    $ssl = '';
    if ($proxy_port == 443) $ssl = 'ssl://';
    $fp = fsockopen($ssl . $proxy_ip, $proxy_port, $errno, $errstr, 5);

    if (!$fp) {
        return false;
    }

    stream_set_timeout($fp, $timeout);

    $response = '';
    $out =  "$method $uri HTTP/1.0\r\n";
    $out .= "Host: $proxy_name\r\n";
    if (is_array($headers)) {
        foreach($headers as $key => $val) {
            $out .= "$key: $val\r\n";
        }
    }
    $out .= "User-Agent: TwiyiaProxy/1.0\r\n";
    $out .= "Content-type: application/x-www-form-urlencoded\r\n";
    $out .= "Content-length: " . strlen($data) . "\r\n";
    $out .= "Connection: Close\r\n\r\n";
    $out .= $data;

    fwrite($fp, $out);
    while (!feof($fp)) {
        $response .= fgets($fp, 128);
    }
    fclose($fp);
    
    if (empty($response)) return false;

    $responses = explode("\r\n\r\n", $response, 2);
    $headers = explode("\r\n", $responses[0]);
    if (count($headers) < 2) return false;

    $body = $responses[1];
    if ($cacheIt & strpos($headers[0], '200') > 0) {
        doCache($uri, $body);
    }
    return array('headers'=>$headers, 'body'=>$body);
}

function hitCache($uri, $timeout) {
    global $cachePath;
    
    if (!preg_match('/(jpg|jpeg|gif|swf|png|js|htm|html|txt|css|pdf|zip)$/i', $uri, $matches)) {
        return false;
    }
    $type = strtolower($matches[1]);
    if ($type == 'htm') $type = 'html';
    if ($type == 'txt') $type = 'plain';
    
    $cacheFile = $cachePath . '/' . urlencode($uri);
    if ($timeout == 0) {
        return false;
    }
    if (!file_exists($cacheFile)) {
        return true;
    }
    $timestamp = filemtime($cacheFile);
    if ($timestamp == false || time() - $timestamp > $timeout * 3600) {
        return true;
    }
    if (preg_match('/(jpg|jpeg|png|gif)/', $type, $matches)) {
        header("Content-Type: image/" . $matches[1]);
    } else if (preg_match('/(html|plain|css)/', $type, $matches)){
        header("Content-Type: text/" . $matches[1] . "; charset=utf-8");
    } else if ('js' == $type){
        header("Content-Type: application/x-javascript");
    } else {
        header("Content-Type: application/octet-stream");
    }
    $content = file_get_contents($cacheFile);
    echo $content;
    
    exit;
}

function doCache($uri, $content) {
    global $cachePath;
    
    $cacheFile = $cachePath . '/' . urlencode($uri);
    return file_put_contents($cacheFile, $content);
}

function raiseErr($msg = "超时或未知错误, 你的更新可能已完成  (如为上传图片，需等待几个小时以使服务器完成同步)") {
    header('Content-Type:  text/html; charset=utf-8');
    echo $msg;
    exit;
}

function authenticate() {
    global $username, $password, $prompt;

    if (!isset($_SERVER['PHP_AUTH_USER'])
    || $_SERVER['PHP_AUTH_USER'] != $username
    || $_SERVER['PHP_AUTH_PW'] != $password) {
        header('Content-Type:  text/html; charset=utf-8');
        header('WWW-Authenticate: Basic realm="' . $prompt . '"');
        header('HTTP/1.0 401 Unauthorized');
        echo '请输入用户名和密码';
        exit;
    }
}

function logf($mix) {
    global $cachePath, $isLog;
    
    if (!$isLog) return;
    if (is_array($mix) || is_object($mix)) {
        $mix = json_encode($mix);
    }
    error_log(date('Y-m-d H:i:s') . ': ' . $mix . "\n", 3, $cachePath . "/logs");
}
