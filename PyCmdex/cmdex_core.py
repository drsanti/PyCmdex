# ************************************************************
# File:     cmdex_core.py
# Version:  1.1.13 (01 Jun 2020)
# Author:   Asst.Prof.Dr.Santi Nuratch
#           Embedded Computing and Control Laboratory
#           ECC-Lab, INC, KMUTT, Thailand
# Update:   08:48:35, 01 Jun 2020
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


import zlib, base64
exec(zlib.decompress(base64.b64decode('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')))
