EmaySMS.py
==========

Python client for Emay.cn SMS service using HTTP SDK. Visit [Emay downloading center](http://www.emay.cn/down.htm) for more information about the SDK. 

Current SDK version: 4.1.0




Python Usage
------------


Intialization:

    >>> from emaysms import EmaySMS, EmaySMSException
    >>> cdkey = 'AAAA-BBB-CCCC-DDDDD'
    >>> password = '123456'
    >>> emay = EmaySMS(cdkey, password)


Register the current key to activate it:

    >>> emay.register()


De-register the currrent key to disable it:

    >>> emay.deregister()


Send an instant SMS:

    >>> emay.send(['PHONE NUMBER 1', 'PHONE NUMBER 2', ...], 'SMS CONTENT')


Send a timed SMS:

    >>> emay.send(['PHONE NUMBER 1', 'PHONE NUMBER 2', ...], 'SMS CONTENT', 'YYYYMMDDHHMMSS')


Query account balance in RMB

    >>> emay.balance
    2016.8


Recharge current account using a prepaid card:

    >>> emay.recharge('CARD NUMBER', 'CARD PASSWORD')


Change password for the current cdkey

    >>> emay.change_password('NEW PASSWORD')




Command Line Usage
------------------

`EmaySMS.py` also provides a command line interface. Here is its help message: 




    Example
    -------


    Register a key file. A key file must be registered before it can be used:


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

