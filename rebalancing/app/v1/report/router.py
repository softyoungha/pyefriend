import os
from typing import Optional, List
from fastapi import APIRouter, Request, Response, status, HTTPException, Depends
from fastapi.responses import FileResponse

from pyefriend.exceptions import NotConnectedException, AccountNotExistsException
from rebalancing.utils.const import How
from rebalancing.models.report import Status, Report
from rebalancing.app.auth import login_required
from .schema import ReportInput, ReportOutput, CreateReportOutput, PricesOutput, ExecuteReportOutput


r = APIRouter(prefix='/report',
              tags=['report'])


@r.post('/', response_model=CreateReportOutput)
async def create_report(request: ReportInput, user=Depends(login_required)):
    """### pyefriend api 생성로 접속 테스트 후 성공시 report_name 생성 """
    try:
        context = request.dict()

        # set report
        report: Report = Report(**context, prompt=False)

        # create api
        api = report.api

        # get context
        context.update(account=api.account,
                       is_vts=api.controller.IsVTS(),
                       created_time=report.created_time,
                       report_name=report.report_name)

        # create report
        report.save(delete_if_exists=True)

        return context

    except NotConnectedException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    except AccountNotExistsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'{e.__class__.__name__}: \n{str(e)}')


@r.post('/{report_name}/prices', response_model=ReportOutput)
async def refresh_prices(report_name: str,
                         created_time: Optional[str] = None,
                         user=Depends(login_required)):
    """
    ### DB 내 종목 가격 최신화('product' table)
    - report_name: ~/report/ POST를 통해 생성된 리포트
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    """
    report: Report = Report.get(report_name=report_name, created_time=created_time)
    report.refresh_prices()
    return {
        'report_name': report.report_name,
        'created_time': report.created_time
    }


@r.get('/{report_name}/prices', response_model=List[PricesOutput])
async def get_prices(report_name: str,
                     created_time: Optional[str] = None,
                     user=Depends(login_required)):
    """
    ### DB 내 종목 가격 조회('product' table)
    - report_name: ~/report/ POST를 통해 생성된 리포트
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    """
    report: Report = Report.get(report_name=report_name, created_time=created_time)
    return report.get_prices()


@r.post('/{report_name}/plan', response_model=ReportOutput)
async def make_plan(report_name: str,
                    created_time: Optional[str] = None,
                    overall: bool = False,
                    user=Depends(login_required)):
    """
    ### 최신화된 가격을 토대로 리밸런싱 플랜 생성
    - report_name: ~/report/ POST를 통해 생성된 리포트
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    - overall: 국내/해외 잔고 모두 계산할지 여부. 모의투자에서는 True 설정 불가능(default=False)
    """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time)
    report.make_plan(overall=overall)
    return {
        'report_name': report.report_name,
        'created_time': report.created_time
    }


@r.get('/{report_name}/plan', response_class=FileResponse)
async def get_plan(report_name: str,
                   created_time: Optional[str] = None,
                   summary: Optional[bool] = False,
                   user=Depends(login_required)):
    """
    ### 리밸런싱 플랜 조회
    - report_name: ~/report/ POST를 통해 생성된 리포트
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    - summary: True일 경우 요약정보, False일 경우 상세정보
    """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time,
                                statuses=[Status.PLANNING, Status.EXECUTED])

    if summary:
        path = report.summary_path
    else:
        path = report.plan_path

    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    response = FileResponse(path,
                            media_type='text/csv',
                            filename=report.name)
    return response


@r.put('/{report_name}/plan', response_model=ReportOutput)
async def adjust_plan(report_name: str,
                      created_time: Optional[str] = None,
                      user=Depends(login_required)):
    """
    ### 최신화된 가격을 토대로 리밸런싱 플랜 생성
    - report_name: ~/report/ POST를 통해 생성된 리포트
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    """

    report: Report = Report.get(report_name=report_name,
                                created_time=created_time,
                                statuses=[Status.PLANNING, Status.EXECUTED])
    report.adjust_plan()

    return {
        'report_name': report.report_name,
        'created_time': report.created_time
    }


@r.post('/{report_name}/execute', response_model=List[ExecuteReportOutput])
async def execute_plan(report_name: str,
                       created_time: Optional[str] = None,
                       how: How = How.MARKET,
                       n_diff: int = 3,
                       user=Depends(login_required)):
    """
    ### 리밸런싱 플랜 실행
    - report_name: ~/report/ POST를 통해 생성된 리포트
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time,
                                statuses=[Status.PLANNING, Status.EXECUTED])

    return report.execute_plan(how=how, n_diff=n_diff)


@r.post('/{report_name}/execute', response_model=List[ExecuteReportOutput])
async def get_order_status(report_name: str,
                           created_time: Optional[str] = None,
                           user=Depends(login_required)):
    """
    ### 리밸런싱 체결 상황 조회
    - report_name: ~/report/ POST를 통해 생성된 리포트
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time,
                                statuses=[Status.EXECUTED])

    return report.get_order_status()

