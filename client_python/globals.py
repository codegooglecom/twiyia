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

from os import curdir, sep

local_ip      = '127.0.0.1'
local_port    = None

static_ver = 1.0
proxy_ver  = 1.0
proxy_name = 'twiyia.com'
proxy_ip   = 'twiyia.com'
proxy_port = 443
ping_uri = '/ping/message.php'

keyFile     = curdir + sep + 'key'
cachePath   = curdir + sep + 'cache'
settingFile = curdir + sep + 'setting.ini'