#!/usr/bin/python

from urllib2 import urlopen
from urllib import urlencode
from getopt import gnu_getopt as getopt, GetoptError
import sys
import logging


ENDPOINT_URL = 'http://sdkhttp.eucp.b2m.cn/sdkproxy/'


class EmaySMSException(Exception):
    pass


class EmaySMS(object):
    def __init__(self, cdkey, password):
        self.cdkey      = cdkey
        self.password   = password


    def api(self, action, data):
        data['cdkey']       = self.cdkey
        data['password']    = self.password
        f = urlopen(ENDPOINT_URL + action + '.action', urlencode(data))
        response = f.read()
        if '<error>0</error>' not in response:
            raise EmaySMSException(response)
        return response


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

        numbers = ','.join(phone_numbers)
        logging.debug('{0} | "{1}"'.format(numbers, message))
        # max 500 Chinese chars or 1000 ASCII chars
        msg     = message.encode('UTF-8')  
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

        return self.api(action, data)


    @property
    def sent(self):
        return self.api('getmo', {})


    @property
    def balance(self):
        ' Query account blance '
        xml = self.api('querybalance', {})
        return xml


    def recharge(self, card_number, card_password):
        ' Recharge account using a prepaid card '
        self.api('chargeup', {'cardno': card_number, 'cardpass': card_password})
        

    def change_password(self, new_password):
        self.api('changepassword', {'newPassword': new_password})





USAGE = '''
Usage: emaysms.py -k [KEY FILE] [ACTION] [ARGS]


Example
-------


Register a key file:

    emaysms.py register -k [KEY FILE]


De-register a key file:

    emaysms.py deregister -k [KEY FILE] 


Send an SMS:

    emaysms.py send -k [KEY FILE] [-t YYYYMMDDHHMMSS] PHONE1 [PHONE2 ...]


Query balance:

    emaysms.py balance -k [KEY FILE]


Recharge an account:

    emaysms.py recharge -k [KEY FILE] [PREPAID CARD NUMBER] [PREPAID CARD PASSWORD]


Change password for a key file:

    emaysms.py changepassword -k [KEY FILE]  [NEW PASSWORD]



Key file format
---------------

    cdkey=AAAA-BBBB-CCCC-DDDD
    password=123456
'''


def parse_key_file(filename):
    for line in open(filename).readlines():
        line = line.strip()
        if line.startswith('cdkey'):
            k, v = line.split('=', 1)
            cdkey = v.strip()
        elif line.startswith('password'):
            k, v = line.split('=', 1)
            password = v.strip()

    return cdkey, password



def main():

    try:
        opts, args = getopt(sys.argv[1:], 'k:h', ['help'])
        opts = dict(opts)
    except GetoptError as e:
        sys.exit(str(e) + '\n' + USAGE)

    if '-h' in opts or '--help' in opts:
        sys.exit(USAGE)

    if '-k' in opts:
        cdkey, password = parse_key_file(opts['-k'])
        emay = EmaySMS(cdkey, password)
    else:
        sys.exit('Require key file "-k". ')

    if len(args) < 1:
        sys.exit(USAGE)

    action  = args[0].lower()
    args    = args[1:]

    if action == 'send':
        if len(args) < 1:
            sys.exit(USAGE)

        numbers = args
        message = sys.stdin.read()
        emay.send(numbers, message)

    elif action == 'sent':
        print emay.sent

    elif action == 'balance': 
        print emay.balance

    elif action == 'recharge':

        card_number     = args[0]
        card_password   = args[1]
        emay.recharge(card_number, card_password)

    elif action == 'changepassword':

        new_password = args[0]
        emay.change_password(new_password)

    else:
        sys.exit('Unknonw action {0}'.format(action))



if __name__ == "__main__" : 
    main()
