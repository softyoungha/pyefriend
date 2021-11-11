# -*- coding:utf-8 -*-
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Optional
from getpass import getpass


def argument_parser() -> ArgumentParser:
    from rebalancing.utils.const import Target

    description = 'Re-balancing 모듈 실행'
    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--target', '-t',
                        type=str,
                        help='domestic: 국내 투자 선택\n'
                             'overseas: 해외 투자 선택',
                        choices=[Target.DOMESTIC, Target.OVERSEAS],
                        required=True)
    parser.add_argument('--created', '-c',
                        type=str,
                        help="Report 생성이력(YYYYmmdd_HH_MM_SS format)",
                        default=None)
    parser.add_argument('--test',
                        action="store_true",
                        help="테스트 계정 사용여부")
    parser.add_argument('--account', '-a',
                        type=str,
                        help="계좌명('-' 제외), 입력하지 않을 경우 config.yml에서 사용",
                        default=None)
    parser.add_argument('--password', '-p',
                        action="store_true",
                        help="계좌 매수/매도시 입력 비밀번호\n"
                             "입력하지 않을 경우 config.yml에서 사용\n"
                             "-p/--password 입력 후 별도로 입력")
    parser.add_argument('--skip-refresh', '-s',
                        action="store_true",
                        help="입력시 종목 최신화 skip")

    return parser


def main():
    # get parser
    parser = argument_parser()

    # parse
    parsed_args = parser.parse_args()

    # set
    target: str = parsed_args.target
    created_time: Optional[str] = parsed_args.created_time
    account: Optional[str] = parsed_args.account
    test: bool = parsed_args.test
    skip: bool = parsed_args.skip_refresh

    if parsed_args.password:
        password: Optional[str] = getpass('Password: ')
    else:
        password = None

    # arg parsing 이후에 import
    from rebalancing.models import Report

    # create executor
    report = Report(target=target,
                    account=account,
                    password=password,
                    created_time=created_time,
                    prompt=False,
                    test=test)

    # refresh
    if skip:
        report.logger.info('종목 최신화를 Skip합니다.')

    else:
        report.refresh_prices()

    # plan
    report.make_plan()

    msg = f"\n저장된 결과를 보고 리밸런싱을 진행할지 여부를 결정합니다." \
          f"\nY 또는 1을 입력할 경우 리밸런싱 대상 종목에 대한 매수/매도가 진행됩니다." \
          f"\n그외의 값을 입력할 경우 프로그램이 종료됩니다." \
          f"\n- report_name: '{report.account}'" \
          f"\n- 생성시간: '{report.created_time}'"
    print(msg)

    answer = input("Input(Y or N): ")

    if answer.lower() in ('y', '1'):
        report.execute_plan()
    else:
        exit()


if __name__ == "__main__":
    main()
