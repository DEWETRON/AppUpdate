#! python

#
# dwsign.py Copyright (c) Dewetron 2019
#

import argparse
import os
import subprocess
import sys
import time


VERBOSE = 0

def die(msg):
    print("-----------------------------------------------------------------")
    print("Error: %s" % msg, flush=True)
    sys.exit(1)


def verbose(msg):
    if VERBOSE:
        print(msg, flush=True)


def get_signtool():
    """
    should be extended for available windows kits
    """
    signtool_candidates = [
        "C:/Program Files (x86)/Windows Kits/10/App Certification Kit/signtool.exe",
        "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x64/signtool.exe",
        "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe",
        "C:/Program Files (x86)/Windows Kits/10/bin/10.0.18362.0/x64/signtool.exe",
        "C:/Program Files (x86)/Windows Kits/10/bin/10.0.18362.0/x86/signtool.exe",
        "C:/Program Files (x86)/Windows Kits/8.1/bin/x64/signtool.exe",
        "C:/Program Files (x86)/Windows Kits/8.1/bin/x86/signtool.exe",
        "C:/Program Files (x86)/Microsoft SDKs/Windows/v7.1A/Bin/signtool.exe"
    ]

    for signtool in signtool_candidates:
        if os.path.exists(signtool):
            return signtool

    return None


def verify_signature(file_to_sign):
    """
    """
    signtool = get_signtool()
    if signtool is None:
        return True
        
    try:
        subprocess.check_call([signtool, 'verify', '-pa', file_to_sign])

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            'verify_signature problem (CalledProcessError) (%s)' % str(e))
    return True


def sign_exe(file_to_sign, host):
    """
    sign_exe(file_to_sign, host):
    """
    verbose("sign_exe(%s, %s)" % (file_to_sign, host))
    try:
        if not os.path.exists('c:\\signature\\sign.cmd'):
            raise RuntimeError(
                'sign_exe problem not found: c:\\signature\\sign.cmd')

        if not os.path.exists(file_to_sign):
            raise RuntimeError(
                'sign_exe could not find %s' % file_to_sign)

        subprocess.check_call(['C:\\signature\\sign.cmd', file_to_sign, 'app'])

        verify_signature(file_to_sign)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            'sign_exe problem (CalledProcessError) (%s)' % str(e))
    return True


def sign(file_to_sign, host, sign_method):
    """
    sign(file_to_sign, host, type)
    """
    verbose("sign(%s, %s, %s)" % (file_to_sign, host, sign_method))
    try:
        if not os.path.exists('c:\\signature\\sign.cmd'):
            raise RuntimeError(
                'sign problem not found: c:\\signature\\sign.cmd')

        if not os.path.exists(file_to_sign):
            raise RuntimeError(
                'sign could not find %s' % file_to_sign)

        subprocess.check_call(['C:\\signature\\sign.cmd', file_to_sign, sign_method])

        verify_signature(file_to_sign)

    except subprocess.CalledProcessError as e:
            raise RuntimeError(
                'sign problem (CalledProcessError) (%s)' % str(e))
    return True


def sign_bundle(file_to_sign, host):
    """
    sign_bundle(file_to_sign, host):
    Explanation here: http://wixtoolset.org/documentation/manual/v3/overview/insignia.html
    """
    verbose("sign_bundle(%s, %s)" % (file_to_sign, host))
    try:
        if not os.path.exists('c:\\signature\\sign_sw_app.cmd'):
            raise RuntimeError(
                'sign_bundle problem not found: c:\\signature\\sign_sw_app.cmd')

        if 'WIX' not in os.environ.keys():
            die("WIX installation not found")

        insignia_bin = os.path.join(os.environ['WIX'], 'bin', 'insignia.exe')
        if not os.path.exists(insignia_bin):
            die("WIX insignia not found")

        if not os.path.exists(file_to_sign):
            raise RuntimeError(
                'sign_bundle could not find %s' % file_to_sign)

        # detach burn engine, sign burn engine
        burn_engine = os.path.splitext(file_to_sign)[0] + '_engine.exe'
        subprocess.check_call([insignia_bin, '-ib', file_to_sign, '-o', burn_engine])
        sign_exe(burn_engine, host)
        verify_signature(burn_engine)  

        # attach burn engine, sign complete bundle
        subprocess.check_call([insignia_bin, '-ab', burn_engine, file_to_sign, '-o', file_to_sign])
        time.sleep(1)
        sign_exe(file_to_sign, host)
        verify_signature(file_to_sign)

        # remove detached burn engine
        os.unlink(burn_engine)

    except subprocess.CalledProcessError as e:
            raise RuntimeError(
                'sign_bundle problem (CalledProcessError) (%s)' % str(e))
    return True


def dwsign(argv):
    """
    function interface for dwsign. to be used if imported (instead of main)
    """
    parser = argparse.ArgumentParser(
    description='%s is a script file for signing installer, driver and executables' % sys.argv[0])

    parser.add_argument('files_to_sign',
                        metavar="files",
                        nargs="+",
                        default=[],
                        help='files to sign')
    parser.add_argument('--bundle', dest='bundle',
                        action='store_true',
                        default=False,
                        help='Uses special WiX bundle signing')
    parser.add_argument('--type', dest='type',
                        action='store',
                        default='Auto',
                        choices=['Auto', 'app', 'driver', 'driver10', 'msi'],
                        help='select the sign type')
    parser.add_argument('-s', '--signing_host', dest='signing_host',
                        action='store',
                        default='bruck.dewetron.com',
                        help='Server to use for signing')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        default=False,
                        help='be more verbose')

    args = parser.parse_args(argv)

    global VERBOSE
    VERBOSE = args.verbose

    try:
        for f in args.files_to_sign:
            if args.type == 'Auto':
                ext = os.path.splitext(f)[1]
                if '.msi' == ext:
                    sign(f, args.signing_host, 'msi')
                if '.exe' == ext:
                    if args.bundle:
                        sign_bundle(f, args.signing_host)
                    else:
                        sign(f, args.signing_host, 'app')
                if '.cab' == ext:
                    sign(f, args.signing_host, 'driver10')
            else:
                sign(f, args.signing_host, args.type)

    except RuntimeError as e:
        print("%s" % (e))
        return False

    return True

# main
if __name__ == "__main__":
    ret = dwsign(sys.argv[1:])
    # cmdlne expexts 0 (== False) for success
    sys.exit(not ret)
