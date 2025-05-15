import sys
from networksecurity.logging import logger


class NetworkSecurityException(Exception):
    def __init__(self, error_message,error_details:sys):
        self.error_message=error_message ## get the error message 
        _,_,exc_tb=error_details.exc_info() ## error info details 

        self.lineno=exc_tb.tb_lineno ## the line no
        self.file_name=exc_tb.tb_frame.f_code.co_filename ## the file name

    def __str__(self):
        return f"Error occured in python script name [{self.file_name}] line number [{self.lineno}] error message [{str(self.error_message)}]"

if __name__=='__main__':
    try:
        logger.logging.info("enter the try block")## logs get in exception.py coz it is executed in exception.py terminal
        a=1/0
        print("this would not be printed",a)
    except Exception as e:
        raise NetworkSecurityException(e,sys)


        