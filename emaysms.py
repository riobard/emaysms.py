#!/usr/bin/python

from urllib2 import urlopen, URLError
from urllib import urlencode
from getopt import gnu_getopt as getopt, GetoptError
import sys
import logging
import xml.etree.ElementTree as ET


ENDPOINT_URL = 'http://sdkhttp.eucp.b2m.cn/sdkproxy/'
SDK_VERSION = '4.1.0'


class EmaySMSException(Exception):
    pass


class EmaySMS(object):
    def __init__(self, cdkey, password):
        self.cdkey      = cdkey
        self.password   = password


    def api(self, action, data):
        data['cdkey']       = self.cdkey
        data['password']    = self.password

        try:
            f   = urlopen(ENDPOINT_URL + action + '.action', urlencode(data))
            xml = f.read().strip()
        except URLError as e:
            raise EmaySMSException(e)

        try:
            e   = ET.fromstring(xml) 
            err = int(e.find('error').text)
            msg = e.find('message').text
        except ET.ParseError as e:
            raise EmaySMSException(e)

        if 1 == err:    # Something went wrong
            raise EmaySMSException(msg)
        else:           # Looks good
            return msg


    def register(self):
        '''
        Register the cdkey once and for all. A cdkey must be registered before
        you can use it to send SMS. A cdkey needs to be re-registered if it is
        de-registered before. 
        '''

        self.api('regist', {})


    def deregister(self):
        ' De-register a cdkey '
        self.api('logout', {})


    def register_detail_info(self, cdkey, password, name, contact, tel,
                             mobile, email, fax, address, zipcode):
        ' Register your company\'s detailed information. '

        self.api('registdetailinfo', {
            'ename'     : name,
            'linkman'   : contact,  # I HATE POOR ENGLIHS!!! WTF is linkman??
            'phonenum'  : tel,
            'mobile'    : mobile,
            'email'     : email,
            'fax'       : fax,
            'address'   : address,
            'postcode'  : zipcode
        })


    def send(self, phone_numbers, message, time=None, serial=None):
        ' Send an instant SMS to a list of phone numbers '

        if not isinstance(message, unicode):
            raise EmaySMSException('Message must be a Unicode string. ')

        # Max 500 chars (same for UTF-8 and ASCII) per message. It will be 
        # split into 70 chars chunks before sending to mobile phones. The 4.1.0
        # HTTP SDK is wrong about the 1,000 chars limit for ASCII chars. 
        if len(message) > 500:
            raise EmaySMSException('Message too long. ')

        numbers = ','.join(phone_numbers)
        msg     = message.encode('utf-8')
        logging.debug('{0} | "{1}"'.format(numbers, msg))
        data    = {'phone': numbers, 'message': msg}

        if time is None:
            action = 'sendsms'
            if len(phone_numbers) > 1000:
                raise EmaySMSException('Too many phone numbers. '
                                       'Maxium 1000 for sending instant SMS. ')
        else:
            action = 'sendtimesms'
            data['sendtime'] = time
            if len(phone_numbers) > 200:
                raise EmaySMSException('Too many phone numbers. '
                                       'Maxium 200 for sending timed SMS. ')

        if serial is not None:
            if len(serial) > 10:
                raise EmaySMSException('Serial too long. Max 10 digits. ')
            data['addserial'] = serial

        self.api(action, data)


    @property
    def sent(self):
        return self.api('getmo', {})


    @property
    def balance(self):
        ' Query account blance in RMB '
        msg = self.api('querybalance', {})
        return float(msg)


    def recharge(self, card_number, card_password):
        ' Recharge account using a prepaid card '
        self.api('chargeup', {'cardno': card_number, 'cardpass': card_password})
        

    def change_password(self, new_password):
        self.api('changepassword', {'newPassword': new_password})




if __name__ == "__main__" : 

    USAGE = '''
Usage: emaysms.py -k [KEY FILE] [ACTION] [ARGS]


Example
-------


Register a key file. A key file must be registered before it can be used:

    emaysms.py register -k [KEY FILE]


De-register a key file:

    emaysms.py deregister -k [KEY FILE] 


Send an SMS. If `-t` option is omitted, the message is sent immediately. Otherwise, the message is sent at the given time by `-t`. SMS content is read from stdin, with up to 500 Chinese characters or 1,000 ASCII characters. 

    echo "Hello World!" | emaysms.py send -k [KEY FILE] [-t YYYYMMDDHHMMSS] PHONE1 [PHONE2 ...]


Query account balance:

    emaysms.py balance -k [KEY FILE]


Recharge an account:

    emaysms.py recharge -k [KEY FILE] [PREPAID CARD NUMBER] [PREPAID CARD PASSWORD]


Change password for a key file. Remember to change the old password in the key file:

    emaysms.py changepassword -k [KEY FILE]  [NEW PASSWORD]



Key file format
---------------

    cdkey=AAAA-BBB-CCCC-DDDD
    password=123456
'''


    def parse_key_file(filename):
        try:
            for line in open(filename).readlines():
                line = line.strip()
                if line.startswith('cdkey'):
                    k, v = line.split('=', 1)
                    cdkey = v.strip()
                elif line.startswith('password'):
                    k, v = line.split('=', 1)
                    password = v.strip()
            return cdkey, password
        except IOError as e:
            if e.errno == 2:
                sys.exit('Key file "{0}" not found. '.format(filename))



    class Actions():
        ' Command containter '

        @staticmethod
        def send(emay, opts, args):
            if len(args) < 1:
                sys.exit(USAGE)
            numbers = args

            try:
                encoding = opts.get('-c', 'utf8')
                message = sys.stdin.read()
                msg = message.decode(encoding)
            except UnicodeDecodeError:
                sys.exit('Failed to decode message using encoding "{0}". '.format(encoding))

            emay.send(numbers, msg)

        
        @staticmethod
        def sent(emay, opts, args):
            print emay.sent


        @staticmethod
        def balance(emay, opts, args):
            print emay.balance

        
        @staticmethod
        def recharge(emay, opts, args):
            card_number     = args[0]
            card_password   = args[1]
            emay.recharge(card_number, card_password)


        @staticmethod
        def changepassword(emay, opts, args):
            new_password = args[0]
            emay.change_password(new_password)


        @staticmethod
        def register(emay, opts, args):
            emay.register()


        @staticmethod
        def deregister(emay, opts, args):
            emay.deregister()




    def main():

        try:
            opts, args = getopt(sys.argv[1:], 'k:hc:', ['help'])
            opts = dict(opts)
        except GetoptError as e:
            sys.exit(str(e) + '\n' + USAGE)

        if '-h' in opts or '--help' in opts:
            sys.exit(USAGE)

        if len(args) > 0:
            action  = args[0].lower()
            args    = args[1:]
        else:
            sys.exit('Action required. ')


        if not hasattr(Actions, action):
            sys.exit('Unknonw action {0}'.format(action))

        if '-k' in opts:
            cdkey, password = parse_key_file(opts['-k'])
            emay = EmaySMS(cdkey, password)
        else:
            sys.exit('Key file "-k" required. ')

        try:
            getattr(Actions, action)(emay, opts, args)
        except EmaySMSException as e:
            sys.exit(e)



    main()
