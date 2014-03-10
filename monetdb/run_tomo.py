#!/usr/bin/python

import pexpect,os,sys
mcl = pexpect.spawn("/home/adria/bin/monetdb/bin/mclient -d tpch")
mcl.expect("sql>")

os.system("/home/adria/bin/monetdb/bin/tomograph --dbname=tpch &")

mcl.sendline(open(sys.argv[1]).read()+"\q")

mcl.expect(pexpect.EOF, timeout=3600*2)
