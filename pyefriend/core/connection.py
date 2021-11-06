import time
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop

from pyefriend.utils.const import System


class Conn:
    """ QAxWidget을 통해 Connection Instance 생성(Low-Level) """
    def __init__(self):
        self.instance = QAxWidget(System.PROGID)
        self._event_loop = None
        self._error = None

    def dynamic_call(self, func_name: str, *args):
        return self.instance.dynamicCall(func_name, *args)

    def clear_event_loop(self):
        if self._event_loop is not None:
            self._event_loop.exit()
            self._event_loop = None
        return self

    def execute_event_loop(self):
        # delay 추가
        time.sleep(0.01)

        if self._error is not None:
            # event loop 내에서 에러 생겼을 경우 error 받아옴
            raise self._error
        
        self._event_loop = QEventLoop()  # 이벤트루프 할당
        self._event_loop.exec_()  # 이벤트루프 실행
        return self

    def _set_event_handler(self, event, handler):
        """이벤트 핸들러 등록 관련함수의 코드 중복을 제거하기 위한 함수"""

        # 데코레이터
        def decorated_handler():
            try:
                handler()
            except Exception as e:
                self._error = e
            self.clear_event_loop()

        event.connect(decorated_handler)  # handler 연결

    def set_receive_error_data_handler(self, handler):
        """ ReceiveErrorData 이벤트에 대한 핸들러를 등록한다 """
        self._set_event_handler(self.instance.ReceiveErrorData, handler)

    def set_receive_data_event_handler(self, handler):
        """ReceiveData 이벤트에 대한 핸들러를 등록한다
        ReceiveData 이벤트: 사용자가 요청한 조회 데이터를 받았을 때 발생되는 이벤트
        """
        self._set_event_handler(self.instance.ReceiveData, handler)

    # Wrapper
    def SetSingleData(self, field_index: int, value: str) -> str:
        """ 사용자가 요청할 서비스의 Input 이 단건(Single 형) 데이터 값일 때 사용하는 공통함수 """
        return self.dynamic_call('SetSingleData(int, QString)', field_index, value)

    def SetSingleDataEx(self, block_index: int, field_index: int, value: str) -> str:
        """ 사용자가 요청할 서비스의 Input 이 다건 데이터 값일 때 사용하는 공통함수 """
        return self.dynamic_call('SetSingleDataEx(int, int, QString)', block_index, field_index, value)

    def SetMultiData(self, record_index: int, field_index: int, value: str) -> str:
        """ 사용자가 요청할 서비스의 Input 이 다건(Multi 형) 데이터 값일 때 사용하는 공통함수 """
        return self.dynamic_call('SetMultiData(int, int, QString)', record_index, field_index, value)

    def GetSingleFieldCount(self) -> int:
        """
        요청한 데이터를 ReceiveData에서 받았을 때Output 블록이 단건 일 경우 필드 개수를 가져오는 공통함수(편의성을 위해 제공함)

        :return ReceiveData로 수신된 단건 Output 필드 개수
        """
        return self.dynamic_call("GetSingleFieldCount()")

    def GetMultiBlockCount(self) -> int:
        """
        요청한 데이터를 ReceiveData에서 받았을 때Output 블록에 Multi 블록이 하나 이상일 경우 블록 개수를 반환하는 공통함수
        서비스의 Multi(다건) 블록이 여러 개 일 경우 사용함(보통은 하나이므로 예외적인 케이스에만 사용함)
        """
        return self.dynamic_call("GetMultiBlockCount()")

    def GetMultiRecordCount(self, block_index: int) -> int:
        """
        요청한 데이터를 ReceiveData에서 받았을 때 멀티 블록 레코드(Row) 개수를 반환하는 공통함수
        해당 서비스의 Output 블록이 Multi일 때 레코드 개수(Occurs Count)를 반환합니다.
        """
        return self.dynamic_call("GetMultiRecordCount(int)", block_index)

    def GetMultiFieldCount(self, block_index: int, record_index: int) -> int:
        """
        요청한 데이터를 ReceiveData에서 받았을 때 멀티 블록의 Field 개수를 얻을 때 사용하는 공통함수(편의성을 위해 제공함)

        :return 선택한 멀티 블록 레코드의 필드 개수
        """
        return self.dynamic_call("GetMultiFieldCount(int, int)", block_index, record_index)

    def GetSingleData(self, field_index: int, attribute_type: int) -> str:
        """
        요청한 데이터를 ReceiveData, ReceiveRealData에서 받았을 때 단건 데이터 필드 값을 얻을 때 사용하는 공통함수(단건 조회 및 실시간 데이터 값을 얻을 때 사용함)
        ReceiveData, ReceiveRealData 이벤트 발생시 인덱스 값과 속성 구분을 설정하여 수신된 서비스의 데이터 값과 속성 값을 받습니다.
        데이터의 형태는 모두 스트링 형태이므로 사용자가 데이터를 가공해서 사용할 때는 원하는 타입에 맞춰서 casting을 해서 사용해야 합니다.

        :param field_index: 수신된 필드의 Index 값.
        :param attribute_type: 얻고자 하는 데이터 타입을 입력(0: 데이터값, 1: 속성값)
        :return 수신된 서비스의 데이터 값과 속성 값
        """
        return self.dynamic_call("GetSingleData(int, int)", field_index, attribute_type)

    def GetSingleDataEx(self, block_index: int, field_index: int, attribute_type: int) -> str:
        """
        요청한 데이터를 ReceiveData, ReceiveRealData에서 받았을 때 다건 데이터 필드 값을 얻을 때 사용하는 공통함수
        (* 공식 메뉴얼에 자세한 설명이 없으나, GetSingleData과 blockIndex 이외에는 GetSingleData와 동일한 것으로 보임)
        """
        return self.dynamic_call("GetSingleDataEx(int, int, int)", block_index, field_index, attribute_type)

    def GetMultiData(self, block_index: int, record_index: int, field_index: int, attribute_type: int = 0) -> str:
        """
        요청한 데이터를 ReceiveData에서 받았을 때 멀티 데이터 필드 값을 얻는데 사용하는 공통함수
        해당 서비스가 멀티 블록일 경우 사용자가 원하는 데이터 필드 값을 설정하여 수신된 데이터 또는 속성값을 받을 때 사용합니다.
        데이터의 형태는 모두 스트링 형태이므로 사용자가 데이터를 가공해서 사용할 때는 원하는 타입에 맞춰서 casting을 해서 사용해야 합니다.
        다건 조회 데이터를 얻을 때만 사용되는 함수입니다.(실시간 데이터에서는 사용되지 않음)

        :param block_index: 멀티 블록의 인덱스.(보통 Multi Block이 하나이므로 0으로 셋팅함)
        :param record_index: 해당 멀티 블록의 레코드 인덱스
        :param field_index: 수신된 필드의 Index 값.
        :param attribute_type: 해당 인덱스의 속성 값(0: 데이터값, 1: 속성값)
        :return 선택한 인덱스의 데이터 값을 반환합니다.
        """
        return self.dynamic_call("GetMultiData(int, int, int, int)",
                                         block_index, record_index, field_index, attribute_type)

    def GetReqMsgCode(self) -> str:
        """
        요청한 데이터를 ReceiveData, ReceiveErrorData에서 받았을 때 요청한 서비스의 메시지 코드 정보를 받는데 사용하는 공통함수
        요청한 서비스의 메시지 코드 값을 반환합니다. 요청 서비스가 정상적으로 처리됐는지 기타 에러 처리시에 사용합니다.

        :return 선택한 인덱스의 데이터 값을 반환합니다.
        """
        return self.dynamic_call("GetReqMsgCode()")

    def GetRtCode(self) -> str:
        """
        요청한 데이터를 ReceiveErrorData에서 받았을 때 요청한 서비스의 메시지 코드 정보를 받는데 사용하는 공통함수
        요청한 서비스의 메시지 코드 값을 반환합니다. 요청 서비스가 정상적으로 처리됐는지 기타 에러 처리시에 사용합니다.

        :return 서버에서 수신된 서비스의 메시지 코드 값을 반환합니다.
        """
        return self.dynamic_call("GetRtCode()")

    def GetReqMessage(self) -> str:
        """
        요청한 데이터를 ReceiveData, ReceiveErrorData에서 받았을 때 요청한 서비스의 메시지 정보를 받는 공통함수
        요청한 서비스의 응답 메시지를 반환합니다 응답 메시지를 통해 잘못된 정보를 확인할 수 있습니다.

        :return 서버에서 수신된 서비스의 통신 메시지를 받습니다.
        """
        return self.dynamic_call("GetReqMessage()")

    def RequestData(self, service: str):
        """
        사용자가 SetSingleData , SetMultiData로 넣은 Input 정보를 가지고 해당 서비스의 조회를 요청하는 공통함수
        사용자가 사용할 서비스 명을 설정하고 데이터를 요청한다.

        :param service: 요청할 서비스명
        """
        # transaction
        time.sleep(0.1)

        # call
        self.dynamic_call("RequestData(QString)", service)

        # clear and execute
        return (
            self.clear_event_loop()
                .execute_event_loop()
        )

    def RequestNextData(self, service: str):
        """
        RequestData 를 호출해서 받은 데이터의 다음 데이터를 요청하는 공통함수
        다음 조회를 요청할 서비스 명을 설정한다. 호출하기 전에 IsMoreNextData 공통함수를 통해서 다음 조회 데이터가 있는지 확인한 후에
        RequestNextData 를 호출한다.

        :param service: 요청할 서비스명
        """
        self.dynamic_call("RequestData(QString)", service)

        # clear and execute
        return (
            self.clear_event_loop()
                .execute_event_loop()
        )

    def RequestRealData(self, query: str, code: str):
        raise NotImplementedError('Not yet')

    def UnRequestRealData(self, query: str, code: str):
        raise NotImplementedError('Not yet')

    def UnRequestAllRealData(self):
        raise NotImplementedError('Not yet')

    def SetMultiBlockData(self, block_index: int, record_index: int, field_index: int, value: str) -> bool:
        """
        멀티 블록이 여러 개 일 경우 Input 데이터를 설정하는 공통함수
        멀티 블록 서비스인 경우 Input 항목에 데이터를 설정할 때 사용한다.
        SetsingleData와 SetMultiData는 하나의 블록 기준이지만 여러 개의 멀티 블록이 사용되는 서비스가 추후에 만들어질 경우를 대비해서 만들어 놓은 함수이다.

        :return 0(FALSE) 이면 실패, 1(TRUE) 이면 성공
        """
        result = self.dynamic_call("SetMultiBlockData(int, int, int, QString)",
                                           block_index, record_index, field_index, value)
        print(result, type(result))

        return result == '1'

    def IsMoreNextData(self) -> str:
        """
        요청한 데이터의 ReceiveData 이벤트 발생 후에 다음 조회 데이터가 있는지 확인하는 공통함수

        :return: 다음 조회가 있으면 TRUE 를 반환, 없으면 FALSE 반환
        """
        return self.dynamic_call("IsMoreNextData()")

    def GetAccountCount(self) -> int:
        """
        로그인한 사용자 계좌 개수를 반환하는 공통함수
        사용자 프로그램 시작시 계좌 리스트 정보를 가져올 때 사용하며 로그인한 사용자의 개설된 계좌 개수를 반환합니다.

        :return 계좌 개수를 반환
        """
        return self.dynamic_call("GetAccountCount()")

    def GetAccount(self, account_index: int) -> str:
        """
        인덱스 별 사용자 계좌를 가져오는 공통함수
        사용자 프로그램 시작시 계좌 리스트 정보를 가져올 때 사용하며 인덱스 별 사용자 계좌를 반환합니다.

        :param account_index: 계좌의 인덱스 값.
        :return 계좌 번호 반환 (단, 이때 총 10자리를 반환하며, 앞의 8자리는 종합계좌 번호 뒤의 2자리는 상품계좌 번호이다.)
        """
        return self.dynamic_call("GetAccount(int)", account_index)

    def GetEncryptPassword(self, raw_password) -> str:
        """
        암호화 처리된 비밀번호를 반환합니다.
        매수/매도/정정/취소 주문 서비스 요청시 필요한 암호화 된 비밀번호를 반환하는데 사용합니다.
        이 함수를 사용하지 않고 암호화 되지 않은 비밀번호를 서버에 올릴 경우 정상적으로 주문이 처리되지 않습니다.

        :param raw_password: 암호화 안 된 비밀번호
        :return 암호화 처리된 비밀번호
        """
        return self.dynamic_call("GetEncryptPassword(QString)", raw_password)

    def GetOverSeasStockSise(self) -> str:
        """
        해외주식 이용시 사용자 권한 정보를 가져오는 함수
        해외주식 이용 사용자 권한 정보를 반환합니다. 해외주식 이용신청시 신청자에 대한 암호값이 반환되며 미신청이용자의 경우 지연시세를 이용할 수 있는 값이 반환됩니다.

        :return 해외주식 이용 사용자 권한 정보
        """
        return self.dynamic_call("GetOverSeasStockSise()")

    def GetSingleDataStockMaster(self, product_code: str, field_index: int) -> str:
        """
        국내(KOSPI, KOSDAQ) 주식 종목의 정보를 가져오는 함수

        :return: 입력한 종목코드(vStkCode)의 nFieldIdx 번째 항목 종목 정보
        """
        return self.dynamic_call("GetSingleDataStockMaster(QString, int)", product_code, field_index)

    def IsVTS(self) -> bool:
        """
        모의투자 접속 여부 확인

        :return: 모의투자 접속 여부 (TRUE : 모의투자 접속, FALSE : 운영 접속)
        """
        return self.dynamic_call("IsVTS()")


