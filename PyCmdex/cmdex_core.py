"""
# ************************************************************
# File:     cmdex_core.py
# Version:  1.1.16 (11 Jun 2020)
# Author:   Asst.Prof.Dr.Santi Nuratch
#           Embedded Computing and Control Laboratory
#           ECC-Lab, INC, KMUTT, Thailand
# Update:   15:33:32, 11 Jun 2020
# ************************************************************
# 
# 
# Copyright 2020 Asst.Prof.Dr.Santi Nuratch
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
"""


import zlib, base64
exec(zlib.decompress(base64.b64decode('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')))
