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

from distutils.core import setup
import py2exe

py2exe_options = dict(
                      ascii=True,
                      compressed=True,
                      )
setup(name='Twiyia Web Accelerator',
      version='v1.0',
      description='A web proxy accelerator tool by http proxy and email proxy',
      author='https://code.google.com/p/twiyia/',
      console=[{"script":'twiyia.py', "icon_resources": [(1, "twiyia1.ico")]}]) # windows or console